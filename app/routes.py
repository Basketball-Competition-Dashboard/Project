import sqlite3
from flask import Blueprint, jsonify, render_template

bp = Blueprint('main', __name__)
webpage = Blueprint(
    'webpage',
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


@webpage.route('/')
def get_index_html():
    return render_template('index.html')


def init_app(app):
    app.register_blueprint(webpage)
    app.register_blueprint(bp)
