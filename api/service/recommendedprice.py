import datetime
import json
from typing import Any
from uuid import uuid4

from api.exceptions.argumentnullerror import ArgumentNullError
from api.exceptions.breakerror import BreakError
from api.exceptions.dividebyzeroerror import DivideByZeroError
from api.service.calculationhelper import CalculationHelper
from api.service.modelservice import ModelService
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

    def perform_calculations(self, log_information: LogInformationModel, request_client_id: str, client_id: str, inputs: dict, calculation_inputs_to_return_in_output: set, calculation_id: str, debug_mode: bool, original_payload: dict, token: str) -> dict[str, Any]:
        error_message = "errorMessage"
        calculation_results = {}
        intermediate_calcs = {}
        json_output = {}

        columns_to_return = ["quoteLines"]

        try:
            model_service = ModelService()

            total_quote_pounds = sum(map(lambda ql: float(ql["weight"]), inputs["quotelines"]))

            customer_id = inputs.get('customerid')
            sales_office = inputs.get('salesoffice')

            customer_with_office_key = f"{customer_id}|{sales_office}"

            customer_with_office_info = None if sales_office == "NA" else self._lookup_service.lookup_customer(client_id, "customers", customer_with_office_key, None)

            customer_without_office_info = self._lookup_service.get_customer_without_office(customer_id) if sales_office == "NA" else None

            default_office_info = self._lookup_service.get_default_office(sales_office) if customer_with_office_info is None and customer_without_office_info is None else None

            customer_info = customer_with_office_info or customer_without_office_info or default_office_info

            if customer_info is None:
                raise BreakError("Customer not found.")

            customer_name = customer_info.customer_name

            rc_mapping = customer_info.rc_mapping.upper()

            if rc_mapping == "":
                raise BreakError("rcMapping not found.")

            multi_market = customer_info.multi_market_name.upper()

            customer_sales_office = customer_info.customer_sales_office

            sap_ind = customer_info.sap_ind

            isr_office = customer_info.isr_office

            dso_adder = customer_info.dso_adder

            # Get the quote lines from the original payload
            original_quote_lines = original_payload.get("modelinputs").get("quotelines")

            if original_quote_lines is None:
                raise Exception("QuoteLines are missing from the input.")

            quote_line_input = list()

            for quote_line in original_quote_lines:
                ql = {
                    "rcMapping": rc_mapping,
                    "isrOffice": isr_office,
                    "multiMarket": multi_market,
                    "customerId": customer_id,
                    "customerName": customer_name,
                    "sapInd": sap_ind,
                    "customerSalesOffice": customer_sales_office,
                    "shipToState": inputs.get('shiptostate'),
                    "shipToZipCode": inputs.get('shiptozipcode'),
                    "isrName": inputs.get('isrname'),
                    "dsoAdder": dso_adder,
                    "waiveSkid": customer_info.waive_skid,
                    "dollarAdder": customer_info.dollar_adder,
                    "percentAdder": customer_info.percent_adder,
                    "totalQuotePounds": total_quote_pounds,
                    "IndependentCalculationFlag": inputs.get('independentcalculationflag')
                }

                quote_line_input.append(ql)

                quote_line_sap_model = model_service.get_model("quotelinesap", debug_mode)

            calculation_results = {"modelId": "bob", "quoteLines": [{"itemNumber": "000010", "recommendedPricePerPound": "9.801"}]}
        except BreakError as ex:
            # telemetry track exception

            calculation_results[error_message] = ex
        except ArgumentNullError as ex:
            # telemetry track exception

            calculation_results[error_message] = ex
        except DivideByZeroError as ex:
            # telemetry track exception

            calculation_results[error_message] = ex

        for key, value in calculation_results.items():
            column_to_return = key in columns_to_return
            return_in_output = key in calculation_inputs_to_return_in_output
            is_error_message = key == error_message

            if debug_mode or column_to_return or return_in_output or is_error_message:
                json_output[key] = value

        return json_output

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

            model_inputs = [item.name.lower() for item in model.model_inputs if item.is_required]
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

            calculation_output = self.perform_calculations(log_information, request_client_id, client_id, inputs, calculation_inputs_to_return_in_output, calculation_id, model.debug_mode, original_payload, token)
            # calculation_output = {"modelId": model.id, "quoteLines": [{"itemNumber": "000010", "recommendedPricePerPound": "9.801"}]}

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
