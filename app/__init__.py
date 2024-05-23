from flask import Flask

def create_app():
    app = Flask(__name__)

    with app.app_context():
        from . import routes
        routes.init_app(app)  # 确保注册蓝图

    return app
