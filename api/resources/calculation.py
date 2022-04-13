import http.client
import json
from typing import Any
from uuid import uuid4
from flask import request
from flask_restful import Resource
from flasgger import swag_from
from http import HTTPStatus

from api.service.modelservice import ModelService
from config import Config
from api.schema.responsewrapperwithmeta import ResponseWrapperWithMetaSchema
from api.schema.errorwrapperwithmeta import ErrorWrapperWithMetaSchema
from api.service.authenticationhelper import AuthenticationHelper
from api.model.calculationoutput import CalculationOutputModel
from api.service.recommendedprice import RecommendedPrice
from api.service.quotelinesap import QuoteLineSap
from api.service.sqllitelookupservice import SqlLiteLookupService
from api.service.queuedlogger import QueuedLogger


def lower_keys(data):
    if isinstance(data, list):
        return [lower_keys(v) for v in data]
    elif isinstance(data, dict):
        return {k.lower(): lower_keys(v) for (k, v) in data.items()}
    else:
        return data


def generate_error_wrapper_with_meta(code: int, description: str, calculation_id: str) -> dict:
    metadata = {"calculationIid": calculation_id}

    error = {"responseCode": code, "description": description}

    return {"error": error, "metadata": metadata}


def transform_input_list_object_array(data: list) -> dict[str, Any]:
    transformed_data = {}

    for line in data:
        property_name = line["name"]
        property_value = line["value"]

        if isinstance(property_value, list):
            converted = []

            for pline in property_value:
                if isinstance(pline, list):
                    converted.append(transform_input_list_object_array(pline))
                else:
                    converted.append(pline)

            transformed_data[property_name] = converted
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


def convert_json_to_calculation_output(obj: {}) -> [{}]:
    output = list()

    for key, value in obj.items():
        if isinstance(value, list):
            o = CalculationOutputModel()

            o.Name = key
            o.Passthrough = True
            o.Value = convert_list_to_output_list(value)

            output.append(o)
        else:
            o = CalculationOutputModel()

            o.Name = key
            o.Passthrough = True
            o.Value = value

            output.append(o)

    return output


def convert_list_to_output_list(arr: list) -> list:
    output = list()

    for line in arr:
        line_data = list()

        for key, value in line.items():
            if isinstance(value, list):
                val = convert_list_to_output_list(value)
            else:
                val = value

            calc = CalculationOutputModel()

            calc.Name = key
            calc.Passthrough = True
            calc.Value = val

            line_data.append(calc)

        output.append(line_data)

    return output


