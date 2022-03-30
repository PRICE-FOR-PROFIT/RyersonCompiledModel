import json
from uuid import uuid4
from flask import request
from flask_restful import Resource
from flasgger import swag_from
from http import HTTPStatus
from api.schema.responsewrapperwithmeta import ResponseWrapperWithMetaSchema
from api.schema.errorwrapperwithmeta import ErrorWrapperWithMetaSchema
from api.service.authenticationhelper import AuthenticationHelper


def lower_keys(data):
    if isinstance(data, list):
        return [lower_keys(v) for v in data]
    elif isinstance(data, dict):
        return {k.lower(): lower_keys(v) for (k, v) in data.items()}
    else:
        return data


def generate_error_wrapper_with_meta(code: str, description: str, calculation_id: str) -> dict:
    metadata = {"calculationIid": calculation_id}

    error = {"responseCode": code, "description": description}

    return {"error": error, "metadata": metadata}


def transform_input_list_object_array(data: [dict]) -> [str]:
    transformed_data = {}

    for line in data:
        property_name = line["name"]
        property_value = line["value"]

        if isinstance(property_value, list):
            transformed_data[property_name] = [transform_input_list_object_array(property_value[0])]
        else:
            transformed_data[property_name] = property_value

    return transformed_data


def extract_properties_to_include_in_response(data: dict) -> [str]:
    try:
        properties = []

        for line in data:
            key = line["name"]
            return_in_output = False if line["returninoutput"] is None else line["returninoutput"]

            if return_in_output and not (key in properties):
                properties.append(key)

            if key == "":
                print("")

            if line["value"] and isinstance(line["value"], dict):
                properties.append(extract_properties_to_include_in_response(line["value"]))

        return properties
    except Exception as ex:
        print(ex)
        return ""


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

        debug_header = request.headers.get("x-insight-debug")

        is_debug_header_set = False if debug_header is None else debug_header.casefold() == "true".casefold()

        # var scopes = new
        # List < string > ();
        # var azureB2CScopes = HttpContext.User.Claims.FirstOrDefault(c= > c.Type == "http://schemas.microsoft.com/identity/claims/scope")?.Value;
        # if (!string.IsNullOrWhiteSpace(azureB2CScopes)) scopes.AddRange(azureB2CScopes.Split(" "));
        # var insightClaims = HttpContext.User.Claims.FirstOrDefault(c= > c.Type == "InsightClaims")?.Value;
        # if (!string.IsNullOrWhiteSpace(insightClaims)) scopes.AddRange(insightClaims.Split(" "));
        # scopes = scopes.Distinct().ToList();
        # var hasDebugPermissions = HttpContext.User.IsInRole("ces.global.debug") | | scopes.Contains("ces.global.debug");

        metadata = {"calculationid": calculation_id}

        calculation_inputs = lower_keys(request.get_json())

        if calculation_inputs["inputparameters"] is not None:
            try:
                input_data = calculation_inputs["inputparameters"]

                properties = extract_properties_to_include_in_response(input_data)
                converted_inputs = [transform_input_list_object_array(input_data)]
                
                calculation_inputs["modelinputs"] = converted_inputs
                calculation_inputs["includeinresponse"] = properties
            except Exception as ex:
                error_info = f"Error evaluating model: {model_id}"

                ex = Exception(error_info)

                output = generate_error_wrapper_with_meta(HTTPStatus.NOT_FOUND, error_info, calculation_id)

                return ErrorWrapperWithMetaSchema().dump(output), HTTPStatus.BAD_REQUEST

        result = [{"name": "John", "value": 30}]

        output = {"data": result, "metadata": metadata}

        return ResponseWrapperWithMetaSchema().dump(output), HTTPStatus.OK
