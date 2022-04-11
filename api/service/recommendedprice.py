import datetime
import json
from typing import Any
from uuid import uuid4

from api.service.calculationhelper import CalculationHelper
from config import Config
from api.exceptions.symbolnotfounderror import SymbolNotFoundError
from api.service.interfaces.calcengineinterface import CalcEngineInterface
from api.service.interfaces.lookupserviceinterface import LookupServiceInterface
from api.service.interfaces.queuedloggerinterface import QueuedLoggerInterface
from api.model.model import ModelModel
from api.model.loginformation import LogInformationModel


class RecommendedPrice(CalcEngineInterface):
    def __init__(self, lookup_service: LookupServiceInterface, queued_logger: QueuedLoggerInterface, configuration: Config, quote_line_sap: CalcEngineInterface):
        self._lookup_service = lookup_service
        self._config = configuration
        self._quote_line_sap = quote_line_sap
        self._disable_logging = configuration.disable_Logging
        self._namespace = configuration.namespace
        self._base_calculation_endpoint = configuration.base_calculation_endpoint
        self._fan_out = configuration.fan_out

        if self._base_calculation_endpoint == "":
            self._base_calculation_endpoint = f"http://ccs.{self._namespace}.svc.cluster.local"

    def execute_model(self, request_client_id: str, client_id: str, model: ModelModel, original_payload: dict[str, Any], calculation_id: str, token: str) -> dict[str, Any]:
        json_output = {}

        log_information = LogInformationModel()

        log_information.id = uuid4()
        log_information.create_date = datetime.datetime.now()
        log_information.calculation_id = calculation_id
        log_information.model_id = model.id
        log_information.client_id = client_id
        log_information.authorization_id = request_client_id
        log_information.model_version = model.version
        log_information.original_payload = json.dumps(original_payload)

        try:
            if original_payload["modelinputs"] is None:
                raise Exception("Model inputs are null")

            inputs = original_payload["modelinputs"]

            included_properties = [p for p in inputs]
            properties_to_scrub = []

            # Get all the inputs that are null
            for key, value in inputs.items():
                if value is None:
                    included_properties.remove(value)
                    properties_to_scrub.append(key)
                    del inputs[key]

            # Remove any properties have a value of a default value
            for model_input in model.model_inputs:
                input_value = inputs.get(model_input.name)

                if model_input.default_value is not None and model_input.name in inputs and ("" if input_value is None else json.dumps(input_value)) == "":
                    included_properties.remove(model_input.name)
                    properties_to_scrub.append(model_input.name)

            model_inputs = [item.name for item in model.model_inputs if item.is_required]
            missing_inputs = [item for item in model_inputs if item not in included_properties]

            if len(missing_inputs) > 0:
                missing_text = ','.join(missing_inputs)
                validation_info = f"Invalid payload, all required inputs not set.  {missing_text}"

                raise Exception(validation_info)

            # Get the defaulted optional inputs
            defaulted_optional_inputs = CalculationHelper.get_defaulted_optional_inputs_json(model.model_inputs, inputs)

            # Add the defaulted optional attributes to the inputs
            for val in defaulted_optional_inputs:
                name_key = val.Name.lower()

                inputs[name_key] = val.Value

            # Get a distinct list of the inputs

            calculation_inputs_to_return_in_output = set(original_payload["includeinresponse"])

            for key, value in inputs.items():
                if key in calculation_inputs_to_return_in_output or model.debug_mode:
                    json_output[key] = value

            log_information.calculation_inputs = inputs

            # perform_calculations(log_information, request_client_id, client_id, inputs,)
            calculation_output = {"modelId": model.id, "quoteLines": [{"itemNumber": "000010", "recommendedPricePerPound": "9.801"}]}

            json_output = json_output | calculation_output

            log_information.calculation_outputs = json_output
        except SymbolNotFoundError as ex:
            # telemetry track exception
            log_information.error_message = ex

            # if calculation_id != None and not _disable_logging
            # log the log information

            raise
        except Exception as ex:
            # telemetry track exception
            log_information.error_message = ex

            # if calculation_id != None and not _disable_logging
            # log the log information

            raise

        # if calculation_id != None and not _disable_logging
        # log the log information

        return json_output
