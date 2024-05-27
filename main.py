from app import create_app
from logging import basicConfig, DEBUG
from sys import stderr

if __name__ == '__main__':
    basicConfig(format='%(message)s', level=DEBUG, stream=stderr)
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
