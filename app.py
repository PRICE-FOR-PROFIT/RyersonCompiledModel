from flask import Flask
from flasgger import Swagger
from api.route.home import home_api


def create_app():
    flask_app = Flask(__name__)

    flask_app.config['SWAGGER'] = {
        'title': 'Ryerson Compiled Model',
    }
    swagger = Swagger(flask_app)

    # Initialize Config
    flask_app.config.from_pyfile('config.py')
    flask_app.register_blueprint(home_api, url_prefix='/api')

    return flask_app


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app = create_app()

    app.run(host='0.0.0.0', port=port)