def convert_calculation_outputs_to_array(outputs: list) -> list:
    arr_data = list()

    for output_item in outputs:
        name = output_item.Name
        passthrough = output_item.Passthrough

        if isinstance(output_item.Value, list):
            all_lines = list()

            for item in output_item.Value:
                value = convert_calculation_outputs_to_array(item)

                all_lines.append(value)

            line = {"name": name, "passthrough": passthrough, "value": all_lines}
        else:
            line = {"name": name, "passthrough": passthrough, "value": output_item.Value}

        arr_data.append(line)

    return arr_data


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
            HTTPStatus.OK: {
                'description': 'The output of the execution of the model.',
                'schema': ResponseWrapperWithMetaSchema
            },
            HTTPStatus.BAD_REQUEST: {
                'description': 'The input JSON was not correct for the requested model.',
                'schema': ResponseWrapperWithMetaSchema
            },
            HTTPStatus.UNAUTHORIZED: {
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

        # REM create request telemetry
        # var requestTelemetry = HttpContext.Features.Get < RequestTelemetry > ();
        #
        # requestTelemetry?.Properties.Add("CalculationId", calculationId);

        if not calculation_id:
            calculation_id = uuid4().hex

        if not (model_id.casefold() == "recommendedPrice".casefold() or model_id.casefold() == "quoteLineSap".casefold()):
            error_info = f"Model not found for clientId: {client_id}, modelId: {model_id}"

            ex = Exception(error_info)
            # REM _telemetry.TrackTrace(errorInfo, SeverityLevel.Error);

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
        has_debug_permissions = True

        metadata = {"calculationid": calculation_id}

        calculation_inputs = lower_keys(request.get_json())

        if calculation_inputs["inputparameters"] is not None:
            try:
                input_data = calculation_inputs["inputparameters"]

                properties = extract_properties_to_include_in_response(input_data)
                converted_inputs = lower_keys([transform_input_list_object_array(input_data)])

                bob = json.dumps(converted_inputs)

                calculation_inputs["modelinputs"] = converted_inputs[0]
                calculation_inputs["includeinresponse"] = properties
            except Exception as ex:
                # REM _telemetry.TrackTrace(ex.Message, SeverityLevel.Error);
                error_info = f"Error evaluating model: {model_id}"

                output = generate_error_wrapper_with_meta(HTTPStatus.NOT_FOUND, error_info, calculation_id)

                return ErrorWrapperWithMetaSchema().dump(output), HTTPStatus.BAD_REQUEST

        if calculation_inputs["modelinputs"] is None:
            payload_error_info = "Input payload not structured correctly, neither property 'InputParameters' or 'modelInput' is not set."

            # ex = Exception(payload_error_info)

            # REM _telemetry.TrackTrace(ex.Message, SeverityLevel.Error);

            output = generate_error_wrapper_with_meta(HTTPStatus.BAD_REQUEST, payload_error_info, calculation_id)

            return ErrorWrapperWithMetaSchema().dump(output), http.client.BAD_REQUEST

        try:
            model_service = ModelService()

            if model_id.casefold() == "recommendedPrice".casefold():
                model = model_service.get_model(model_id, is_debug_header_set and has_debug_permissions)

                lookup_service = SqlLiteLookupService()
                queued_logger = QueuedLogger()
                quote_line_sap = QuoteLineSap()
                recommended_price_model = RecommendedPrice(lookup_service, queued_logger, Config, quote_line_sap)

                json_output = recommended_price_model.execute_model(authenticated_client_id, client_id, model, calculation_inputs, calculation_id, token)
            else:
                model = model_service.get_model(model_id, is_debug_header_set and has_debug_permissions)

                quote_line_sap = QuoteLineSap()

                json_output = quote_line_sap.execute_model(authenticated_client_id, client_id, model, calculation_inputs, calculation_id, token)

            # Collect all the outputs from the calc engine into the output dictionary
            output_dictionary = {k: json.dumps(v) for (k, v) in json_output.items()}

            output_dictionary["AuthorizationClientId"] = authenticated_client_id
            output_dictionary["ModelClientId"] = client_id

            calc_info = f"Calculation performed, {len(json_output)} output(s) returned."

            # telemetry.TrackTrace

        # parameter type exception
        # _telemetry.TrackTrace(ex.Message, SeverityLevel.Error);
        # symbol not found exception
        # _telemetry.TrackTrace(ex.Message, SeverityLevel.Error);
        # masked exception
        # _telemetry.TrackTrace(ex.Message, SeverityLevel.Error);
        except Exception as ex:
            # REM _telemetry.TrackTrace(ex.Message, SeverityLevel.Error);

            error = f"Error evaluating model: {model_id}. {ex}"

            output = generate_error_wrapper_with_meta(HTTPStatus.BAD_REQUEST, error, calculation_id)

            return ErrorWrapperWithMetaSchema().dump(output), http.client.BAD_REQUEST

        if calculation_inputs["inputparameters"] is not None:
            converted_output = convert_json_to_calculation_output(json_output)

            data = convert_calculation_outputs_to_array(converted_output)
        else:
            data = json_output

        response = {"data": data, "metadata": metadata}

        return ResponseWrapperWithMetaSchema().dump(response), HTTPStatus.OK
