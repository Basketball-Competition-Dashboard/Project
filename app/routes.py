import sqlite3
from flask import Blueprint, jsonify, render_template

# __name__ == app.routes
# __name__取得當前模組的名稱，用於定位相對路徑
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
    # 渲染位於 ../web/dist/index.html 的模板
    return render_template('index.html')

@bp_web_page.errorhandler(404)
def get_dynamic_page(*_):
    return render_template('index.html')


def init_app(app):
    # 負責靜態資源和模板渲染
    app.register_blueprint(bp_web_page)

    # 負責 API
    app.register_blueprint(bp)
