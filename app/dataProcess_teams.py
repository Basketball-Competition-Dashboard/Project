from flask import jsonify
import sqlite3

DATABASE_PATH = f'{__file__}/../../data/nbaDB.db'

def create_teams_status(data):
    try:
        data_dict = dict(data)
        data = data_dict
        
        NameAbbr = data.get('abbr')
        City = data.get('city')
        Nickname = data.get('name')
        YearFounded = data.get('year_founded')
        CoachName = data.get('coach')

        conn = sqlite3.connect(DATABASE_PATH, isolation_level='IMMEDIATE')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Team (Nickname, City, NameAbbr, CoachName, YearFounded) VALUES (?, ?, ?, ?, ?)",(Nickname, City, NameAbbr, CoachName, YearFounded))
        team_id = cursor.lastrowid
       
        sql = """
            SELECT 
                t.Nickname AS team,
                t.City AS city,
                t.NameAbbr AS abbr,
                t.CoachName AS coach,
                t.YearFounded AS year_founded
            FROM 
                Team AS t
            WHERE
                t.TID = ?
        """
        cursor.execute(sql,(team_id,))
        conn.commit()

        cols = [col[0] for col in cursor.description]
        response = []
        for row in cursor.fetchall():
            response.append(dict(zip(cols, row)))
        conn.close() 
        response = response[0]
        
        return response,201

    except sqlite3.Error as e:
        print("SQLite error:", e.args[0])
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500
    except Exception as e:
        print("General error:", str(e))
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500
            

def update_teams_status(id,data):
    try:
        coach = data["coach"]
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("UPDATE Team SET CoachName = ? WHERE TID =? ", (coach,id))
        conn.commit()
        conn.close()
        return {'message': 'Team status updated'}, 201

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return {'error': str(e)}, 500


def get_team(page_length, page_offset, sort_field, sort_order):
    
    try:
      conn = sqlite3.connect(DATABASE_PATH)
      cursor = conn.cursor()
        # 構建排序字段和順序
    #   sort_column = 'FName || " " || LName' if sort_field == 'name' else 'BDate'
      order_direction = 'ASC' if sort_order == 'ascending' else 'DESC'

      # 構建SQL查詢語句
      sql = f"""
        SELECT 
           NameAbbr as abbr, City as city, CoachName as coach, tid as id, NickName as name, YearFounded as year_founded
           from Team
           ORDER BY {sort_field} {order_direction}
           LIMIT {page_length} OFFSET {page_offset}

      """
      cursor.execute(sql)
      rows = cursor.fetchall()
      conn.close()
    #   print(rows[0][0])

    #   print(rows)
      values = [{
            "abbr": row[0],
            "city": row[1],
            "coach": row[2],
            "id": row[3],
            "name": row[4],
            "year_founded": row[5]
        } for row in rows]
      
      response_data = values

      return response_data, 200
    
    except Exception:
        return {"message": "Sorry, an unexpected error has occurred."}, 500