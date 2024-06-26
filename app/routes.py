from flask import Blueprint, Flask, jsonify, render_template, request, Response,make_response
from flask_cors import CORS
import sqlite3
import uuid
from swagger_ui import api_doc
from app import dataProcess_player_profiles, dataProcess_player_stats, dataProcess_games, dataProcess_teams
from pathlib import Path

DATABASE_PATH = Path(f'{__file__}/../../data/nbaDB.db').resolve()

# __name__ == app.routes
# __name__取得當前模組的名稱，用於定位相對路徑
bp_web_api = Blueprint(
    'Web API',
    __name__,
    url_prefix='/api/web',
)
bp_web_page = Blueprint(
    'Web page',
    __name__,
    url_prefix='/',
    static_url_path='/',
    static_folder='../web/dist',
    template_folder='../web/dist',
)

# record user session_id in session
sessions = {}

@bp_web_api.route('/ping', methods=['GET'])
def ping():
    return jsonify('Pong!')


@bp_web_api.route('/auth/session', methods=['POST'])  
def create_session():
    try:
        data = request.get_json()
        name = data['name']
        credential = data['credential']
    except:
        return jsonify({"message": "Your request is invalid."}), 400

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT Account, Password FROM Manager where Account = ? and Password = ? limit 1;',
        (name, credential),
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"message": "The resource you are accessing is not found."}), 404

    session_id = str(uuid.uuid4().hex)
    sessions[session_id] = name
    response = Response(status=201)
    response.set_cookie('session_id', session_id, httponly=True, max_age=31536000, path='/', samesite='Strict')
    return response

@bp_web_api.route('/auth/session', methods=['DELETE'])  
def delete_session():
    session_id = request.cookies.get('session_id')
    if session_id is None:
        return jsonify({"message": "You are not authorized to access this resource."}), 401
    if session_id in sessions:
        response = Response(status=204)
        del sessions[session_id]
        response.set_cookie('session_id', '', httponly=True, max_age=0, path='/', samesite='Strict')
        return response

    return jsonify({"message": "You are not authorized to access this resource."}), 401


@bp_web_api.route('/game', methods=['POST'])
def POST_games():
    session_id = request.cookies.get('session_id')
    if session_id not in sessions:
        return jsonify({"message": "You are not authorized to access this resource."}), 401

    try:
        data = request.get_json()
        required_fields = ['date', 'away_name', 'home_name']
        optional_fields = ["away_score", "home_score", "is_home_winner"]

        for field in required_fields:
            if field not in data:
                return jsonify({'message': 'Your request is invalid.'}), 400

        home_team_name = data['home_name']
        away_team_name = data['away_name']
        home_team_id, home_team_city = dataProcess_games.get_team_id_and_city(home_team_name)
        away_team_id, _ = dataProcess_games.get_team_id_and_city(away_team_name)
        if home_team_id is None or away_team_id is None:
            return jsonify({'message': 'One or both teams do not exist.'}), 400

        fields = required_fields.copy()
        values = [data[field] for field in required_fields]
        for field in optional_fields:
            if field in data:
                fields.append(field)
                values.append(data[field])

        data = list(zip(fields, values))

        response, status_code = dataProcess_games.create_games_status(data, home_team_city, home_team_id, away_team_id)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({'message': 'Sorry, an unexpected error has occurred.'}), 500
    
@bp_web_api.route('/games', methods=['GET'])
def GET_games():
    try:
        page_offset = int(request.args.get('page_offset', 0))
        page_length = int(request.args.get('page_length', 3))
        sort_field = request.args.get('sort_field', 'name')
        sort_order = request.args.get('sort_order', 'ascending')
        response, status_code = dataProcess_games.fetch_games_details(page_offset,page_length,sort_field,sort_order)
        return jsonify(response),status_code

    except Exception as e:
        return jsonify({'message': 'Sorry, an unexpected error has occurred.'}), 500
    
@bp_web_api.route('/games/<int:id>/teams/<int:team_id>', methods=['PATCH'])
def PATCH_games(id, team_id):
    session_id = request.cookies.get('session_id')
    if session_id not in sessions:
        return jsonify({"message": "You are not authorized to access this resource."}), 401

    try:
        data = request.json
        response, status_code = dataProcess_games.update_games_status(id, team_id, data)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({'message': 'Sorry, an unexpected error has occurred.'}), 500


@bp_web_api.route('/team', methods=['POST'])
def POST_teams():
    session_id = request.cookies.get('session_id')
    if session_id not in sessions:
        return jsonify({"message": "You are not authorized to access this resource."}), 401

    try:
        data = request.get_json()
        required_fields = ['abbr', 'city', 'name', 'year_founded']
        optional_fields = ['coach']

        for field in required_fields:
            if field not in data:
                return jsonify({'message': 'Your request is invalid.'}), 400

        fields = required_fields.copy()
        values = [data[field] for field in required_fields]
        for field in optional_fields:
            if field in data:
                fields.append(field)
                values.append(data[field])

        data = list(zip(fields, values))

        response, status_code = dataProcess_teams.create_teams_status(data)
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({'message': 'Sorry, an unexpected error has occurred.'}), 500

