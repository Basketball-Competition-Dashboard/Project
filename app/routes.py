from flask import Blueprint, Flask, jsonify, render_template, request, make_response, Response
import sqlite3
import uuid
from swagger_ui import api_doc

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

cookie = {}

@bp_web_api.route('/ping', methods=['GET'])
def ping():
    return jsonify('Pong!')

@bp_web_api.route('/auth/login', methods=['GET', 'POST'])  
def login():   
    if request.method == 'GET':  
           return '''
     <form action='login' method='POST'>
     <input type='text' name='name' id='name' placeholder='name'/>
     <input type='password' name='credential' id='credential' placeholder='credential'/>
     <input type='submit' name='submit'/>
     </form>
                  '''

    conn = sqlite3.connect('data/nbaDB.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Manager;')
    rows = cursor.fetchall()
    conn.close()

    name = request.form['name']  
    for username, password in rows:
        if request.form['credential'] == password and name == username :  
            session_id = str(uuid.uuid4().hex)
            cookie['session_id'] = session_id
            response = Response(status=201)
            response.set_cookie('session_id', session_id, httponly=True, max_age=31536000, path='/', samesite='Strict')
        return response
    
    return jsonify({"message": "The resource you are accessing is not found."}), 404

@bp_web_api.route('/auth/logout')  
def logout():
    session_id = request.cookies.get('session_id')  
    if session_id :
        response = Response(status=204)
        response.set_cookie('session_id', '', httponly=True, max_age=0, path='/', samesite='Strict')
        return response  
    
    return jsonify({"message": "You are not authorized to access this resource."}), 404

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

    app.logger.info(' * Web API Documentation URL: http://127.0.0.1:5000/api/web/auth/login')
