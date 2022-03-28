from uuid import uuid4
from flask import request
from flask_restful import Resource
from flasgger import swag_from
from http import HTTPStatus
from api.schema.responsewrapperwithmeta import ResponseWrapperWithMetaSchema
from api.schema.errorwrapperwithmeta import ErrorWrapperWithMetaSchema
from api.service.authenticationhelper import AuthenticationHelper


def generate_error_wrapper_with_meta(code: str, description: str, calculation_id: str) -> dict:
    metadata = {"calculationIid": calculation_id}

    error = {"responseCode": code, "description": description}

    return {"error": error, "metadata": metadata}


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
        token = request.headers.get("Authorization").split(" ")[1]
        authenticated_client_id = AuthenticationHelper.extract_client_id(token)

        calculation_id = request.headers.get("x-insight-calculationid")

        if not calculation_id:
            calculation_id = uuid4().hex

        if not (model_id.casefold() == "recommendedPrice".casefold() or model_id.casefold() == "quoteLineSap".casefold()):
            error_info = f"Model not found for clientId: {client_id}, modelId: {model_id}"

            ex = Exception(error_info)

            output = generate_error_wrapper_with_meta(HTTPStatus.NOT_FOUND, error_info, calculation_id)

            return ErrorWrapperWithMetaSchema().dump(output), HTTPStatus.NOT_FOUND

        metadata = {"calculationid": calculation_id}

        payload = request.get_json()

        result = {"name": "John", "age": 30, "city": "New York"}

        output = {"data": result, "metadata": metadata}

        return ResponseWrapperWithMetaSchema().dump(output), HTTPStatus.OK
