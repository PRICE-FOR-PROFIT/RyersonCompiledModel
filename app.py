from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from api.resources.routes import initialize_routes


def create_app():
    flask_app = Flask(__name__)
    api = Api(flask_app)

    flask_app.config['SWAGGER'] = {
        'title': 'Ryerson Compiled Model',
    }

    Swagger(flask_app)

    # Initialize Config
    flask_app.config.from_pyfile('config.py')

    initialize_routes(api)

    return flask_app


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app = create_app()

    app.run(host='0.0.0.0', port=port)
