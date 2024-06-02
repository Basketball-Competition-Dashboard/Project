import sqlite3
def fetch_player_profiles(length, offset, sort_field, sort_order):
    try:
      conn = sqlite3.connect('data/nbaDB.db')
      cursor = conn.cursor()
        # 構建排序字段和順序
      sort_column = 'FName || " " || LName' if sort_field == 'name' else 'BDate'
      order_direction = 'ASC' if sort_order == 'ascending' else 'DESC'

      # 構建SQL查詢語句
      sql = f"""
          SELECT
              Player.BDate AS birthdate,
              Player.Country AS country,
              Player.Height AS height,
              Player.PID AS id,
              Player.FName || ' ' || Player.LName AS name,
              Player.Position AS position,
              Team.TName AS team_name,
              Player.Weight AS weight
          FROM Player
          JOIN Team ON Player.TID = Team.TID
          ORDER BY {sort_column} {order_direction}
          LIMIT {length} OFFSET {offset}
      """
      cursor.execute(sql)
      rows = cursor.fetchall()
      conn.close()
      print(rows)
          
      values = [{
          "birthdate": row[0][:10],  # 格式化日期字符串，只取前10個字符
          "country": row[1],
          "height": row[2],
          "id": row[3],
          "name": row[4],
          "position": row[5],
          "team_name": row[6],
          "weight": row[7]
      } for row in rows]
      response_data = {
          "page": {
              "length": length,
              "offset": offset
          },
          "values": values
      }

      return response_data, 200
    except Exception as e:
        return {"message": "Your request is invalid.!"}, 400