@bp_web_api.route('/teams', methods=['GET'])
def GET_teams():
    page_offset = request.args.get('page_offset', type=int)
    page_length = request.args.get('page_length', type=int)
    sort_field = request.args.get('sort_field')
    sort_order = request.args.get('sort_order')

    if page_offset is None or page_length is None or not sort_field or not sort_order:
        return jsonify({"message": "Your request is invalid."}), 400

    if page_length == 0:
        return jsonify([]), 200
    
    response_data, status_code = dataProcess_teams.get_team(page_length, page_offset, sort_field, sort_order)
    # return jsonify(response_data), status_code
    return jsonify(response_data), status_code

@bp_web_api.route('/teams/<int:id>', methods=['PATCH'])
def PATCH_teams(id):
    session_id = request.cookies.get('session_id')
    if session_id not in sessions:
        return jsonify({"message": "You are not authorized to access this resource."}), 401

    try:
        data = request.json
        response, status_code = dataProcess_teams.update_teams_status(id,data)
        return jsonify(response),status_code

    except Exception as e:
        return jsonify({'message': 'Sorry, an unexpected error has occurred.'}), 500


# Player Profiles API
@bp_web_api.route('/player/profile', methods=['POST'])
def post_player_profiles():
  try:
    cookies = request.cookies
    session_id = cookies.get('session_id')
    if session_id is None:
      return jsonify({"message": "You are not authorized to access this resource."}), 401

    data = request.get_json()
      
    # 檢查必要參數
    if 'name' not in data:
        return jsonify({"message": "Your request is invalid."}), 400

    # 取得參數
    player_profile = {
        'name': data.get('name'),
        'birthdate': data.get('birthdate'),
        'country': data.get('country'),
        'height': data.get('height'),
        'position': data.get('position'),
        'team_name': data.get('team_name'),
        'weight': data.get('weight')
    }
    response_data, status_code = dataProcess_player_profiles.post_player_profiles(player_profile)
  except Exception:
    return jsonify({"message": "Sorry, an unexpected error has occurred."}), 500
  return jsonify(response_data), status_code

@bp_web_api.route('/players/profile', methods=['GET'])
def get_player_profile():
    try:
      page_offset = request.args.get('page_offset', type=int)
      page_length = request.args.get('page_length', type=int)
      sort_field = request.args.get('sort_field', type=str)
      sort_order = request.args.get('sort_order', type=str)
      if None in [page_offset, page_length, sort_field, sort_order] or sort_order not in ['ascending', 'descending']:
          return jsonify({"message": "Your request is invalid."}), 400
      response_data, status_code = dataProcess_player_profiles.get_player_profiles(page_length, page_offset, sort_field, sort_order)
    except Exception:
      return jsonify({"message": "Sorry, an unexpected error has occurred."}), 500
    return response_data, status_code

@bp_web_api.route('/players/<int:id>/profile', methods=['DELETE'])
def delete_player_profile(id):
    try:
      cookies = request.cookies
      session_id = cookies.get('session_id')
      if session_id is None:
        return jsonify({"message": "You are not authorized to access this resource."}), 401
      response_data, status_code = dataProcess_player_profiles.delete_player_profiles(id)
    except Exception:
      return jsonify({"message": "Sorry, an unexpected error has occurred."}), 500
    return response_data, status_code

    # response_data, status_code = dataProcess_player_profiles.player_profiles_put_stub()
    # return jsonify(response_data), status_code
    response_data, status_code = dataProcess_player_profiles.player_profiles_delete_stub(id)
    return jsonify(response_data), status_code

@bp_web_api.route('/players/<int:id>/profile', methods=['PATCH'])
def patch_player_profile(id):
    try:
      cookies = request.cookies
      session_id = cookies.get('session_id')
      if session_id is None:
        return jsonify({"message": "You are not authorized to access this resource."}), 401
      data = request.get_json()
      if not data:
        return jsonify({"message": "Your request is invalid."}), 400
      player_profile = {
          'name': data.get('name'),
          'birthdate': data.get('birthdate'),
          'country': data.get('country'),
          'height': data.get('height'),
          'position': data.get('position'),
          'team_name': data.get('team_name'),
          'weight': data.get('weight')
      }
      response_data, status_code = dataProcess_player_profiles.patch_player_profiles(id,player_profile)
    except Exception:
      return jsonify({"message": "Sorry, an unexpected error has occurred."}), 500
    return response_data, status_code



