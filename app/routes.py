from flask import Blueprint, Flask, jsonify, render_template, request, Response,make_response
import sqlite3
import uuid
from swagger_ui import api_doc
from app import dataProcess_player_profiles

DATABASE_PATH = f'{__file__}/../../data/nbaDB.db'

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

@bp_web_api.route('/games', methods=['POST'])
def get_games():
    "TODO: Stub for the function"
    request_data = request.get_json()
    page = request_data.get('page', {})
    sort = request_data.get('sort', {})

    offset = page.get('offset', 0)
    length = page.get('length', 10)
    
    sort_field = sort.get('field', 'date')
    sort_order = sort.get('order', 'ascending')

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    sort_order_sql = 'ASC' if sort_order == 'ascending' else 'DESC'
    # query = '''
    #     SELECT 
    #         ATTEND.GID, Game.Date, Team.TName, Attend.Score, Attend.is_win_team 
    #     FROM 
    #         ATTEND 
    #     JOIN 
    #         Team ON Attend.TID = Team.TID
    #     JOIN 
    #         Game ON Game.GID = Attend.GID 
    #     where
    #         Attend.GID='0024600008' 
    #     ORDER BY 
    #         ? ?
    #     LIMIT ? OFFSET ?
    # '''
    query = '''
        SELECT 
            ATTEND.GID, Game.Date, ATTEND.TID, Team.TName, Attend.Score, Attend.is_win_team
        FROM 
            ATTEND 
        JOIN 
            Game ON Game.GID = Attend.GID 
        LEFT OUTER JOIN 
            Team ON Attend.TID = Team.TID
        where
            Attend.GID='0024600008' 
        ORDER BY 
            ? ?
        LIMIT ? OFFSET ?
    '''
    cursor.execute(query, (sort_field, sort_order_sql, length, offset))
    rows = cursor.fetchall()
    conn.close()
    print(rows)
    
    # games = {}
    # for row in rows:
    #     game_id = row[0]
    #     if game_id not in games:
    #         games[game_id] = {
    #             'id': game_id,# Game GID
    #             'date': row[1],# Game Date
    #             'home_name': '',# attend ishometeam(得知GID) -> ishometeam=1 team TName
    #             'away_name': '',# attend ishometeam(得知GID) -> ishometeam=0 team TName
    #             'home_score': 0,# attend score 
    #             'away_score': 0,# attend score 
    #             'winner_name': '' # attend is_win_team
    #         }
    #     team_name = row[2]
    #     score = row[3]
    #     is_win_team = row[4]
        
    #     if games[game_id]['home_name'] == '':
    #         games[game_id]['home_name'] = team_name
    #         games[game_id]['home_score'] = score
    #         if is_win_team == 'W':
    #             games[game_id]['winner_name'] = team_name
    #         # else:
    #         #     games[game_id]['winner_name'] = 
    #     else:
    #         games[game_id]['away_name'] = team_name
    #         games[game_id]['away_score'] = score
    #         if is_win_team:
    #             games[game_id]['winner_name'] = team_name

    # data = list(games.values())
    
    # response = {
    #     'page': {
    #         'offset': offset,
    #         'length': length
    #     },
    #     'values': data
    # }
    response = {
        "page": {
            "length": 10,
            "offset": 0
            },
        "values": [
            {
            "away_name": "Nets",
            "away_score": 98,
            "date": "2024-05-06",
            "home_name": "Celtics",
            "home_score": 123,
            "id": 3001,
            "winner_name": "Celtics"
            }
        ]
    }

    return jsonify(response)

@bp_web_api.route('/games', methods=['PUT'])
def put_games():
    "TODO: Stub for the function"
    request_data = request.get_json()
    
    # if not request_data:
    #     return make_response(jsonify({'message': 'Your request is invalid.'}), 400)
    
    # conn = sqlite3.connect(DATABASE_PATH)
    # cursor = conn.cursor()
    
    # for game in request_data:
    #     if 'id' in game:
    #         cursor.execute("""
    #             UPDATE Game SET 
    #                 date = ?, 
    #                 home_name = ?, 
    #                 away_name = ?, 
    #                 home_score = ?, 
    #                 away_score = ?, 
    #                 winner_name = ? 
    #             WHERE id = ?
    #         """, (
    #             game['date'],
    #             game['home_name'],
    #             game['away_name'],
    #             game['home_score'],
    #             game['away_score'],
    #             game['winner_name'],
    #             game['id']
    #         ))
            
    #         if cursor.rowcount == 0:  # 沒有更新的行數
    #             conn.rollback()
    #             conn.close()
    #             return make_response(jsonify({'message': 'Your request is invalid.'}), 400)
    #     else:
    #         cursor.execute("""
    #             INSERT INTO Game (date, home_name, away_name, home_score, away_score, winner_name) 
    #             VALUES (?, ?, ?, ?, ?, ?)
    #         """, (
    #             game['date'],
    #             game['home_name'],
    #             game['away_name'],
    #             game['home_score'],
    #             game['away_score'],
    #             game.get('winner_name')
    #         ))

    # conn.commit()
    # conn.close()

    return make_response(jsonify({'message': 'Created'}), 201 if any('id' not in game for game in request_data) else 204)

@bp_web_api.route('/teams', methods=['POST'])
def GET_teams():
    "TODO: Stub for the function"
    return {
        "page": {
            "length": 10,
            "offset": 0
        },
        "values": [
            {
            "abbr": "BOS",
            "city": "Boston",
            "coach": "Joseph Mazzulla",
            "id": 60020,
            "name": "Celtics",
            "year_founded": 1946
            }
        ]
    }

# Player Profiles API
@bp_web_api.route('/player-profiles', methods=['POST'])
def get_player_profiles():
  if not request.is_json:
    return jsonify({"message": "Your request is invalid."}), 400

  req_data = request.get_json()

  try:
    page = req_data['birthdate']
    sort = req_data['country']
    length = page['height']
    offset = page['name']
    sort_field = sort['position']
    sort_order = sort['team_name']
    weight = page['weight']
  except KeyError:
    return jsonify({"message": "Your request is invalid."}), 400
  print(length, offset, sort_field, sort_order, weight, page, sort)
  breakpoint()
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
