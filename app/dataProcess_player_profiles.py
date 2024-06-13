import sqlite3
import random

DATABASE_PATH = f'{__file__}/../../data/nbaDB.db'

def fetch_player_profiles(length, offset, sort_field, sort_order):
    try:
      conn = sqlite3.connect(DATABASE_PATH)
      cursor = conn.cursor()
        # 構建排序字段和順序
      sort_column = 'FName || " " || LName' if sort_field == 'name' else 'BDate'
      order_direction = 'ASC' if sort_order == 'ascending' else 'DESC'

      # 構建SQL查詢語句
      sql = """
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
          ORDER BY ? ?
          LIMIT ? OFFSET ?
      """
      cursor.execute(sql, (sort_column, order_direction, length, offset))
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
      response_data = values

      return response_data, 200
    except Exception:
        return {"message": "Your request is invalid.!"}, 400

def player_profiles_put_stub():
  state1 = random.choice([1, 2, 3, 4])
  if state1 == 1:
    return "Created",200
  elif state1 == 2:
    return "Updated", 204
  elif state1 == 3:
    return {"message": "Your request is invalid."}, 400
  else:
    return {"message": "You are not authorized to access this resource."}, 401
  


def player_profiles_delete_stub(id):
  if id == 1:
    return "Deleted", 204
  elif id == 2:
    return {"message": "Your request is invalid."}, 400
  elif id == 3:
    return {"message": "You are not authorized to access this resource."}, 401
  else:
    return {"message": "You are not authorized to access this resource."}, 404