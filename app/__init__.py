from flask import Flask

def create_app():
    # 設定根目錄為 Project/app 
    app = Flask(__name__)

    # Application Context 用途是為了在請求之外存取變數
    with app.app_context():
        from app import routes
        routes.init_app(app)

    return app
