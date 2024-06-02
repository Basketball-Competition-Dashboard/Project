from http.cookiejar import Cookie
from flask import Blueprint, Flask, jsonify, render_template, request, json
import sqlite3
from swagger_ui import api_doc
from data import dataProcess

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

@bp_web_api.route('/ping', methods=['GET'])
def ping():
    return jsonify('Pong!')

@bp_web_api.route('/data', methods=['GET'])
def get_data():
    conn = sqlite3.connect('data/nbaDB.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Team;')
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append(
            {
                'column1': row[0],
                'column2': row[1],
            }
        )
    return jsonify(data)

# Player Profiles API
@bp_web_api.route('/player-profiles', methods=['POST'])
def get_player_profiles():
  if not request.is_json:
      return jsonify({"message": "Your request is invalid."}), 400

  req_data = request.get_json()
  page = req_data.get('page', {})
  sort = req_data.get('sort', {})

  length = page.get('length', 0)
  offset = page.get('offset', 8888)
  sort_field = sort.get('field', 'name')
  sort_order = sort.get('order', 'ascending')
  print(length, offset, sort_field, sort_order)
  if length == 0 & offset == 8888:
    return jsonify({
                    "page": {
                      "length": 0,
                      "offset": 8888
                    },
                    "values": []
                  }), 400
  
  response_data, status_code = dataProcess.fetch_player_profiles(length, offset, sort_field, sort_order)
  return jsonify(response_data), status_code

@bp_web_api.route('/player-profiles', methods=['PUT'])
def update_or_create_player_profile():
    cookies = request.cookies
    session_id = cookies.get('session_id')
    print("Cookies received:", cookies)
    print("Session ID:", session_id)
    if not request.is_json:
      return jsonify({"message": "Your request is invalid."}), 400
    
    req_data = request.get_json()
    print(req_data[0])
    return "ok"

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
