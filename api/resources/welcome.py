from typing import Any

from flask_restful import Resource, request
from flasgger import swag_from
from http import HTTPStatus
from api.model.welcome import WelcomeModel
from api.schema.welcome import WelcomeSchema


class WelcomeApi(Resource):
    @swag_from({
        'responses': {
            HTTPStatus.OK.value: {
                'description': 'Welcome to the Flask Starter Kit',
                'schema': WelcomeSchema
            }
        }
    })
    def get(self):
        """
        1 liner about the route
        A more detailed description of the endpoint
        ---
        """
        result = WelcomeModel()

        return WelcomeSchema().dump(result), 200

    def post(self):
        body = request.get_json()

        return 200
