import sqlite3
from flask import Blueprint, jsonify

bp = Blueprint('main', __name__)

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
            # 根据实际的表结构添加更多的列
        })
    return jsonify(data)

def init_app(app):
    app.register_blueprint(bp)
