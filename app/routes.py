from flask import Blueprint, Flask, jsonify, render_template, request, Response,make_response
import sqlite3
import uuid
from swagger_ui import api_doc
from app import dataProcess_player_profiles,dataProcess_games

DATABASE_PATH = f'data/nbaDB.db'

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
    try:
        data = request.get_json()
        required_fields = ['date', 'away_name', 'home_name']
        optional_fields = ["away_score", "home_score", "is_home_winner"]

        # 確認required資訊都有
        for field in required_fields:
            if field not in data:
                return jsonify({'message': 'Your request is invalid.'}), 400

        # 確認主隊與客隊存在於Team中
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
        
        response, status_code = dataProcess_games.create_games_status(data,home_team_city,home_team_id,away_team_id)

        return jsonify(response),status_code

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
    try:
        data = request.json
        response, status_code = dataProcess_games.update_games_status(id,team_id,data)
        return jsonify(response),status_code

    except Exception as e:
        return jsonify({'message': 'Sorry, an unexpected error has occurred.'}), 500

@bp_web_api.route('/team', methods=['POST'])
def POST_teams():
    try:
        data = request.get_json()
        required_fields = ['abbr', 'city', 'name','year_founded']
        optional_fields = ['coach']

        # 確認required資訊都有
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
        
        response, status_code = dataProcess_games.create_teams_status(data)

        return jsonify(response),status_code

    except Exception as e:
        return jsonify({'message': 'Sorry, an unexpected error has occurred.'}), 500    

# Player Profiles API
@bp_web_api.route('/player-profiles', methods=['POST'])
def get_player_profiles():
  if not request.is_json:
    return jsonify({"message": "Your request is invalid."}), 400

  req_data = request.get_json()

  try:
    page = req_data['page']
    sort = req_data['sort']
    length = page['length']
    offset = page['offset']
    sort_field = sort['field']
    sort_order = sort['order']
  except KeyError:
    return jsonify({"message": "Your request is invalid."}), 400

  print(length, offset, sort_field, sort_order)
  # TODO: Stub for the response
  if length == 0 and offset == 8888:
    return jsonify([]), 200

  response_data, status_code = dataProcess_player_profiles.fetch_player_profiles(length, offset, sort_field, sort_order)
  return jsonify(response_data), status_code

@bp_web_api.route('/player-profiles', methods=['PUT'])
def update_or_create_player_profile():
    "TODO: Stub for the function"
    response_data, status_code = dataProcess_player_profiles.player_profiles_put_stub()
    return jsonify(response_data), status_code
    cookies = request.cookies
    session_id = cookies.get('session_id')
    
    print("Cookies received:", cookies)
    print("Session ID:", session_id)
    if not request.is_json:
      return jsonify({"message": "Your request is invalid."}), 400
    
    req_data = request.get_json()
    print(req_data[0])
    return "ok"

@bp_web_api.route('/player-profiles/<int:id>', methods=['DELETE'])
def delete_player_profile(id):
    "TODO: Stub for the function"
    # response_data, status_code = dataProcess_player_profiles.player_profiles_put_stub()
    # return jsonify(response_data), status_code
    response_data, status_code = dataProcess_player_profiles.player_profiles_delete_stub(id)
    return jsonify(response_data), status_code

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

    app.logger.info(' * Web API Documentation URL: http://127.0.0.1:5000/_doc/api/web')
