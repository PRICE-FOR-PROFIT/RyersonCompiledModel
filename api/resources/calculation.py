import json

from flask_restful import Resource
from flasgger import swag_from
from http import HTTPStatus
from api.schema.responsewrapperwithmeta import ResponseWrapperWithMetaSchema



class CalculationApi(Resource):
    @swag_from({
        'parameters': [
            {
                'description': 'ID of the client.',
                'in': 'path',
                'name': 'client_id',
                'required': True,
                'type': 'string'
            },
            {
                'description': 'ID of the model.',
                'in': 'path',
                'name': 'model_id',
                'required': True,
                'type': 'string'
            }
        ],
        'responses': {
            HTTPStatus.OK.value: {
                'description': 'The output of the execution of the model.',
                'schema': ResponseWrapperWithMetaSchema
            },
            HTTPStatus.BAD_REQUEST.value: {
                'description': 'The input JSON was not correct for the requested model.',
                'schema': ResponseWrapperWithMetaSchema
            },
            HTTPStatus.UNAUTHORIZED.value: {
                'description': 'Caller was not authorized to call their API.',
                'schema': ResponseWrapperWithMetaSchema
            }
        }
    })
    def post(self, client_id, model_id):
        """
        Executes the requested model using the supplied JSON inputs.
        ---
        """
        result = {"name": "John", "age": 30, "city": "New York"}
        metadata = {"calculationIid": "123456789"}

        output = {"data": result, "metadata": metadata}

        return ResponseWrapperWithMetaSchema().dump(output), 200
