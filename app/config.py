import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///nbaDB.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
