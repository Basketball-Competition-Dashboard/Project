import sqlite3
from flask import Blueprint, jsonify, render_template, send_from_directory
from flask_cors import CORS

bp = Blueprint('main', __name__)
bp_web_page = Blueprint(
    'Web page',
    __name__,
    url_prefix='/',
    static_url_path='/',
    static_folder='../web/dist',
    template_folder='../web/dist',
)

@bp.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify(message="Hello, World!")

@bp.route('/api/data', methods=['GET'])
def get_data():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM your_table_name')
    rows = cursor.fetchall()
    conn.close()
    
    data = []
    for row in rows:
        data.append({
            'column1': row[0],
            'column2': row[1],
        })
    return jsonify(data)

@bp_web_page.route('/')
def get_index_page():
    return render_template('index.html')

@bp_web_page.errorhandler(404)
def get_dynamic_page(*_):
    return render_template('index.html')

def init_app(app):
    app.register_blueprint(bp_web_page)
    app.register_blueprint(bp)
    CORS(app, resources={r"/*": {"origins": "*"}})  # 啟用 CORS 並允許所有來源

    @app.route('/swagger-ui/')
    def swagger_ui():
        return send_from_directory('../swagger-ui', 'index.html')

    @app.route('/swagger-ui/<path:path>')
    def swagger_static(path):
        return send_from_directory('../swagger-ui', path)

    @app.route('/openapi.yml')
    def openapi_spec():
        return send_from_directory('..', 'openapi.yml')
