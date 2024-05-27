from flask import Blueprint, Flask, jsonify, render_template
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
        config_path='doc/api/web/openapi.yml',
        url_prefix='/_doc/api/web',
        title='Web API Documentation',
        editor=True,
    )

    app.logger.info(' * Web API Documentation URL: http://127.0.0.1:5000/_doc/api/web')
