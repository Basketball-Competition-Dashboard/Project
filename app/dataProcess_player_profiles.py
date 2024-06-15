import sqlite3
import random

DATABASE_PATH = f'{__file__}/../../data/nbaDB.db'

def post_player_profiles(player_profile):
    try:
      query = "SELECT * FROM players WHERE name = ?"
      params = [player_profile['name']]

      if player_profile.get('birthdate'):
          query += " AND birthdate = ?"
          params.append(player_profile['birthdate'])
      if player_profile.get('country'):
          query += " AND country = ?"
          params.append(player_profile['country'])
      if player_profile.get('height'):
          query += " AND height = ?"
          params.append(player_profile['height'])
      if player_profile.get('position'):
          query += " AND position = ?"
          params.append(player_profile['position'])
      if player_profile.get('team_name'):
          query += " AND team_name = ?"
          params.append(player_profile['team_name'])
      if player_profile.get('weight'):
          query += " AND weight = ?"
          params.append(player_profile['weight'])
      connection = sqlite3.connect(DATABASE_PATH)
      # cursor = connection.cursor()
      # cursor.execute(query, params)
      # result = cursor.fetchall()
      connection.close()
      response_data = {
        "birthdate": "1970-05-25",
        "country": "Nigeria",
        "height": "6-8",
        "id": 3695,
        "name": "Precious Achiuwa",
        "team_name": "Knicks",
        "weight": 243
      }
      return response_data , 201
    except Exception:
        return {"message": "Sorry, an unexpected error has occurred."}, 500

def get_player_profiles(page_length, page_offset, sort_field, sort_order):
    
    sort_order_sql = 'ASC' if sort_order == 'ascending' else 'DESC'
    
    query = f""
    
    connection = sqlite3.connect(DATABASE_PATH)
    # cursor = connection.cursor()
    # cursor.execute(query, params)
    # result = cursor.fetchall()
    connection.close()
    response_data = []
    # for row in result:
    #     response_data.append({
    
    return response_data, 201
  
def delete_player_profiles(id):
  connection = sqlite3.connect(DATABASE_PATH)
  # cursor = connection.cursor()
  # cursor.execute(query, params)
  # result = cursor.fetchall()
  connection.close()
  response_data = []
  return response_data, 201

def patch_player_profiles(id, player_profile):
  try:
    query = "SELECT * FROM players WHERE name = ?"
    params = [player_profile['name']]

    if player_profile.get('birthdate'):
        query += " AND birthdate = ?"
        params.append(player_profile['birthdate'])
    if player_profile.get('country'):
        query += " AND country = ?"
        params.append(player_profile['country'])
    if player_profile.get('height'):
        query += " AND height = ?"
        params.append(player_profile['height'])
    if player_profile.get('position'):
        query += " AND position = ?"
        params.append(player_profile['position'])
    if player_profile.get('team_name'):
        query += " AND team_name = ?"
        params.append(player_profile['team_name'])
    if player_profile.get('weight'):
        query += " AND weight = ?"
        params.append(player_profile['weight'])
    connection = sqlite3.connect(DATABASE_PATH)
    # cursor = connection.cursor()
    # cursor.execute(query, params)
    # result = cursor.fetchall()
    connection.close()
  except Exception:
      return {"message": "Sorry, an unexpected error has occurred."}, 500
  return '', 204