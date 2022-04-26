import datetime
import math
from typing import Any
from uuid import uuid4
import json

from api.exceptions.argumentnullerror import ArgumentNullError
from api.exceptions.breakerror import BreakError
from api.exceptions.dividebyzeroerror import DivideByZeroError
from api.exceptions.symbolnotfounderror import SymbolNotFoundError
from api.model.calculationoutput import CalculationOutputModel
from api.model.loginformation import LogInformationModel
from api.schema.costadjustment import CostAdjustmentSchema
from api.schema.product import ProductSchema
from api.service.calculationhelper import CalculationHelper
from api.service.interfaces.calcengineinterface import CalcEngineInterface
from api.model.model import ModelModel
from api.service.interfaces.lookupserviceinterface import LookupServiceInterface
from api.service.interfaces.queuedloggerinterface import QueuedLoggerInterface
from config import Config


class QuoteLineSap(CalcEngineInterface):
    def __init__(self, lookup_service: LookupServiceInterface, queued_logger: QueuedLoggerInterface, configuration: Config):
        self._lookup_service = lookup_service
        self._config = configuration
        self._disable_logging = configuration.disable_Logging
        self._namespace = configuration.namespace
        self._base_calculation_endpoint = configuration.base_calculation_endpoint
        self._fan_out = eval(configuration.fan_out)

    def perform_calculations(self, log_information: LogInformationModel, inputs: dict[str, Any], client_id: str, debug_mode: bool) -> dict[str, Any]:
        outputs = list()
        intermediate_calcs = dict()
        error_message = "Valid price generated."

        try:
            net_weight_of_sales_item = inputs.get("netweightofsalesitem")
            intermediate_calcs["netWeightOfSalesItem"] = net_weight_of_sales_item

            weight = inputs.get("weight")
            intermediate_calcs["weight"] = weight

            bundles = inputs.get("bundles")
            intermediate_calcs["bundles"] = bundles

            customer_id = inputs.get("customerid")
            intermediate_calcs["customerId"] = customer_id

            material = inputs.get("material")
            intermediate_calcs["material"] = material

            ship_plant = inputs.get("shipplant")
            intermediate_calcs["shipPlant"] = ship_plant

            stock_plant = inputs.get("stockplant")
            intermediate_calcs["stockPlant"] = stock_plant

            independent_calculation_flag = inputs.get("independentcalculationflag")
            intermediate_calcs["independentCalculationFlag"] = independent_calculation_flag

            ship_to_state = inputs.get("shiptostate")
            intermediate_calcs["shipToState"] = ship_to_state

            ship_to_zip_code = inputs.get("shiptozipcode")
            intermediate_calcs["shipToZipCode"] = ship_to_zip_code

            op_code = inputs.get("opcode")
            intermediate_calcs["opCode"] = op_code

            net_weight_per_finished_piece = inputs.get("netweightperfinishedpiece")
            intermediate_calcs["netWeightPerFinishedPiece"] = net_weight_per_finished_piece

            isr_name = inputs.get("isrname")
            intermediate_calcs["isrName"] = isr_name

            is_test_customer = "CL2 PRICE MASTER" in inputs.get("customername")
            intermediate_calcs["isTestCustomer"] = is_test_customer

            adjusted_net_weight_of_sales_item = weight if net_weight_of_sales_item == -1 else net_weight_of_sales_item
            intermediate_calcs["adjustedNetWeightOfSalesItem"] = adjusted_net_weight_of_sales_item

            adjusted_bundles = math.ceil(weight / 2000) if bundles == -1 else bundles
            intermediate_calcs["adjustedBundles"] = adjusted_bundles

            product_key = f"{inputs.get('rcmapping')}|{material}"
            intermediate_calcs["productKey"] = weight

            product_info = self._lookup_service.lookup_product(client_id, "products", product_key, None)
            if product_info is not None:
                intermediate_calcs["productInfo"] = ProductSchema().dump(product_info)

            cost_adjustment_lookup_key = f"{material}|{stock_plant}"
            intermediate_calcs["costAdjustmentTestLookupKey"] = cost_adjustment_lookup_key

            cost_adjustment_test_info = self._lookup_service.lookup_cost_adjustment(client_id, "cost_adjustment_test_materials", cost_adjustment_lookup_key, None)
            intermediate_calcs["costAdjustmentTestInfo"] = CostAdjustmentSchema().dump(cost_adjustment_test_info)

            material_classification = "STD" if cost_adjustment_test_info is None or cost_adjustment_test_info.material_classification == "" else cost_adjustment_test_info.material_classification
            intermediate_calcs["materialClassification"] = material_classification

            cost_plus = material_classification.casefold() == "cpl".casefold()

            if product_info is None and not cost_plus:
                raise BreakError("Material not found")

            bell_wether_material = inputs.get("material") if cost_plus else product_info.bellwether_material
            intermediate_calcs["bellWetherMaterial"] = bell_wether_material

            if bell_wether_material.casefold() == "na".casefold():
                raise BreakError("bellWetherMaterial not found.")

            bell_wether_base_cost = cost_adjustment_test_info.Cost if cost_plus else product_info.bellwether_base_cost
            intermediate_calcs["bellwetherBaseCost"] = bell_wether_base_cost

            index = material_classification.upper() if cost_plus else product_info.index
            intermediate_calcs["index"] = index

            if index == "":
                raise BreakError("Index not found.")

            if cost_plus:
                exchange_rate_info = self._lookup_service.lookup_exchange_rate(client_id, "products", inputs.get("rcmapping"), None)

            outputs.append(CalculationOutputModel("itemNumber", False, "000010"))
            outputs.append(CalculationOutputModel("recommendedPricePerPound", True, "9.801"))
        except BreakError as ex:
            # Track exception
            error_message = ex
            log_information.intermediate_calculations = intermediate_calcs
        except ArgumentNullError as ex:
            log_information.intermediate_calculations = intermediate_calcs

            raise Exception(f"Error evaluating the function : ex")
        except DivideByZeroError as ex:
            log_information.intermediate_calculations = intermediate_calcs

            raise Exception(f"Error evaluating the function : ex")
        except Exception as ex:
            log_information.intermediate_calculations = intermediate_calcs

            raise

        outputs.append(CalculationOutputModel("errorMessage", False, error_message))

        json_output = dict()

        for value in outputs:
            json_output[value.Name] = value.Value

        return json_output

    def execute_model(self, request_client_id: str, client_id: str, model: ModelModel, original_payload: dict[str, Any], calculation_id: str, token: str) -> dict[str, Any]:

        # a = self._lookup_service.lookup_customer(client_id, "customers", "0000000000|T09", None)
        # c = self._lookup_service.lookup_packaging_cost(client_id, "packaging_cost_lookups", "99GB100000", None)
        # d = self._lookup_service.lookup_tm_adjustment(client_id, "tm_adjustments", "CAL-MEX|ALUMINUM|FLAT", None)
        # e = self._lookup_service.lookup_mill_to_plant_freight(client_id, "mill_to_plant_freights", "160000885|1004", None)
        # f = self._lookup_service.lookup_material_sales_office(client_id, "MaterialSalesOfficeLookups", "160006249|3030", None)
        # g = self._lookup_service.lookup_sap_freight(client_id, "sap_freight_lookups", "1001|131", None)
        # h = self._lookup_service.lookup_south_skid_charge(client_id, "south_skid_charge_lookup", "STAINLESS|PLATE", None)
        # i = self._lookup_service.lookup_op_code("ABM", 100.0, 10.0)
        # j = self._lookup_service.lookup_south_freight(client_id, "south_freight_lookups", "2001|1", None)
        # k = self._lookup_service.lookup_ship_zone(client_id, "ship_zone_lookups", "0000000000|2031", None)
        # l = self._lookup_service.lookup_so_bw_floor_price(client_id, "so_bw_floor_price_lookup", "1004|100018313", None)
        # m = self._lookup_service.lookup_bw_rating(client_id, "bw_rating_lookup", "CAL-MEX|160001700", None)
        # o = self._lookup_service.lookup_freight_default(client_id, "freight_defaults", "4806|WI", None)
        # p = self._lookup_service.lookup_target_margin(client_id, "target_margin_lookups", "T19|26228", None)
        # q = self._lookup_service.lookup_cl_code(client_id, "cl_codes", "0010050438|1021|STAINLESS|FLAT", None)
        # r = self._lookup_service.lookup_ido(client_id, "ido_lookup", "2000|2000", None)
        # s = self._lookup_service.get_customer_without_office("0000000003")
        # t = self._lookup_service.get_default_office("T07")
        # u = self._lookup_service.lookup_automated_tuning(client_id, "automated_tuning_lookup", "CANADA|ALUMINUM|FR", None)
        # v = self._lookup_service.lookup_location_group(client_id, "location_group_lookup", "CDNEAST", None)
        # z = self._lookup_service.bucketed_lookup(client_id, "weight_class", 300.0, "totalquotepounds")

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

            if original_payload.get("includeinresponse") is None:
                calculation_inputs_to_return_in_output = list()
            else:
                calculation_inputs_to_return_in_output = set(original_payload.get("includeinresponse"))

            for key, value in inputs.items():
                if key in calculation_inputs_to_return_in_output or model.debug_mode:
                    json_output[key] = value

            log_information.calculation_inputs = inputs

            calculation_output = self.perform_calculations(log_information, inputs, client_id, model.debug_mode)

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
