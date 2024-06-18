import sqlite3
import random
import string

DATABASE_PATH = f'{__file__}/../../data/nbaDB.db'
def get_team_id(team_name):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute("SELECT TID FROM Team WHERE TName = ?", (team_name,))
    result = cursor.fetchone()
    connection.close()
    if result:
        return result[0]
    return None
def post_player_profiles(player_profile):
    name_parts = player_profile['name'].split()
    if len(name_parts) == 1:
        fname = name_parts[0]
        lname = ""
    else:
        fname = name_parts[0]
        lname = " ".join(name_parts[1:])
    team_name = player_profile.get('team_name')
    tid = get_team_id(team_name) if team_name else None
    pid = ''.join(random.choices(string.digits, k=5))

    columns = ['PID','Fname', 'Lname']
    values = [pid, fname, lname]
    if player_profile.get('birthdate'):
        columns.append('Bdate')
        values.append(player_profile['birthdate'])
    if player_profile.get('height'):
        columns.append('Height')
        values.append(player_profile['height'])
    if player_profile.get('weight'):
        columns.append('Weight')
        values.append(player_profile['weight'])
    if player_profile.get('position'):
        columns.append('Position')
        values.append(player_profile['position'])
    if player_profile.get('country'):
        columns.append('Country')
        values.append(player_profile['country'])
    if tid:
        columns.append('TID')
        values.append(tid)

    columns_str = ', '.join(columns)
    placeholders = ', '.join(['?' for _ in values])
    query = f"INSERT INTO Player ({columns_str}) VALUES ({placeholders})"
    print(columns_str,"_______")
    print(placeholders,"_______")
    print(values,"_______")
    print(query,"_______")

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    
    cursor.execute(query, values)
    connection.commit()
    
    cursor.execute("SELECT PID, Fname, Lname, Bdate, Height, Weight, Position, Country, TID FROM Player WHERE PID = ?", (pid,))
    new_player = cursor.fetchone()
    connection.close()

    if new_player:
        response_data = {
            'PID': new_player[0],
            'Fname': new_player[1],
            'Lname': new_player[2],
            'Bdate': new_player[3],
            'Height': new_player[4],
            'Weight': new_player[5],
            'Position': new_player[6],
            'Country': new_player[7],
            'TID': new_player[8]
        }
    return response_data , 201

def get_player_profiles(page_length, page_offset, sort_field, sort_order):
    
    sort_order_sql = 'ASC' if sort_order == 'ascending' else 'DESC'
    # 構建基本的SQL查詢語句
    base_query = """
    SELECT  p.PID,
        p.Fname,
        p.Lname,
        p.Bdate,
        p.Height,
        p.Weight,
        CASE
            WHEN INSTR(p.Position, '-') > 0 THEN SUBSTR(p.Position, 1, 1) || SUBSTR(p.Position, INSTR(p.Position, '-') + 1, 1)
            ELSE SUBSTR(p.Position, 1, 1)
        END AS Position,
        p.Country,
        t.TName AS team_name
    FROM
        Player p
    JOIN
        Team t ON p.TID = t.TID
    """
    # 添加排序條件
    if sort_field in ['Player', 'Team', 'Position', 'Birthdate', 'Height', 'Weight', 'Country', 'Fname']:
        base_query += f" ORDER BY {sort_field} {sort_order_sql.upper()}"
    else:
        base_query += f" ORDER BY Fname {sort_order_sql.upper()}"
    
    # 添加分頁條件
    base_query += " LIMIT ? OFFSET ?"
    
    # print(base_query)

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    cursor.execute(base_query, (page_length, page_offset))
    results = cursor.fetchall()
    connection.close()
    # print(results)
    response_data = []
    for row in results:
        player_data = {
            'id': row[0],
            'name': f"{row[1]} {row[2]}",
            'birthdate': row[3][0:10],
            'height': row[4],
            'weight': row[5],
            'position': row[6],
            'country': row[7],
            'team_name': row[8]
        }
        response_data.append(player_data)
    print(response_data)
    return response_data, 200
  
def delete_player_profiles(player_id):
  connection = sqlite3.connect(DATABASE_PATH)
  cursor = connection.cursor()

  # 查找球員的 PID
  cursor.execute("SELECT PID FROM Player WHERE PID = ?", (player_id,))
  result = cursor.fetchone()

  if result is None:
      connection.close()
      return {"message": "The resource you are accessing is not found."}, 404

  # 刪除 Player 表中的記錄
  cursor.execute("DELETE FROM Player WHERE PID = ?", (player_id,))
  connection.commit()
  connection.close()

  return "Deleted", 200

def patch_player_profiles(player_id, player_profile):
    
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # 查找球員的 PID
    cursor.execute("SELECT PID FROM Player WHERE PID = ?", (player_id,))
    result = cursor.fetchone()
    if result is None:
        connection.close()
        return {"message": "The resource you are accessing is not found."}, 404
    update_fields = []
    update_values = []
    if player_profile['name'] != None:
        name_parts = player_profile['name'].split()
        if len(name_parts) == 1:
            update_fields.append('Fname = ?')
            update_values.append(name_parts[0])
            update_fields.append('Lname = ?')
            update_values.append('')
        else:
            update_fields.append('Fname = ?')
            update_values.append(name_parts[0])
            update_fields.append('Lname = ?')
            update_values.append(' '.join(name_parts[1:]))
    
    if player_profile['birthdate'] != None:
        update_fields.append('Bdate = ?')
        update_values.append(player_profile['birthdate'])

    if player_profile['country'] != None:
        update_fields.append('Country = ?')
        update_values.append(player_profile['country'])

    if player_profile['height'] != None:
        update_fields.append('Height = ?')
        update_values.append(player_profile['height'])

    if player_profile['weight'] != None:
        update_fields.append('Weight = ?')
        update_values.append(player_profile['weight'])

    if player_profile['position'] != None:
        update_fields.append('Position = ?')
        update_values.append(player_profile['position'])

    if player_profile['team_name'] != None:
        team_id = get_team_id(player_profile['team_name'])
        if team_id:
            update_fields.append('TID = ?')
            update_values.append(team_id)
        else:
            return {"error": "Team not found"}, 404
    update_values.append(player_id)
    update_query = f"UPDATE Player SET {', '.join(update_fields)} WHERE PID = ?"
    # print(update_query)
    # print(update_values)
    # breakpoint()

    cursor.execute(update_query, update_values)
    connection.commit()
    connection.close()
    return "Updated", 204