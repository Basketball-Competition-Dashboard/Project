from flask import Blueprint, Flask, jsonify, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user  
import sqlite3
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

login_manager = LoginManager()
login_manager.init_app(bp_web_api)

@bp_web_api.route('/ping', methods=['GET'])
def ping():
    return jsonify('Pong!')

class User(UserMixin):
    pass

@bp_web_api.route('/login', methods=['GET', 'POST'])  
def login():   
    if request.method == 'GET':  
           return '''
     <form action='login' method='POST'>
     <input type='text' name='name' id='name' placeholder='name'/>
     <input type='text' name='credential' id='credential' placeholder='credential'/>
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
            user = User()  
            user.id = name  
            #  這邊，透過login_user來記錄user_id，如下了解程式碼的login_user說明。  
            login_user(user)  
            return 'Login'

    return 'Fail to login'

@bp_web_api.route('/logout')  
def logout():  
    logout_user()  
    return 'Logged out'  
  

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

    app.logger.info(' * Web API Documentation URL: http://127.0.0.1:5000/api/web/login')
