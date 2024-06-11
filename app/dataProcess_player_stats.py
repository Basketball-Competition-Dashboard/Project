import sqlite3

def fetch_player_stats(length, offset, sort_field, sort_order):
   try:
      conn = sqlite3.connect('data/nbaDB.db')
      cursor = conn.cursor()
        # 構建排序字段和順序
    #   sort_column = 'FName || " " || LName' if sort_field == 'name' else 'BDate'
      order_direction = 'ASC' if sort_order == 'ascending' else 'DESC'

      # 構建SQL查詢語句
      sql = f"""
        SELECT 
            p.PID as id,
            p.Fname || ' ' || p.Lname AS name,
            gr.GID as game_id,
            strftime('%Y-%m-%d', g.Date) as game_date,
            away_team.NameAbbr as game_away_abbr,
            home_team.NameAbbr as game_home_abbr,
            gr.Assist as assist,
            gr.Hit as hit,
            gr.Steal,
            gr.Rebound as rebound,
            gr.FreeThrow as free_throw,
            gr.Score

        FROM 
            Game AS g
        JOIN 
            GameRecord AS gr ON g.GID = gr.GID
        JOIN 
            Player AS p ON gr.PID = p.PID
        JOIN 
            Attend AS home_attend ON g.GID = home_attend.GID AND home_attend.is_home_team = 1
        JOIN 
            Attend AS away_attend ON g.GID = away_attend.GID AND away_attend.is_home_team = 0
        JOIN 
            Team AS home_team ON home_attend.TID = home_team.TID
        JOIN 
            Team AS away_team ON away_attend.TID = away_team.TID

        ORDER BY {sort_field} {order_direction}
        LIMIT {length} OFFSET {offset}

      """
      cursor.execute(sql)
      rows = cursor.fetchall()
      conn.close()
      print(rows[0][0])


      values = [{
            "id": row[0],
            "name": row[1],
            "game_id": row[2],
            "game_date": row[3],
            "game_away_abbr": row[4],
            "game_home_abbr": row[5],
            "assist": row[6],
            "hit": row[7],
            "steal": row[8],
            "rebound": row[9],
            "free_throw": row[10],
            "score": row[11]
        } for row in rows]
      
      response_data = values

      return response_data, 200
   except Exception:
        return {"message": "Sorry, an unexpected error has occurred."}, 500



def create_player_stats(name, game_date, game_home_abbr, game_away_abbr, assist, hit, steal, rebound, free_throw, score):
    try:
        conn = sqlite3.connect('data/nbaDB.db')
        cursor = conn.cursor()

        # print(name)
        lname, fname = name.split()
        # print(lname, fname)

        cursor.execute("SELECT PID FROM Player WHERE Fname = ? AND Lname = ?", (fname, lname))
        player = cursor.fetchone()

        sql = """
            SELECT g.GID
            FROM Game g
            JOIN Attend as home_attend ON g.GID = home_attend.GID
            JOIN Attend as away_attend ON g.GID = away_attend.GID
            JOIN Team as home_team ON home_attend.TID = home_team.TID
            JOIN Team as away_team ON away_attend.TID = away_team.TID
            WHERE strftime('%Y-%m-%d', g.Date) = ? AND home_team.NameAbbr = ? AND away_team.NameAbbr = ? AND home_attend.is_home_team = 1 AND away_attend.is_home_team = 0
        """
        
        cursor.execute(sql, (game_date, game_home_abbr, game_away_abbr))
        game = cursor.fetchone()
        

        if not player or not game:
            conn.close()
            return {"message": "The resource you are accessing is not found."}, 404
        
        # if not game:
        #     conn.close()
        #     return {"message": "The game you are accessing is not found."}, 404

        player_id = player[0]
        #print(f"Player ID: {player_id}")

        game_id = game[0]
        #print(f"Game ID: {game_id}")

        sql_create = f"""
        INSERT INTO "GameRecord" ("PID", "GID", "Assist", "Hit", "Steal", "Rebound", "Score", "FreeThrow")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """ 
        
        cursor.execute(sql_create, (player_id, game_id, assist, hit, steal, rebound, score, free_throw))
        conn.commit()

        conn.close()
        
        values = {
            "id": player_id,
            "game_id": game_id,
            "name": name,
            "game_date": game_date,
            "game_away_abbr": game_away_abbr,
            "game_home_abbr": game_home_abbr,
            "assist": assist,
            "hit": hit,
            "steal": steal,
            "rebound": rebound,
            "free_throw": free_throw,
            "score": score
        }
        
        response_data = values

        return response_data, 201
    
    except Exception as e:
        return {"message": "Sorry, an unexpected error has occurred."}, 500


def update_player_stats(id, gid, update_fields):

    try:
        conn = sqlite3.connect('data/nbaDB.db')
        cursor = conn.cursor()

        # Check if the record exists
        cursor.execute("SELECT * FROM GameRecord WHERE PID = ? AND GID = ?", (id, gid))
        record = cursor.fetchone()

        if not record:
            conn.close()
            return {"message": "The resource you are accessing is not found."}, 404

        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values()) + [id, gid]

        # print("set_clause: ",set_clause)
        # print("values: ", values)

        sql_update = f"UPDATE GameRecord SET {set_clause} WHERE PID = ? AND GID = ?"
        
        cursor.execute(sql_update, values)
        conn.commit()
        conn.close()

        return {"message": "Updated!"}, 204

    except Exception as e:
        return {"message": "Sorry, an unexpected error has occurred."}, 500


def delete_player_stats(id, game_id):

    try:
        conn = sqlite3.connect('data/nbaDB.db')
        cursor = conn.cursor()

        
        cursor.execute("SELECT * FROM GameRecord WHERE PID = ? AND GID = ?", (id, game_id))
        record = cursor.fetchone()

        if not record:
            conn.close()
            return {"message": "The resource you are accessing is not found."}, 404


        cursor.execute("DELETE FROM GameRecord WHERE PID = ? AND GID = ?", (id, game_id))
        conn.commit()
        conn.close()
        
        return {"message": "Deleted!"}, 204

    except Exception as e:
        return {"message": "Sorry, an unexpected error has occurred."}, 500
