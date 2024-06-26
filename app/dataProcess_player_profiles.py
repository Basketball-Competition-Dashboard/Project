import sqlite3
import random
import string
from pathlib import Path

DATABASE_PATH = Path(f'{__file__}/../../data/nbaDB.db').resolve()

def get_team_id(team_name):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()
    cursor.execute("SELECT TID FROM Team WHERE NickName = ?", (team_name,))
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
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()
    
    cursor.execute(query, values)
    connection.commit()

    # 取得新插入的球員資料
    query = """
    SELECT
        p.PID AS id,
        p.Fname || ' ' || p.Lname AS name,
        p.Bdate AS birthdate,
        p.Height AS height,
        p.Weight AS weight,
        CASE
            WHEN INSTR(p.Position, '-') > 0 THEN SUBSTR(p.Position, 1, 1) || SUBSTR(p.Position, INSTR(p.Position, '-') + 1, 1)
            ELSE SUBSTR(p.Position, 1, 1)
        END AS position,
        p.Country AS country,
        t.NickName AS team_name
    FROM
        Player p
    JOIN
        Team t ON p.TID = t.TID
    WHERE
        p.PID = ?
    """
    cursor.execute(query, (pid,))
    new_player = cursor.fetchone()
    connection.close()

    if new_player:
        response_data = {
            "id": new_player[0],
            "name": new_player[1],
            "birthdate": new_player[2][0:10] if new_player[2] is not None else None,
            "height": new_player[3],
            "weight": new_player[4],
            "position": new_player[5],
            "country": new_player[6],
            "team_name": new_player[7],
        }
    return response_data , 201

def get_player_profiles(page_length, page_offset, sort_field, sort_order):
    
    sort_order_sql = 'ASC' if sort_order == 'ascending' else 'DESC'
    # 構建基本的SQL查詢語句
    base_query = """
    SELECT
        p.PID AS id,
        p.Fname || ' ' || p.Lname AS name,
        p.Bdate AS birthdate,
        p.Height AS height,
        p.Weight AS weight,
        CASE
            WHEN INSTR(p.Position, '-') > 0 THEN SUBSTR(p.Position, 1, 1) || SUBSTR(p.Position, INSTR(p.Position, '-') + 1, 1)
            ELSE SUBSTR(p.Position, 1, 1)
        END AS position,
        p.Country AS country,
        t.NickName AS team_name
    FROM
        Player p
    JOIN
        Team t ON p.TID = t.TID
    """
    # 添加排序條件
    if sort_field in {'name', 'birthdate', 'height', 'weight', 'position', 'country', 'team_name'}:
        base_query += f" ORDER BY {sort_field} {sort_order_sql.upper()}"
    else:
        base_query += f" ORDER BY name {sort_order_sql.upper()}"
    
    # 添加分頁條件
    base_query += " LIMIT ? OFFSET ?"
    
    # print(base_query)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()
    cursor.execute(base_query, (page_length, page_offset))
    results = cursor.fetchall()
    connection.close()
    # print(results)
    response_data = []
    for row in results:
        player_data = {
            'id': row[0],
            'name': row[1],
            'birthdate': row[2][0:10] if row[2] is not None else None,
            'height': row[3],
            'weight': row[4],
            'position': row[5],
            'country': row[6],
            'team_name': row[7]
        }
        response_data.append(player_data)
    print(response_data)
    return response_data, 200
  
def delete_player_profiles(player_id):
  connection = sqlite3.connect(DATABASE_PATH)
  connection.execute("PRAGMA foreign_keys = ON")
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
    connection.execute("PRAGMA foreign_keys = ON")
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