# Player Stats API 取得球員表現
@bp_web_api.route('/players/stats', methods=['GET'])
def get_player_stats():
    page_offset = request.args.get('page_offset', type=int)
    page_length = request.args.get('page_length', type=int)
    sort_field = request.args.get('sort_field')
    sort_order = request.args.get('sort_order')

    if page_offset is None or page_length is None or not sort_field or not sort_order:
        return jsonify({"message": "Your request is invalid."}), 400

    if page_length == 0:
        return jsonify([]), 200

    response_data, status_code = dataProcess_player_stats.get_player_stats(page_length, page_offset, sort_field, sort_order)
    # return jsonify(response_data), status_code
    return jsonify(response_data), status_code

# Player Stats API 新增球員資料
@bp_web_api.route('/player/stat', methods=['POST'])
def create_player_stats():
    session_id = request.cookies.get('session_id')
    if not request.is_json:
        return jsonify({"message": "Your request is invalid."}), 400

    
    req_data = request.get_json()
    if session_id in sessions:
        try:
            name = req_data['name']
            game_date = req_data['game_date']
            game_away_abbr = req_data['game_away_abbr']
            game_home_abbr = req_data['game_home_abbr']
        except KeyError:
            return jsonify({"message": "Your request is invalid."}), 400
        
        assist = req_data.get('assist', None)
        hit = req_data.get('hit', None)
        steal = req_data.get('steal', None)
        rebound = req_data.get('rebound', None)
        free_throw = req_data.get('free_throw', None)
        score = req_data.get('score', None)

        #print(name,game_date,game_away_abbr,game_home_abbr,assist,hit,steal,rebound,free_throw,score)
        
        response_data, status_code = dataProcess_player_stats.create_player_stats(name, game_date, game_home_abbr, game_away_abbr, assist, hit, steal, rebound, free_throw, score)
        
        # print("create: ", response_data)

        # player_id = response_data['id']
        # game_id = response_data['game_id']
        # record, status_code1 = dataProcess_player_stats.fetch_game_record(player_id, game_id)
        # print("create and search: ",record, status_code1)

        return jsonify(response_data), status_code
    else:
        return jsonify({"message": "You are not authorized to access this resource."}), 401

# player-stats 更新
@bp_web_api.route('/players/<int:id>/stats/<int:game_id>', methods=['PATCH'])
def update_player_stats(id, game_id):
    
    key_to_column_mapping = {
    'assist': 'Assist',
    'hit': 'Hit',
    'steal': 'Steal',
    'rebound': 'Rebound',
    'free_throw': 'FreeThrow',
    'score': 'Score'
    }
    
    session_id = request.cookies.get('session_id')
    if not request.is_json:
        return jsonify({"message": "Your request is invalid."}), 400

    req_data = request.get_json()
    if session_id in sessions:

        # print("pid: ", id, game_id)
        if id is None or game_id is None:
            return jsonify({"message": "Your request is invalid."}), 400

        update_fields = {key_to_column_mapping[k]: v for k, v in req_data.items() if k in key_to_column_mapping}
        # print(update_fields)

        if not update_fields:
            return jsonify({"message": "Your request is invalid."}), 400

        # record, status_code1 = dataProcess_player_stats.fetch_game_record(id, game_id)
        # print("before update: ",record, status_code1)

        response_data, status_code = dataProcess_player_stats.update_player_stats(id, game_id, update_fields)

        # record, status_code1 = dataProcess_player_stats.fetch_game_record(id, game_id)
        # print("after update: ",record, status_code1)

        return jsonify(response_data), status_code
    
    else:
        return jsonify({"message": "You are not authorized to access this resource."}), 401

# player-stats 刪除
@bp_web_api.route('/players/<int:id>/stats/<int:game_id>', methods=['DELETE'])
def delete_player_stats(id, game_id):
    session_id = request.cookies.get('session_id')

    if session_id in sessions:

        if id is None or game_id is None:
            return jsonify({"message": "Your request is invalid."}), 400


        response_data, status_code = dataProcess_player_stats.delete_player_stats(id, game_id)

        # record, status_code1 = dataProcess_player_stats.fetch_game_record(id, game_id)
        # print("hello")
        # if not record:
        #     print("not found!")

        return response_data, status_code
    
    else:
        return jsonify({"message": "You are not authorized to access this resource."}), 401

# Render the HTML file at ../web/dist/index.html
@bp_web_page.route('/')
def get_index_page():
    return render_template('index.html')

@bp_web_page.errorhandler(404)
def get_dynamic_page(*_):
    return render_template('index.html')

def init_app(app: Flask):
    # 負責靜態資源
    app.register_blueprint(bp_web_page)
    # 負責處理 API 請求
    app.register_blueprint(bp_web_api)
    # Generate Web API documentation
    api_doc(
        app,
        config_url='https://raw.githubusercontent.com/Basketball-Competition-Dashboard/doc/main/api/web/openapi.yml',
        url_prefix='/_doc/api/web',
        title='Web API Documentation',
        editor=True,
    )
    # Enable CORS
    CORS(app, resources={r"/api/web/*": {"origins": "http://localhost:5173"}})

    app.logger.info(' * Web API Documentation URL: http://localhost:5000/_doc/api/web')