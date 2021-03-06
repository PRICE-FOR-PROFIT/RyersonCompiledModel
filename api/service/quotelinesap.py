import datetime
import math
from datetime import date
from typing import Any
from uuid import uuid4
import json

from dateutil.relativedelta import relativedelta
from requests.structures import CaseInsensitiveDict

from api.exceptions.argumentnullerror import ArgumentNullError
from api.exceptions.breakerror import BreakError
from api.exceptions.dividebyzeroerror import DivideByZeroError
from api.exceptions.symbolnotfounderror import SymbolNotFoundError
from api.model.calculationoutput import CalculationOutputModel
from api.model.loginformation import LogInformationModel
from api.model.southskidcharge import SouthSkidChargeModel
from api.schema.costadjustment import CostAdjustmentSchema
from api.schema.product import ProductSchema
from api.schema.milltoplantfreight import MillToPlantFreightSchema
from api.schema.ido import IdoSchema
from api.schema.tmadjustment import TmAdjustmentSchema
from api.schema.clcode import ClCodeSchema
from api.schema.materialsalesoffice import MaterialSalesOfficeSchema
from api.schema.packagingcost import PackagingCostSchema
from api.schema.southskidcharge import SouthSkidChargeSchema
from api.schema.sapfreight import SapFreightSchema
from api.schema.southfreight import SouthFreightSchema
from api.schema.freight import FreightSchema
from api.schema.freightdefault import FreightDefaultSchema
from api.schema.sobwfloorprice import SoBwFloorPriceSchema
from api.schema.bwrating import BwRatingSchema
from api.schema.locationgroup import LocationGroupSchema
from api.service.calculationhelper import CalculationHelper
from api.schema.automatedtuning import AutomatedTuningSchema
from api.service.interfaces.calcengineinterface import CalcEngineInterface
from api.model.model import ModelModel
from api.service.interfaces.lookupserviceinterface import LookupServiceInterface
from api.service.interfaces.queuedloggerinterface import QueuedLoggerInterface
from api.service.miscoperations import MiscOperations
from config import Config


class QuoteLineSap(CalcEngineInterface):
    def __init__(self, lookup_service: LookupServiceInterface, queued_logger: QueuedLoggerInterface, configuration: Config):
        self._lookup_service = lookup_service
        self._config = configuration
        self._disable_logging = configuration.disable_Logging
        self._namespace = configuration.namespace
        self._base_calculation_endpoint = configuration.base_calculation_endpoint
        self._fan_out = eval(configuration.fan_out)
        self._queued_logger = queued_logger

    @staticmethod
    def calculate_recommended_price_per_pound_for_weight_class(rc_mapping: str, multi_market: str, weight_class: float, cust_price_weight_class: float, non_mat_cost_weight_class: float, cust_service_percent_adder: float, cust_service_dollar_adder: float, floor_price: float, automated_tuning_magnitude: float, bw_rating_adder: float, price_adjustment: float) -> str:
        if rc_mapping.casefold() == "SOUTH".casefold() and weight_class <= 500.0:
            a = 25.0
        else:
            if multi_market.casefold() == "NORTHEAST".casefold() and weight_class <= 1000:
                a = 15.0
            else:
                if rc_mapping.casefold() != "SOUTH".casefold() and multi_market.casefold() != "NORTHEAST" and weight_class <= 500.0:
                    a = 50.0
                else:
                    a = 0.0

        return str(round(((max(round(((((cust_price_weight_class + non_mat_cost_weight_class)) + (a) / weight_class) * (1 + cust_service_percent_adder)) + (cust_service_dollar_adder / weight_class), 4), floor_price) * (1.0 + automated_tuning_magnitude) * (1.0 + bw_rating_adder)) + price_adjustment), 4))

    @staticmethod
    def calculate_order_cost_for_weight_class(unit_handling_cost: float, waive_skid: str, packaging_cost_per_pound: float, sap_ind: str, south_skid_charge_info: SouthSkidChargeModel, south_skid_charge_weight: float, south_skid_charge: float, stocking_cost_per_pound: float, weight_class: float) -> float:
        if waive_skid.casefold() == "N".casefold():
            if sap_ind.casefold() == "Y".casefold():
                a = packaging_cost_per_pound
            else:
                a = (math.ceil(weight_class / south_skid_charge_weight) if south_skid_charge_info is not None else 0.0) * south_skid_charge / 1.0
        else:
            a = 0.0

        return unit_handling_cost / weight_class + a + stocking_cost_per_pound

    @staticmethod
    def calculate_non_mat_cost_for_weight_class(order_cost_weight_class: float, freight_escalation_level: str, freight_info_charge: float, default_freight_charge: float, base_raw_freight_charge: float, minimum_freight_charge: float, weight_class: float) -> float:
        if freight_escalation_level.casefold() == "Level1".casefold():
            freight_charge = freight_info_charge
        elif freight_escalation_level.casefold() == "Level2".casefold():
            freight_charge = default_freight_charge
        else:
            freight_charge = base_raw_freight_charge

        return order_cost_weight_class + max(freight_charge / 100.0, minimum_freight_charge / weight_class) + max(15 / weight_class, 0.01)

    def perform_calculations(self, log_information: LogInformationModel, inputs: CaseInsensitiveDict[str, Any], client_id: str, debug_mode: bool) -> dict[str, Any]:
        outputs = list()
        intermediate_calcs = dict()
        error_message = "Valid price generated."

        try:
            net_weight_of_sales_item = float(inputs.get("netweightofsalesitem"))
            intermediate_calcs["netWeightOfSalesItem"] = net_weight_of_sales_item

            weight = float(inputs.get("weight"))
            intermediate_calcs["weight"] = weight

            bundles = int(inputs.get("bundles"))
            intermediate_calcs["bundles"] = bundles

            customer_id = inputs.get("customerid")
            intermediate_calcs["customerId"] = customer_id

            material = inputs.get("material")
            intermediate_calcs["material"] = material

            ship_plant = inputs.get("shipplant")
            intermediate_calcs["shipPlant"] = ship_plant

            stock_plant = inputs.get("stockplant")
            intermediate_calcs["stockPlant"] = stock_plant

            independent_calculation_flag = bool(inputs.get("independentcalculationflag"))
            intermediate_calcs["independentCalculationFlag"] = independent_calculation_flag

            ship_to_state = inputs.get("shiptostate")
            intermediate_calcs["shipToState"] = ship_to_state

            ship_to_zip_code = inputs.get("shiptozipcode")
            intermediate_calcs["shipToZipCode"] = ship_to_zip_code

            op_code = inputs.get("opcode")
            intermediate_calcs["opCode"] = op_code

            sap_ind = inputs.get("sapind")

            net_weight_per_finished_piece = float(inputs.get("netweightperfinishedpiece"))
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
            intermediate_calcs["productKey"] = product_key

            product_info = self._lookup_service.lookup_product(client_id, "products", product_key, None)
            if product_info is not None:
                intermediate_calcs["productInfo"] = ProductSchema().dump(product_info)

            cost_adjustment_lookup_key = f"{material}|{stock_plant}"
            intermediate_calcs["costAdjustmentTestLookupKey"] = cost_adjustment_lookup_key

            cost_adjustment_test_info = self._lookup_service.lookup_cost_adjustment(client_id, "cost_adjustment_test_materials", cost_adjustment_lookup_key, None)
            if cost_adjustment_test_info is not None:
                intermediate_calcs["costAdjustmentTestInfo"] = CostAdjustmentSchema().dump(cost_adjustment_test_info)

            material_classification = "STD" if cost_adjustment_test_info is None or cost_adjustment_test_info.material_classification == "" else cost_adjustment_test_info.material_classification
            intermediate_calcs["materialClassification"] = material_classification

            cost_plus = material_classification.casefold() == "cpl".casefold()

            if product_info is None and not cost_plus:
                raise BreakError("Material not found.")

            bell_wether_material = inputs.get("material") if cost_plus else product_info.bellwether_material
            intermediate_calcs["bellWetherMaterial"] = bell_wether_material

            if bell_wether_material.casefold() == "na".casefold():
                raise BreakError("bellWetherMaterial not found.")

            bell_wether_base_cost = cost_adjustment_test_info.cost if cost_plus else product_info.bellwether_base_cost
            intermediate_calcs["bellwetherBaseCost"] = bell_wether_base_cost

            index = material_classification.upper() if cost_plus else product_info.index
            intermediate_calcs["index"] = index

            if index == "":
                raise BreakError("Index not found.")

            exchange_rate_info = None

            if cost_plus:
                exchange_rate_info = self._lookup_service.lookup_exchange_rate(client_id, "products", inputs.get("rcmapping"), None)

                if exchange_rate_info is not None:
                    intermediate_calcs["exchangeRateInfo"] = ProductSchema().dump(exchange_rate_info)

                exchange_rate = exchange_rate_info.exchange_rate if exchange_rate_info is not None else 0.0
            else:
                exchange_rate = product_info.exchange_rate if product_info is not None else 0.0

            if exchange_rate == 0.0:
                raise BreakError("exchangeRate not found.")

            intermediate_calcs["exchangeRate"] = exchange_rate

            material_description = cost_adjustment_test_info.material_description if cost_plus else product_info.material_description
            intermediate_calcs["materialDescription"] = material_description

            product = cost_adjustment_test_info.product.upper() if cost_plus else product_info.product_name.upper()
            intermediate_calcs["product"] = product

            form = cost_adjustment_test_info.form.upper() if cost_plus else product_info.form.upper()
            intermediate_calcs["form"] = form

            market_movement_adder = 0.0 if cost_plus else product_info.market_movement_adder
            intermediate_calcs["marketMovementAdder"] = market_movement_adder

            percent_adjustment = 1.0 if cost_plus else product_info.percent_adjustment
            intermediate_calcs["percentAdjustment"] = percent_adjustment

            dollar_adjustment = 0.0 if cost_plus else product_info.dollar_adjustment
            intermediate_calcs["dollarAdjustment"] = dollar_adjustment

            modeled_cost_raw = cost_adjustment_test_info.cost if cost_plus else product_info.modeled_cost
            intermediate_calcs["modeledCostRaw"] = modeled_cost_raw

            cost_adjustment_salt_value = "IE_COST_ADJUSTMENT_TEST"
            intermediate_calcs["costAdjustmentSaltValue"] = cost_adjustment_salt_value

            cost_adjustment_hash_fields = "CustomerId" + "|" + "isrOffice" + "|" + "material" + "|" + "costAdjustmentSaltValue"
            intermediate_calcs["costAdjustmentHashFields"] = cost_adjustment_hash_fields

            cost_adjustment_hash_values = f"{customer_id}|{inputs.get('isroffice')}|{inputs.get('material')}|{cost_adjustment_salt_value}"
            intermediate_calcs["costAdjustmentHashValues"] = cost_adjustment_hash_values

            cost_adj_partition_value = MiscOperations.get_partition_value(cost_adjustment_hash_values)
            intermediate_calcs["costAdjPartitionValue"] = cost_adj_partition_value

            cost_adjustment_test_group_num = int(math.ceil(cost_adj_partition_value/(1.0/7.0)))
            intermediate_calcs["costAdjustmentTestGroupNum"] = cost_adjustment_test_group_num

            test_groups = ["A", "B", "C", "D", "E", "F", "G"]

            cost_adjustment_test_group = test_groups[cost_adjustment_test_group_num - 1]
            intermediate_calcs["costAdjustmentTestGroup"] = cost_adjustment_test_group

            test_group_percentages = [0.0, 0.05, -0.05, 0.10, -0.10, 0.20, -0.20]

            cost_adjustment_percent_raw = test_group_percentages[cost_adjustment_test_group_num - 1]
            intermediate_calcs["costAdjustmentPercentRaw"] = cost_adjustment_percent_raw

            cost_adjustment_percent = cost_adjustment_percent_raw if (cost_plus or material_classification.casefold() == "lm".casefold()) and 25 <= float(inputs.get("weight")) <= 5000 and not is_test_customer else 0.00
            intermediate_calcs["costAdjustmentPercent"] = cost_adjustment_percent

            modeled_cost = modeled_cost_raw * (1 + cost_adjustment_percent)
            intermediate_calcs["modeledCost"] = modeled_cost

            if modeled_cost == 0.0:
                raise BreakError("Modeled cost not found.")

            replacement_cost = modeled_cost / 100
            intermediate_calcs["replacementCost"] = replacement_cost

            mtp_key = f"{bell_wether_material}|{ship_plant}"
            intermediate_calcs["mtpKey"] = mtp_key

            mtp_ship_plant_info = self._lookup_service.lookup_mill_to_plant_freight(client_id, "mill_to_plant_freights", mtp_key, None)
            if mtp_ship_plant_info is not None:
                intermediate_calcs["mtpShipPlantInfo"] = MillToPlantFreightSchema().dump(mtp_ship_plant_info)

            mill_to_plant_freight = 0.0 if mtp_ship_plant_info is None else mtp_ship_plant_info.mill_to_plant_freight_value
            intermediate_calcs["millToPlantFreight"] = mill_to_plant_freight

            replacement_cost_with_mtp = replacement_cost + mill_to_plant_freight
            intermediate_calcs["replacementCostWithMTP"] = replacement_cost_with_mtp

            ido_key = f"{stock_plant}|{ship_plant}"
            intermediate_calcs["idoKey"] = ido_key

            ido_info = self._lookup_service.lookup_ido(client_id, "ido_lookup", ido_key, None)
            if ido_info is not None:
                intermediate_calcs["idoInfo"] = IdoSchema().dump(ido_info)

            ido_per_pound = 0 if ido_info is None else ido_info.ido_per_pound / 100
            intermediate_calcs["idoPerPound"] = ido_per_pound

            ido_min = 0.00 if ido_info is None else ido_info.ido_min
            intermediate_calcs["idoMin"] = ido_min

            ido_max = 10000.0 if ido_info is None else ido_info.ido_max
            intermediate_calcs["idoMax"] = ido_max

            ido_per_pound_min_constrained = ido_min / weight if ido_per_pound * weight < ido_min else ido_per_pound
            intermediate_calcs["idoPerPoundMinConstrained"] = ido_per_pound_min_constrained

            ido_per_pound_max_constrained = ido_max / weight if ido_per_pound_min_constrained * weight > ido_max else ido_per_pound_min_constrained
            intermediate_calcs["idoPerPoundMaxConstrained"] = ido_per_pound_max_constrained

            calculation_quote_pounds = weight if independent_calculation_flag else inputs.get("totalquotepounds")
            intermediate_calcs["calculationQuotePounds"] = calculation_quote_pounds

            weight_class = str(self._lookup_service.bucketed_lookup(client_id, "weight_class", calculation_quote_pounds, "totalquotepounds"))
            intermediate_calcs["weightClass"] = weight_class

            target_margin_key = f"{inputs.get('isroffice')}|{bell_wether_material}"
            intermediate_calcs["targetMarginKey"] = target_margin_key

            base_target_margin_raw = self._lookup_service.lookup_target_margin(client_id, "target_margin_lookups", target_margin_key, None)
            intermediate_calcs["baseTargetMarginRaw"] = base_target_margin_raw

            base_target_margin = base_target_margin_raw if not cost_plus else 0.0 if cost_adjustment_test_info is None else cost_adjustment_test_info.target_margin
            intermediate_calcs["baseTargetMargin"] = base_target_margin

            if base_target_margin == 0:
                raise BreakError("baseTargetMargin not found.")

            target_margin_adjustment_key = f"{inputs.get('multimarket')}|{product}|{form}"
            intermediate_calcs["targetMarginAdjustmentKey"] = target_margin_adjustment_key

            target_margin_adjustment_info = self._lookup_service.lookup_tm_adjustment(client_id, "tm_adjustments", target_margin_adjustment_key, None)
            if target_margin_adjustment_info is not None:
                intermediate_calcs["targetMarginAdjustmentInfo"] = TmAdjustmentSchema().dump(target_margin_adjustment_info)

            if target_margin_adjustment_info is None:
                raise BreakError(f"Target margin adjustment '{target_margin_adjustment_key}' not found.")

            target_margin_adjustment_weight_classes = {
                "1": target_margin_adjustment_info.weight_class_1,
                "200": target_margin_adjustment_info.weight_class_200,
                "500": target_margin_adjustment_info.weight_class_500,
                "1000": target_margin_adjustment_info.weight_class_1000,
                "2000": target_margin_adjustment_info.weight_class_2000,
                "5000": target_margin_adjustment_info.weight_class_5000,
                "6500": target_margin_adjustment_info.weight_class_6500,
                "10000": target_margin_adjustment_info.weight_class_10000,
                "20000": target_margin_adjustment_info.weight_class_20000,
                "24000": target_margin_adjustment_info.weight_class_24000,
                "40000": target_margin_adjustment_info.weight_class_40000
            }

            target_margin_adjustment = target_margin_adjustment_weight_classes.get(weight_class, 0.0)
            intermediate_calcs["targetMarginAdjustment"] = target_margin_adjustment

            raw_target_margin = round(base_target_margin + target_margin_adjustment, 4)
            intermediate_calcs["rawTargetMargin"] = raw_target_margin

            target_margin = max(min(raw_target_margin, 0.85), -0.20)
            intermediate_calcs["targetMargin"] = target_margin

            base_price_per_pound = (replacement_cost_with_mtp / (1 - target_margin)) + ido_per_pound_max_constrained
            intermediate_calcs["basePricePerPound"] = base_price_per_pound

            cl_code_key = f"{customer_id}|{inputs.get('customersalesoffice')}|{product}|{form}"
            intermediate_calcs["clCodeKey"] = cl_code_key

            cl_code_info = self._lookup_service.lookup_cl_code(client_id, "cl_codes", cl_code_key, None)
            if cl_code_info is not None:
                intermediate_calcs["clCodeInfo"] = ClCodeSchema().dump(cl_code_info)

            cl_code = "2" if is_test_customer else "3" if cl_code_info is None or cl_code_info.cl_code_value == "" else cl_code_info.cl_code_value
            intermediate_calcs["clCode"] = cl_code

            if is_test_customer:
                cl_discount = 0.0
            elif cl_code_info is not None:
                cl_discount = cl_code_info.cl_discount
            else:
                cl_discount = 0.05 if inputs.get("sapind").casefold() == "N".casefold() else 0.03

            intermediate_calcs["clDiscount"] = cl_discount

            customer_price_per_pound = base_price_per_pound * (1 + cl_discount + inputs.get("dsoadder"))
            intermediate_calcs["customerPricePerPound"] = customer_price_per_pound

            cust_price_weight_class_1 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_1, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass1"] = cust_price_weight_class_1

            cust_price_weight_class_200 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_200, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass200"] = cust_price_weight_class_200

            cust_price_weight_class_500 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_500, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass500"] = cust_price_weight_class_500

            cust_price_weight_class_1000 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_1000, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass1000"] = cust_price_weight_class_1000

            cust_price_weight_class_2000 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_2000, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass2000"] = cust_price_weight_class_2000

            cust_price_weight_class_5000 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_5000, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass5000"] = cust_price_weight_class_5000

            cust_price_weight_class_6500 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_6500, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass6500"] = cust_price_weight_class_6500

            cust_price_weight_class_10000 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_10000, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass10000"] = cust_price_weight_class_10000

            cust_price_weight_class_20000 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_20000, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass20000"] = cust_price_weight_class_20000

            cust_price_weight_class_24000 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_24000, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass24000"] = cust_price_weight_class_24000

            cust_price_weight_class_40000 = (replacement_cost_with_mtp / (1 - round(max(min(base_target_margin + target_margin_adjustment_info.weight_class_40000, 0.98), -0.20), 4)) + ido_per_pound_max_constrained) * (1 + cl_discount)
            intermediate_calcs["custPriceWeightClass40000"] = cust_price_weight_class_40000

            ogh_ship_plant = "9999" if inputs.get("rcmapping").casefold() == "SOUTH_SAP".casefold() else ship_plant
            intermediate_calcs["oghShipPlant"] = ogh_ship_plant

            overhead_group_key = f"{material.upper()}|{ogh_ship_plant}"
            intermediate_calcs["overheadGroupKey"] = overhead_group_key

            material_sales_office_key = f"{material.upper()}|{inputs.get('isroffice')}"
            intermediate_calcs["materialSalesOfficeKey"] = material_sales_office_key

            material_sales_office_lookup_items = self._lookup_service.lookup_material_sales_office(client_id, "MaterialSalesOfficeLookups", material_sales_office_key, None)
            if material_sales_office_lookup_items is not None:
                intermediate_calcs["materialSalesOfficeLookupItems"] = MaterialSalesOfficeSchema().dump(material_sales_office_lookup_items)

            price_adjustment_value = 0 if material_sales_office_lookup_items is None else material_sales_office_lookup_items.price_adjustment
            intermediate_calcs["priceAdjustmentValue"] = price_adjustment_value

            red_margin_threshold = 0.35 if material_sales_office_lookup_items is None else material_sales_office_lookup_items.red_margin_threshold
            intermediate_calcs["redMarginThreshold"] = red_margin_threshold

            yellow_margin_threshold = 0.85 if material_sales_office_lookup_items is None else material_sales_office_lookup_items.yellow_margin_threshold
            intermediate_calcs["yellowMarginThreshold"] = yellow_margin_threshold

            start_effective_date = datetime.datetime.now() + relativedelta(years=1) if material_sales_office_lookup_items is None else material_sales_office_lookup_items.start_effective_date
            intermediate_calcs["startEffectiveDate"] = start_effective_date

            end_effective_date = datetime.datetime.now() + relativedelta(years=1) if material_sales_office_lookup_items is None else material_sales_office_lookup_items.end_effective_date
            intermediate_calcs["endEffectiveDate"] = end_effective_date

            price_adjustment = price_adjustment_value if start_effective_date <= datetime.datetime.now() <= end_effective_date else 0.0
            intermediate_calcs["priceAdjustment"] = price_adjustment

            packaging_cost_info = None if sap_ind.casefold() == "N".casefold() else self._lookup_service.lookup_packaging_cost(client_id, "packaging_cost_lookups", overhead_group_key, None)
            if packaging_cost_info is not None:
                intermediate_calcs["packagingCostInfo"] = PackagingCostSchema().dump(packaging_cost_info)

            packaging_cost_info_final = product_info if packaging_cost_info is None else packaging_cost_info
            if packaging_cost_info_final is not None:
                intermediate_calcs["packagingCostInfoFinal"] = PackagingCostSchema().dump(packaging_cost_info_final)

            unit_handling_cost = packaging_cost_info_final.unit_handling_cost if sap_ind.casefold() == "Y".casefold() and packaging_cost_info_final is not None else 0.0
            intermediate_calcs["unitHandlingCost"] = unit_handling_cost

            handling_cost_per_pound = unit_handling_cost / (weight / adjusted_bundles)
            intermediate_calcs["handlingCostPerPound"] = handling_cost_per_pound

            handling_cost_per_pound_wc = unit_handling_cost / 2000.0
            intermediate_calcs["handlingCostPerPoundWC"] = handling_cost_per_pound_wc

            total_tons = weight / 2000.0
            intermediate_calcs["totalTons"] = total_tons

            product_form_key = f"{product}|{form}"
            intermediate_calcs["productFormKey"] = product_form_key

            south_skid_charge_info = self._lookup_service.lookup_south_skid_charge(client_id, "south_skid_charge_lookup", product_form_key, None) if sap_ind.casefold() == "N".casefold() else None
            if south_skid_charge_info is not None:
                intermediate_calcs["southSkidChargeInfo"] = SouthSkidChargeSchema().dump(south_skid_charge_info)

            south_skid_charge_weight = south_skid_charge_info.weight_per_skid if sap_ind.casefold() == "N".casefold() and south_skid_charge_info is not None else 0.0
            intermediate_calcs["southSkidChargeWeight"] = south_skid_charge_weight

            south_skid_charge = south_skid_charge_info.skid_charge if sap_ind.casefold() == "N".casefold() and south_skid_charge_info is not None else 0.0
            intermediate_calcs["southSkidCharge"] = south_skid_charge

            per_ton_packaging_cost = packaging_cost_info_final.per_ton_packaging_cost if sap_ind.casefold() == "Y".casefold() and packaging_cost_info_final is not None else 0.0
            intermediate_calcs["perTonPackagingCost"] = per_ton_packaging_cost

            waive_skid = inputs.get("waiveskid")
            intermediate_calcs["waiveSkid"] = waive_skid

            if waive_skid.casefold() == "N".casefold():
                if sap_ind.casefold() == "Y".casefold():
                    packaging_cost_per_pound = per_ton_packaging_cost / 2000.0
                else:
                    packaging_cost_per_pound = ((math.ceil(weight / south_skid_charge_weight) if south_skid_charge_info is not None else 0.0) * south_skid_charge) / weight
            else:
                packaging_cost_per_pound = 0.0

            intermediate_calcs["packagingCostPerPound"] = packaging_cost_per_pound

            per_ton_stocking_cost = packaging_cost_info_final.per_ton_stocking_cost if sap_ind.casefold() == "Y".casefold() and packaging_cost_info_final is not None else 0.0
            intermediate_calcs["perTonStockingCost"] = per_ton_stocking_cost

            stocking_cost_per_pound = round(per_ton_stocking_cost / 2000.0, 4)
            intermediate_calcs["stockingCostPerPound"] = stocking_cost_per_pound

            order_cost_per_pound = handling_cost_per_pound + packaging_cost_per_pound + stocking_cost_per_pound
            intermediate_calcs["orderCostPerPound"] = order_cost_per_pound

            order_cost_per_pound_wc = handling_cost_per_pound_wc + packaging_cost_per_pound + stocking_cost_per_pound
            intermediate_calcs["orderCostPerPoundWC"] = order_cost_per_pound_wc

            order_cost_weight_class_1 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 1.0)
            intermediate_calcs["orderCostWeightClass1"] = order_cost_weight_class_1

            order_cost_weight_class_200 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 200.0)
            intermediate_calcs["orderCostWeightClass200"] = order_cost_weight_class_200

            order_cost_weight_class_500 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 500.0)
            intermediate_calcs["orderCostWeightClass500"] = order_cost_weight_class_500

            order_cost_weight_class_1000 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 1000.0)
            intermediate_calcs["orderCostWeightClass1000"] = order_cost_weight_class_1000

            order_cost_weight_class_2000 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 2000.0)
            intermediate_calcs["orderCostWeightClass2000"] = order_cost_weight_class_2000

            order_cost_weight_class_5000 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 5000.0)
            intermediate_calcs["orderCostWeightClass5000"] = order_cost_weight_class_5000

            order_cost_weight_class_6500 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 6500.0)
            intermediate_calcs["orderCostWeightClass6500"] = order_cost_weight_class_6500

            order_cost_weight_class_10000 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 10000.0)
            intermediate_calcs["orderCostWeightClass10000"] = order_cost_weight_class_10000

            order_cost_weight_class_20000 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 20000.0)
            intermediate_calcs["orderCostWeightClass20000"] = order_cost_weight_class_20000

            order_cost_weight_class_24000 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 24000.0)
            intermediate_calcs["orderCostWeightClass24000"] = order_cost_weight_class_24000

            order_cost_weight_class_40000 = self.calculate_order_cost_for_weight_class(unit_handling_cost, waive_skid, packaging_cost_per_pound, sap_ind, south_skid_charge_info, south_skid_charge_weight, south_skid_charge, stocking_cost_per_pound, 40000.0)
            intermediate_calcs["orderCostWeightClass40000"] = order_cost_weight_class_40000

            sap_freight_key = f"{ship_plant}|{ship_to_zip_code}"
            intermediate_calcs["sapFreightKey"] = sap_freight_key

            sap_freight_info = self._lookup_service.lookup_sap_freight(client_id, "sap_freight_lookups", sap_freight_key, None) if sap_ind.casefold() == "Y".casefold() else None
            if sap_freight_info is not None:
                intermediate_calcs["sapFreightInfo"] = SapFreightSchema().dump(sap_freight_info)

            ship_zone_key = f"{customer_id}|{ship_plant}"
            intermediate_calcs["shipZoneKey"] = ship_zone_key

            ship_zone_info = self._lookup_service.lookup_ship_zone(client_id, "ship_zone_lookups", ship_zone_key, None) if sap_ind.casefold() == "N".casefold() else None
            if ship_zone_info is not None:
                    intermediate_calcs["shipZoneInfo"] = ship_zone_info

            zone = "" if sap_ind.casefold() == "Y".casefold() else ship_zone_info.zone if ship_zone_info is not None else "3"
            intermediate_calcs["zone"] = zone

            as400_freight_key = f"{ship_plant}|{zone}"
            intermediate_calcs["as400FreightKey"] = as400_freight_key

            as400_freight_info = self._lookup_service.lookup_south_freight(client_id, "south_freight_lookups", as400_freight_key, None) if sap_ind.casefold() == "N".casefold() else None
            if as400_freight_info is not None:
                intermediate_calcs["as400FreightInfo"] = SouthFreightSchema().dump(as400_freight_info)

            freight_info = as400_freight_info if sap_freight_info is None else sap_freight_info
            if freight_info is not None:
                intermediate_calcs["freightInfo"] = FreightSchema().dump(freight_info)

            freight_defaults_key = f"{ship_plant}|{ship_to_state}"
            intermediate_calcs["freightDefaultsKey"] = freight_defaults_key

            freight_defaults_info = None if freight_info is not None else self._lookup_service.lookup_freight_default(client_id, "freight_defaults", freight_defaults_key, None) if sap_ind.casefold() == "Y".casefold() else None
            if freight_defaults_info is not None:
                intermediate_calcs["freightDefaultsInfo"] = FreightDefaultSchema().dump(freight_defaults_info)

            freight_escalation_level = "Level1" if freight_info is not None else "Level3" if freight_defaults_info is None else "Level2"
            intermediate_calcs["freightEscalationLevel"] = freight_escalation_level

            minimum_freight_charge = freight_info.minimum_freight_charge if freight_escalation_level == "Level1" else freight_defaults_info.default_minimum_freight_charge if freight_escalation_level == "Level2" else 50.0
            intermediate_calcs["minimumFreightCharge"] = minimum_freight_charge

            base_raw_freight_charge = 1.8

            if freight_escalation_level == "Level1":
                if weight_class == "0":
                    raw_freight_charge = freight_info.weight_class_0
                elif weight_class == "1":
                    raw_freight_charge = freight_info.weight_class_1
                elif weight_class == "200":
                    raw_freight_charge = freight_info.weight_class_200
                elif weight_class == "500":
                    raw_freight_charge = freight_info.weight_class_500
                elif weight_class == "1000":
                    raw_freight_charge = freight_info.weight_class_1000
                elif weight_class == "2000":
                    raw_freight_charge = freight_info.weight_class_2000
                elif weight_class == "5000":
                    raw_freight_charge = freight_info.weight_class_5000
                elif weight_class == "6500":
                    raw_freight_charge = freight_info.weight_class_6500
                elif weight_class == "10000":
                    raw_freight_charge = freight_info.weight_class_10000
                elif weight_class == "20000":
                    raw_freight_charge = freight_info.weight_class_20000
                elif weight_class == "24000":
                    raw_freight_charge = freight_info.weight_class_24000
                elif weight_class == "40000":
                    raw_freight_charge = freight_info.weight_class_40000
                else:
                    raw_freight_charge = base_raw_freight_charge

                raw_freight_charge = raw_freight_charge / 100.0
            elif freight_escalation_level == "Level2":
                raw_freight_charge = freight_defaults_info.default_freight_charge_per_100_pounds / 100.0
            else:
                raw_freight_charge = base_raw_freight_charge / 100.0

            intermediate_calcs["rawFreightCharge"] = raw_freight_charge

            freight_charge_per_pound = max(raw_freight_charge, minimum_freight_charge / calculation_quote_pounds)
            intermediate_calcs["freightChargePerPound"] = freight_charge_per_pound

            labor_cost_per_pound = max(15.0 / weight, 0.01)
            intermediate_calcs["laborCostPerPound"] = labor_cost_per_pound

            total_non_material_cost = order_cost_per_pound + freight_charge_per_pound + labor_cost_per_pound
            intermediate_calcs["totalNonMaterialCost"] = total_non_material_cost

            non_mat_cost_weight_class_1 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_1, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_1, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 1.0)
            intermediate_calcs["nonMatCostWeightClass1"] = non_mat_cost_weight_class_1

            non_mat_cost_weight_class_200 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_200, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_200, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 200.0)
            intermediate_calcs["nonMatCostWeightClass200"] = non_mat_cost_weight_class_200

            non_mat_cost_weight_class_500 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_500, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_500, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 500.0)
            intermediate_calcs["nonMatCostWeightClass500"] = non_mat_cost_weight_class_500

            non_mat_cost_weight_class_1000 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_1000, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_1000, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 1000.0)
            intermediate_calcs["nonMatCostWeightClass1000"] = non_mat_cost_weight_class_1000

            non_mat_cost_weight_class_2000 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_2000, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_2000, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 2000.0)
            intermediate_calcs["nonMatCostWeightClass2000"] = non_mat_cost_weight_class_2000

            non_mat_cost_weight_class_5000 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_5000, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_5000, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 5000.0)
            intermediate_calcs["nonMatCostWeightClass5000"] = non_mat_cost_weight_class_5000

            non_mat_cost_weight_class_6500 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_6500, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_6500, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 6500.0)
            intermediate_calcs["nonMatCostWeightClass6500"] = non_mat_cost_weight_class_6500

            non_mat_cost_weight_class_10000 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_10000, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_10000, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 10000.0)
            intermediate_calcs["nonMatCostWeightClass10000"] = non_mat_cost_weight_class_10000

            non_mat_cost_weight_class_20000 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_20000, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_20000, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 20000.0)
            intermediate_calcs["nonMatCostWeightClass20000"] = non_mat_cost_weight_class_20000

            non_mat_cost_weight_class_24000 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_24000, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_24000, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 24000.0)
            intermediate_calcs["nonMatCostWeightClass24000"] = non_mat_cost_weight_class_24000

            non_mat_cost_weight_class_40000 = self.calculate_non_mat_cost_for_weight_class(order_cost_weight_class_40000, freight_escalation_level, 0.0 if freight_info is None else freight_info.weight_class_40000, 0.0 if freight_defaults_info is None else freight_defaults_info.default_freight_charge_per_100_pounds, base_raw_freight_charge, minimum_freight_charge, 40000.0)
            intermediate_calcs["nonMatCostWeightClass40000"] = non_mat_cost_weight_class_40000

            total_cost_per_pound = round(replacement_cost_with_mtp + total_non_material_cost, 4)
            intermediate_calcs["totalCostPerPound"] = total_cost_per_pound

            if inputs.get("rcmapping").casefold() == "SOUTH".casefold() and calculation_quote_pounds <= 500.0:
                small_order_adder = 25.0 / calculation_quote_pounds
            else:
                if inputs.get("multimarket").casefold() == "NORTHEAST" and calculation_quote_pounds <= 1000.0:
                    small_order_adder = 15.0 / calculation_quote_pounds
                else:
                    if inputs.get("rcmapping").casefold() != "SOUTH" and inputs.get("multimarket").casefold() != "NORTHEAST" and calculation_quote_pounds <= 500:
                        small_order_adder = 50.0 / calculation_quote_pounds
                    else:
                        small_order_adder = 0.0

            intermediate_calcs["smallOrderAdder"] = small_order_adder

            rec_price_pp_with_order_adder = round(customer_price_per_pound + total_non_material_cost + small_order_adder, 4)
            intermediate_calcs["recPricePPWithOrderAdder"] = rec_price_pp_with_order_adder

            cust_service_dollar_adder = inputs.get("dollaradder")
            intermediate_calcs["custServiceDollarAdder"] = cust_service_dollar_adder

            cust_service_dollar_adder_pp = cust_service_dollar_adder / weight
            intermediate_calcs["custServiceDollarAdderPP"] = cust_service_dollar_adder_pp

            cust_service_percent_adder = inputs.get("percentadder")
            intermediate_calcs["custServicePercentAdder"] = cust_service_percent_adder

            rec_price_pp_cust_service_adder = round(rec_price_pp_with_order_adder * (1 + cust_service_percent_adder) + cust_service_dollar_adder_pp, 4)
            intermediate_calcs["recPricePPCustServiceAdder"] = rec_price_pp_cust_service_adder

            floor_price_key = f"{inputs.get('isroffice')}|{bell_wether_material}"
            intermediate_calcs["floorPriceKey"] = floor_price_key

            floor_price_info = self._lookup_service.lookup_so_bw_floor_price(client_id, "so_bw_floor_price_lookup", floor_price_key, None)
            if floor_price_info is not None:
                intermediate_calcs["floorPriceInfo"] = SoBwFloorPriceSchema().dump(floor_price_info)

            floor_price = floor_price_info.floor_price if floor_price_info is not None else 0.0
            intermediate_calcs["floorPrice"] = floor_price

            rec_price_pp_with_price_floor = max(rec_price_pp_cust_service_adder, floor_price)
            intermediate_calcs["recPricePPWithPriceFloor"] = rec_price_pp_with_price_floor

            bw_rating_key = f"{inputs.get('multimarket')}|{bell_wether_material}"
            intermediate_calcs["bwRatingKey"] = bw_rating_key

            bw_rating_info = self._lookup_service.lookup_bw_rating(client_id, "bw_rating_lookup", bw_rating_key, None)
            if bw_rating_info is not None:
                intermediate_calcs["bwRatingInfo"] = BwRatingSchema().dump(bw_rating_info)

            bw_rating = bw_rating_info.bw_rating_value if bw_rating_info is not None else "EXCLUDED"
            intermediate_calcs["bwRating"] = bw_rating

            bw_rating_adder = bw_rating_info.bw_ratting_adder if bw_rating_info is not None else 0.0
            intermediate_calcs["bwRatingAdder"] = bw_rating_adder

            rec_price_pp_with_bw_rating_adder = rec_price_pp_with_price_floor * (1 + bw_rating_adder)
            intermediate_calcs["recommendedPricePerPoundValue"] = rec_price_pp_with_bw_rating_adder

            location_group_lookup_key = inputs.get("rcmapping").upper()
            intermediate_calcs["locationGroupLookupKey"] = location_group_lookup_key

            location_group_info = self._lookup_service.lookup_location_group(client_id, "location_group_lookup", location_group_lookup_key, None)
            if location_group_info is not None:
                intermediate_calcs["locationGroupInfo"] = LocationGroupSchema().dump(location_group_info)

            location_group = location_group_info.location_group_value if location_group_info is not None else "UNKNOWN"
            intermediate_calcs["locationGroup"] = location_group

            condensed_form = "FR" if form.casefold() == "FLAT".casefold() or form.casefold() == "FLAT".casefold() else form
            intermediate_calcs["condensedForm"] = condensed_form

            automated_tuning_lookup_key = f"{location_group}|{product}|{condensed_form}"
            intermediate_calcs["automatedTuningLookupKey"] = automated_tuning_lookup_key

            automated_tuning_info = self._lookup_service.lookup_automated_tuning(client_id, "automated_tuning_lookup", automated_tuning_lookup_key, None)
            if automated_tuning_info is not None:
                intermediate_calcs["automatedTuningInfo"] = AutomatedTuningSchema().dump(automated_tuning_info)

            salt_value = automated_tuning_info.salt_value if automated_tuning_info is not None else "UNKNOWN"
            intermediate_calcs["saltValue"] = salt_value

            price_up_active_flag = automated_tuning_info.price_up_active_flag if automated_tuning_info is not None else "FALSE"
            intermediate_calcs["priceUpActiveFlag"] = price_up_active_flag

            price_up_measurement_level = automated_tuning_info.price_up_measurement_level if automated_tuning_info is not None else ""
            intermediate_calcs["priceUpMeasurementLevel"] = price_up_measurement_level

            price_up_concentration = automated_tuning_info.price_up_concentration if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceUpConcentration"] = price_up_concentration

            price_up_magnitude = automated_tuning_info.price_up_magnitude if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceUpMagnitude"] = price_up_magnitude

            price_up_realization = automated_tuning_info.price_up_realization if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceUpRealization"] = price_up_realization

            price_up_win_rate_diff = automated_tuning_info.price_up_min_win_rate_diff if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceUpMinWinRateDiff"] = price_up_win_rate_diff

            price_up_sig_level = automated_tuning_info.price_up_sig_level if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceUpSigLevel"] = price_up_sig_level

            price_up_power = automated_tuning_info.price_up_power if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceUpPower"] = price_up_power

            price_up_obs_req = automated_tuning_info.price_up_obs_req if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceUpObsReq"] = price_up_obs_req

            price_down_active_flag = automated_tuning_info.price_down_active_flag if automated_tuning_info is not None else "FALSE"
            intermediate_calcs["priceDownActiveFlag"] = price_down_active_flag

            price_down_measurement_level = automated_tuning_info.price_down_measurement_level if automated_tuning_info is not None else ""
            intermediate_calcs["priceDownMeasurementLevel"] = price_down_measurement_level

            price_down_concentration = automated_tuning_info.price_down_concentration if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceDownConcentration"] = price_down_concentration

            price_down_magnitude = automated_tuning_info.price_down_magnitude if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceDownMagnitude"] = price_down_magnitude

            price_down_realization = automated_tuning_info.price_down_realization if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceDownRealization"] = price_down_realization

            price_down_win_rate_diff = automated_tuning_info.price_down_min_win_rate_diff if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceDownMinWinRateDiff"] = price_down_win_rate_diff

            price_down_sig_level = automated_tuning_info.price_down_sig_level if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceDownSigLevel"] = price_down_sig_level

            price_down_power = automated_tuning_info.price_down_power if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceDownPower"] = price_down_power

            price_down_obs_req = automated_tuning_info.price_down_obs_req if automated_tuning_info is not None else 0.0
            intermediate_calcs["priceDownObsReq"] = price_down_obs_req

            monday_date = (datetime.datetime.today() + relativedelta(days=-(datetime.datetime.today().weekday())) if datetime.datetime.today().weekday() != 0 else datetime.datetime.now()).strftime("%Y-%m-%d")
            intermediate_calcs["mondayDate"] = monday_date

            automated_tuning_hash_values = f"{customer_id}|{inputs.get('isroffice')}|{bell_wether_material}|{monday_date}|{salt_value}"
            intermediate_calcs["automatedTuningHashValues"] = automated_tuning_hash_values

            partition_value = MiscOperations.get_partition_value(automated_tuning_hash_values)
            intermediate_calcs["partitionValue"] = partition_value

            control_group_concentration = 1 - (price_up_concentration + price_down_concentration)
            intermediate_calcs["controlGroupConcentration"] = control_group_concentration

            automated_tuning_test_group_raw = "A" if partition_value <= control_group_concentration else "B" if partition_value <= control_group_concentration + price_up_concentration else "C"
            intermediate_calcs["automatedTuningTestGroupRaw"] = automated_tuning_test_group_raw

            automated_tuning_test_group = inputs.get("automatedtuninggroupoverride") if inputs.get("automatedtuninggroupoverride") != "" else "A" if is_test_customer else automated_tuning_test_group_raw
            intermediate_calcs["automatedTuningTestGroup"] = automated_tuning_test_group

            price_up_active_flag_final = price_up_active_flag if inputs.get("automatedtuninggroupoverride") == "" else inputs.get("automatedtuninggroupoverride").upper()
            intermediate_calcs["priceUpActiveFlagFinal"] = price_up_active_flag_final

            price_down_active_flag_final = price_down_active_flag if inputs.get("automatedtuninggroupoverride") == "" else inputs.get("automatedtuninggroupoverride").upper()
            intermediate_calcs["priceDownActiveFlagFinal"] = price_down_active_flag_final

            price_up_magnitude_with_flag = price_up_magnitude if price_up_active_flag_final.casefold() == "TRUE".casefold() else 0.0
            intermediate_calcs["priceUpMagnitudeWithFlag"] = price_up_magnitude_with_flag

            price_down_magnitude_with_flag = price_down_magnitude if price_down_active_flag_final.casefold() == "TRUE".casefold() else 0.0
            intermediate_calcs["priceDownMagnitudeWithFlag"] = price_down_magnitude_with_flag

            automated_tuning_magnitude = 0.0 if automated_tuning_test_group == "A" else price_up_magnitude_with_flag if automated_tuning_test_group == "B" else price_up_magnitude_with_flag
            intermediate_calcs["automatedTuningMagnitude"] = automated_tuning_magnitude

            rec_price_with_automated_tuning = rec_price_pp_with_bw_rating_adder * (1 + automated_tuning_magnitude)
            intermediate_calcs["recPriceWithAutomatedTuning"] = rec_price_with_automated_tuning

            recommended_price_per_pound_value = round(rec_price_with_automated_tuning + price_adjustment, 4)
            intermediate_calcs["recommendedPricePerPoundValue"] = recommended_price_per_pound_value

            recommended_price_per_pound = str(recommended_price_per_pound_value)
            intermediate_calcs["recommendedPricePerPound"] = recommended_price_per_pound

            rec_price_wc_1 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 1.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC1"] = rec_price_wc_1

            rec_price_wc_200 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 200.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC200"] = rec_price_wc_200

            rec_price_wc_500 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 500.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC500"] = rec_price_wc_500

            rec_price_wc_1000 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 1000.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC1000"] = rec_price_wc_1000

            rec_price_wc_2000 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 2000.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC2000"] = rec_price_wc_2000

            rec_price_wc_5000 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 5000.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC5000"] = rec_price_wc_5000

            rec_price_wc_6500 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 6500.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC6500"] = rec_price_wc_6500

            rec_price_wc_10000 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 10000.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC10000"] = rec_price_wc_10000

            rec_price_wc_20000 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 20000.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC20000"] = rec_price_wc_20000

            rec_price_wc_24000 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 24000.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC24000"] = rec_price_wc_24000

            rec_price_wc_40000 = self.calculate_recommended_price_per_pound_for_weight_class(inputs.get("rcmapping"), inputs.get("multimarket"), 40000.0, cust_price_weight_class_200, non_mat_cost_weight_class_200, cust_service_percent_adder, cust_service_dollar_adder, floor_price, automated_tuning_magnitude, bw_rating_adder, price_adjustment)
            intermediate_calcs["recPriceWC40000"] = rec_price_wc_40000

            margin = recommended_price_per_pound_value - total_cost_per_pound
            intermediate_calcs["margin"] = margin

            margin_percent = margin / recommended_price_per_pound_value
            intermediate_calcs["marginPercent"] = margin_percent

            outputs.append(CalculationOutputModel("recommendedPricePerPound", False, recommended_price_per_pound))
            outputs.append(CalculationOutputModel("totalCostPerPound", False, total_cost_per_pound))
            outputs.append(CalculationOutputModel("redMarginThreshold", False, red_margin_threshold))
            outputs.append(CalculationOutputModel("yellowMarginThreshold", False, yellow_margin_threshold))
            outputs.append(CalculationOutputModel("exchangeRate", False, exchange_rate))
            outputs.append(CalculationOutputModel("freightChargePerPound", False, freight_charge_per_pound))
            outputs.append(CalculationOutputModel("recPriceWC1", False, rec_price_wc_1))
            outputs.append(CalculationOutputModel("recPriceWC200", False, rec_price_wc_200))
            outputs.append(CalculationOutputModel("recPriceWC500", False, rec_price_wc_500))
            outputs.append(CalculationOutputModel("recPriceWC1000", False, rec_price_wc_1000))
            outputs.append(CalculationOutputModel("recPriceWC2000", False, rec_price_wc_2000))
            outputs.append(CalculationOutputModel("recPriceWC5000", False, rec_price_wc_5000))
            outputs.append(CalculationOutputModel("recPriceWC6500", False, rec_price_wc_6500))
            outputs.append(CalculationOutputModel("recPriceWC10000", False, rec_price_wc_10000))
            outputs.append(CalculationOutputModel("recPriceWC20000", False, rec_price_wc_20000))
            outputs.append(CalculationOutputModel("recPriceWC24000", False, rec_price_wc_24000))
            outputs.append(CalculationOutputModel("recPriceWC40000", False, rec_price_wc_40000))
            outputs.append(CalculationOutputModel("itemNumber", False, inputs.get("itemnumber")))

            if debug_mode:
                outputs.append(CalculationOutputModel("adjustedNetWeightOfSalesItem", False, adjusted_net_weight_of_sales_item))
                outputs.append(CalculationOutputModel("adjustedBundles", False, adjusted_bundles))
                outputs.append(CalculationOutputModel("productInfo", False, ProductSchema().dump(product_info)))
                outputs.append(CalculationOutputModel("costAdjustmentTestLookupKey", False, cost_adjustment_lookup_key))
                outputs.append(CalculationOutputModel("costAdjustmentTestInfo", False, CostAdjustmentSchema().dump(cost_adjustment_test_info)))
                outputs.append(CalculationOutputModel("materialClassification", False, material_classification))
                outputs.append(CalculationOutputModel("rcMapping", False, inputs.get("rcmapping")))
                outputs.append(CalculationOutputModel("multiMarket", False, inputs.get("multimarket")))
                outputs.append(CalculationOutputModel("customerSalesOffice", False, inputs.get("customersalesoffice")))
                outputs.append(CalculationOutputModel("sapInd", False, sap_ind))
                outputs.append(CalculationOutputModel("isrOffice", False, inputs.get("isroffice")))
                outputs.append(CalculationOutputModel("dsoadder", False, inputs.get("dsoadder")))
                outputs.append(CalculationOutputModel("productKey", False, product_key))
                outputs.append(CalculationOutputModel("bellWetherMaterial", False, bell_wether_material))
                outputs.append(CalculationOutputModel("bellwetherBaseCost", False, bell_wether_base_cost))
                outputs.append(CalculationOutputModel("index", False, index))
                outputs.append(CalculationOutputModel("exchangeRateInfo", False, ProductSchema().dump(exchange_rate_info)))
                outputs.append(CalculationOutputModel("product", False, product))
                outputs.append(CalculationOutputModel("form", False, form))
                outputs.append(CalculationOutputModel("marketMovementAdder", False, market_movement_adder))
                outputs.append(CalculationOutputModel("percentAdjustment", False, percent_adjustment))
                outputs.append(CalculationOutputModel("dollarAdjustment", False, dollar_adjustment))
                outputs.append(CalculationOutputModel("modeledCostRaw", False, modeled_cost_raw))
                outputs.append(CalculationOutputModel("costAdjustmentSaltValue", False, cost_adjustment_salt_value))
                outputs.append(CalculationOutputModel("costAdjustmentHashFields", False, cost_adjustment_hash_fields))
                outputs.append(CalculationOutputModel("costAdjustmentHashValues", False, cost_adjustment_hash_values))
                outputs.append(CalculationOutputModel("costAdjPartitionValue", False, cost_adj_partition_value))
                outputs.append(CalculationOutputModel("costAdjustmentTestGroupNum", False, cost_adjustment_test_group_num))
                outputs.append(CalculationOutputModel("costAdjustmentTestGroup", False, cost_adjustment_test_group))
                outputs.append(CalculationOutputModel("costAdjustmentPercentRaw", False, cost_adjustment_percent_raw))
                outputs.append(CalculationOutputModel("costAdjustmentPercent", False, cost_adjustment_percent))
                outputs.append(CalculationOutputModel("modeledCost", False, modeled_cost))
                outputs.append(CalculationOutputModel("replacementCost", False, replacement_cost))
                outputs.append(CalculationOutputModel("mtpKey", False, mtp_key))
                outputs.append(CalculationOutputModel("millToPlantFreight", False, mill_to_plant_freight))
                outputs.append(CalculationOutputModel("replacementCostWithMTP", False, replacement_cost_with_mtp))
                outputs.append(CalculationOutputModel("idoKey", False, ido_key))
                outputs.append(CalculationOutputModel("idoPerPound", False, ido_per_pound))
                outputs.append(CalculationOutputModel("idoMin", False, ido_min))
                outputs.append(CalculationOutputModel("idoMax", False, ido_max))
                outputs.append(CalculationOutputModel("idoPerPoundMinConstrained", False, ido_per_pound_min_constrained))
                outputs.append(CalculationOutputModel("idoPerPoundMaxConstrained", False, ido_per_pound_max_constrained))
                outputs.append(CalculationOutputModel("calculationQuotePounds", False, calculation_quote_pounds))
                outputs.append(CalculationOutputModel("weightClass", False, weight_class))
                outputs.append(CalculationOutputModel("targetMarginKey", False, target_margin_key))
                outputs.append(CalculationOutputModel("baseTargetMarginRaw", False, base_target_margin_raw))
                outputs.append(CalculationOutputModel("baseTargetMargin", False, base_target_margin))
                outputs.append(CalculationOutputModel("targetMarginAdjustmentKey", False, target_margin_adjustment_key))
                outputs.append(CalculationOutputModel("targetMarginAdjustment", False, target_margin_adjustment))
                outputs.append(CalculationOutputModel("rawTargetMargin", False, raw_target_margin))
                outputs.append(CalculationOutputModel("targetMargin", False, target_margin))
                outputs.append(CalculationOutputModel("basePricePerPound", False, base_price_per_pound))
                outputs.append(CalculationOutputModel("clCodeKey", False, cl_code_key))
                outputs.append(CalculationOutputModel("clCode", False, cl_code))
                outputs.append(CalculationOutputModel("clDiscount", False, cl_discount))
                outputs.append(CalculationOutputModel("customerPricePerPound", False, customer_price_per_pound))
                outputs.append(CalculationOutputModel("custPriceWeightClass1", False, cust_price_weight_class_1))
                outputs.append(CalculationOutputModel("custPriceWeightClass200", False, cust_price_weight_class_200))
                outputs.append(CalculationOutputModel("custPriceWeightClass500", False, cust_price_weight_class_500))
                outputs.append(CalculationOutputModel("custPriceWeightClass1000", False, cust_price_weight_class_1000))
                outputs.append(CalculationOutputModel("custPriceWeightClass2000", False, cust_price_weight_class_2000))
                outputs.append(CalculationOutputModel("custPriceWeightClass5000", False, cust_price_weight_class_5000))
                outputs.append(CalculationOutputModel("custPriceWeightClass6500", False, cust_price_weight_class_6500))
                outputs.append(CalculationOutputModel("custPriceWeightClass10000", False, cust_price_weight_class_10000))
                outputs.append(CalculationOutputModel("custPriceWeightClass20000", False, cust_price_weight_class_20000))
                outputs.append(CalculationOutputModel("custPriceWeightClass24000", False, cust_price_weight_class_24000))
                outputs.append(CalculationOutputModel("custPriceWeightClass40000", False, cust_price_weight_class_40000))
                outputs.append(CalculationOutputModel("oghShipPlan", False, ogh_ship_plant))
                outputs.append(CalculationOutputModel("overheadGroupKey", False, overhead_group_key))
                outputs.append(CalculationOutputModel("materialSalesOfficeKey", False, material_sales_office_key))
                outputs.append(CalculationOutputModel("priceAdjustmentValue", False, price_adjustment_value))
                outputs.append(CalculationOutputModel("priceAdjustment", False, price_adjustment))
                outputs.append(CalculationOutputModel("totalTons", False, total_tons))
                outputs.append(CalculationOutputModel("sapFreightKey", False, sap_freight_key))
                outputs.append(CalculationOutputModel("shipZoneKey", False, ship_zone_key))
                outputs.append(CalculationOutputModel("zone", False, zone))
                outputs.append(CalculationOutputModel("as400FreightKey", False, as400_freight_key))
                outputs.append(CalculationOutputModel("freightDefaultsKey", False, freight_defaults_key))
                outputs.append(CalculationOutputModel("freightEscalationLevel", False, freight_escalation_level))
                outputs.append(CalculationOutputModel("minimumFreightCharge", False, minimum_freight_charge))
                outputs.append(CalculationOutputModel("rawFreightCharge", False, raw_freight_charge))
                outputs.append(CalculationOutputModel("freightChargePerPound ", False, freight_charge_per_pound))
                outputs.append(CalculationOutputModel("laborCostPerPound", False, labor_cost_per_pound))
                outputs.append(CalculationOutputModel("smallOrderAdder", False, small_order_adder))
                outputs.append(CalculationOutputModel("floorPriceKey", False, floor_price_key))
                outputs.append(CalculationOutputModel("floorPrice", False, floor_price))
                outputs.append(CalculationOutputModel("bwRatingKey", False, bw_rating_key))
                outputs.append(CalculationOutputModel("bwRating", False, bw_rating))
                outputs.append(CalculationOutputModel("bwRatingAdder", False, bw_rating_adder))
                outputs.append(CalculationOutputModel("unitHandlingCost", False, unit_handling_cost))
                outputs.append(CalculationOutputModel("handlingCostPerPound", False, handling_cost_per_pound))
                outputs.append(CalculationOutputModel("handlingCostPerPoundWC", False, handling_cost_per_pound_wc))
                outputs.append(CalculationOutputModel("perTonPackagingCost", False, per_ton_packaging_cost))
                outputs.append(CalculationOutputModel("packagingCostPerPound", False, packaging_cost_per_pound))
                outputs.append(CalculationOutputModel("perTonStockingCost", False, per_ton_stocking_cost))
                outputs.append(CalculationOutputModel("stockingCostPerPound", False, stocking_cost_per_pound))
                outputs.append(CalculationOutputModel("orderCostPerPound", False, order_cost_per_pound))
                outputs.append(CalculationOutputModel("orderCostPerPoundWC", False, order_cost_per_pound_wc))
                outputs.append(CalculationOutputModel("orderCostWeightClass1", False, order_cost_weight_class_1))
                outputs.append(CalculationOutputModel("orderCostWeightClass200", False, order_cost_weight_class_200))
                outputs.append(CalculationOutputModel("orderCostWeightClass500", False, order_cost_weight_class_500))
                outputs.append(CalculationOutputModel("orderCostWeightClass1000", False, order_cost_weight_class_1000))
                outputs.append(CalculationOutputModel("orderCostWeightClass2000", False, order_cost_weight_class_2000))
                outputs.append(CalculationOutputModel("orderCostWeightClass5000", False, order_cost_weight_class_5000))
                outputs.append(CalculationOutputModel("orderCostWeightClass6500", False, order_cost_weight_class_6500))
                outputs.append(CalculationOutputModel("orderCostWeightClass10000", False, order_cost_weight_class_10000))
                outputs.append(CalculationOutputModel("orderCostWeightClass20000", False, order_cost_weight_class_20000))
                outputs.append(CalculationOutputModel("orderCostWeightClass24000", False, order_cost_weight_class_24000))
                outputs.append(CalculationOutputModel("orderCostWeightClass40000", False, order_cost_weight_class_40000))
                outputs.append(CalculationOutputModel("totalNonMaterialCost", False, total_non_material_cost))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass1", False, non_mat_cost_weight_class_1))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass200", False, non_mat_cost_weight_class_200))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass500", False, non_mat_cost_weight_class_500))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass1000", False, non_mat_cost_weight_class_1000))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass2000", False, non_mat_cost_weight_class_2000))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass5000", False, non_mat_cost_weight_class_5000))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass6500", False, non_mat_cost_weight_class_6500))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass10000", False, non_mat_cost_weight_class_10000))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass20000", False, non_mat_cost_weight_class_20000))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass24000", False, non_mat_cost_weight_class_24000))
                outputs.append(CalculationOutputModel("nonMatCostWeightClass40000", False, non_mat_cost_weight_class_40000))
                outputs.append(CalculationOutputModel("recPricePPWithOrderAdder", False, rec_price_pp_with_order_adder))
                outputs.append(CalculationOutputModel("custServiceDollarAdder", False, cust_service_dollar_adder))
                outputs.append(CalculationOutputModel("custServiceDollarAdderPP", False, cust_service_dollar_adder_pp))
                outputs.append(CalculationOutputModel("custServicePercentAdder", False, cust_service_percent_adder))
                outputs.append(CalculationOutputModel("recPricePPCustServiceAdder", False, rec_price_pp_cust_service_adder))
                outputs.append(CalculationOutputModel("recPricePPWithPriceFloor", False, rec_price_pp_with_price_floor))
                outputs.append(CalculationOutputModel("recPricePPWithBwRatingAdder", False, rec_price_pp_with_bw_rating_adder))
                outputs.append(CalculationOutputModel("condensedForm", False, condensed_form))
                outputs.append(CalculationOutputModel("automatedTuningLookupKey", False, automated_tuning_lookup_key))
                outputs.append(CalculationOutputModel("automatedTuningInfo", False, AutomatedTuningSchema().dump(automated_tuning_info)))
                outputs.append(CalculationOutputModel("locationGroupLookupKey", False, location_group_lookup_key))
                outputs.append(CalculationOutputModel("locationGroupInfo", False, LocationGroupSchema().dump(location_group_info)))
                outputs.append(CalculationOutputModel("locationGroup", False, location_group))
                outputs.append(CalculationOutputModel("saltValue", False, salt_value))
                outputs.append(CalculationOutputModel("priceUpActiveFlag", False, price_up_active_flag))
                outputs.append(CalculationOutputModel("priceUpMeasurementLevel", False, price_up_measurement_level))
                outputs.append(CalculationOutputModel("priceUpConcentration", False, price_up_concentration))
                outputs.append(CalculationOutputModel("priceUpMagnitude", False, price_up_magnitude))
                outputs.append(CalculationOutputModel("priceUpRealization", False, price_up_realization))
                outputs.append(CalculationOutputModel("priceUpMinWinRateDiff", False, price_up_win_rate_diff))
                outputs.append(CalculationOutputModel("priceUpSigLevel", False, price_up_sig_level))
                outputs.append(CalculationOutputModel("priceUpPower", False, price_up_power))
                outputs.append(CalculationOutputModel("priceUpObsReq", False, price_up_obs_req))
                outputs.append(CalculationOutputModel("priceDownActiveFlag", False, price_down_active_flag))
                outputs.append(CalculationOutputModel("priceDownMeasurementLevel", False, price_down_measurement_level))
                outputs.append(CalculationOutputModel("priceDownConcentration", False, price_down_concentration))
                outputs.append(CalculationOutputModel("priceDownMagnitude", False, price_down_magnitude))
                outputs.append(CalculationOutputModel("priceDownRealization", False, price_down_realization))
                outputs.append(CalculationOutputModel("priceDownMinWinRateDiff", False, price_down_win_rate_diff))
                outputs.append(CalculationOutputModel("priceDownSigLevel", False, price_down_sig_level))
                outputs.append(CalculationOutputModel("priceDownPower", False, price_down_power))
                outputs.append(CalculationOutputModel("priceDownObsReq", False, price_down_obs_req))
                outputs.append(CalculationOutputModel("mondayDate", False, monday_date))
                outputs.append(CalculationOutputModel("automatedTuningHashValues", False, automated_tuning_hash_values))
                outputs.append(CalculationOutputModel("partitionValue", False, partition_value))
                outputs.append(CalculationOutputModel("controlGroupConcentration", False, control_group_concentration))
                outputs.append(CalculationOutputModel("automatedTuningTestGroupRaw", False, automated_tuning_test_group_raw))
                outputs.append(CalculationOutputModel("automatedTuningTestGroup", False, automated_tuning_test_group))
                outputs.append(CalculationOutputModel("priceUpActiveFlagFinal", False, price_up_active_flag_final))
                outputs.append(CalculationOutputModel("priceDownActiveFlagFinal", False, price_down_active_flag_final))
                outputs.append(CalculationOutputModel("priceUpMagnitudeWithFlag", False, price_up_magnitude_with_flag))
                outputs.append(CalculationOutputModel("priceDownMagnitudeWithFlag", False, price_down_magnitude_with_flag))
                outputs.append(CalculationOutputModel("automatedTuningMagnitude", False, automated_tuning_magnitude))
                outputs.append(CalculationOutputModel("recPriceWithAutomatedTuning", False, rec_price_with_automated_tuning))
                outputs.append(CalculationOutputModel("recommendedPricePerPoundValue", False, recommended_price_per_pound_value))
                outputs.append(CalculationOutputModel("margin", False, margin))
                outputs.append(CalculationOutputModel("marginPercent", False, margin_percent))
                outputs.append(CalculationOutputModel("material", False, material))
                outputs.append(CalculationOutputModel("shipPlant", False, ship_plant))
                outputs.append(CalculationOutputModel("stockPlant", False, stock_plant))
                outputs.append(CalculationOutputModel("weight", False, weight))
                outputs.append(CalculationOutputModel("netWeightOfSalesItem", False, net_weight_of_sales_item))
                outputs.append(CalculationOutputModel("opCode", False, op_code))
                outputs.append(CalculationOutputModel("netWeightPerFinishedPiece", False, net_weight_per_finished_piece))
                outputs.append(CalculationOutputModel("bundles", False, bundles))
                outputs.append(CalculationOutputModel("customerid", False, customer_id))
                outputs.append(CalculationOutputModel("isrname", False, isr_name))
                outputs.append(CalculationOutputModel("isTestCustomer", False, is_test_customer))
                outputs.append(CalculationOutputModel("shiptostate", False, ship_to_state))
                outputs.append(CalculationOutputModel("shiptozipcode", False, ship_to_zip_code))
                outputs.append(CalculationOutputModel("independentcalculationflag", False, independent_calculation_flag))
                outputs.append(CalculationOutputModel("totalQuotePounds", False, inputs.get("totalquotepounds")))
                outputs.append(CalculationOutputModel("southSkidChargeWeight", False, south_skid_charge_weight))
                outputs.append(CalculationOutputModel("southSkidCharge ", False, south_skid_charge))
                outputs.append(CalculationOutputModel("materialDescription ", False, material_description))
        except BreakError as ex:
            # Track exception
            error_message = str(ex)
            log_information.intermediate_calculations = intermediate_calcs
        except ArgumentNullError as ex:
            log_information.intermediate_calculations = intermediate_calcs

            raise Exception(f"Error evaluating the function : {str(ex)}")
        except DivideByZeroError as ex:
            log_information.intermediate_calculations = intermediate_calcs

            raise Exception(f"Error evaluating the function : {str(ex)}")
        except Exception as ex:
            log_information.intermediate_calculations = intermediate_calcs

            raise

        outputs.append(CalculationOutputModel("errorMessage", False, error_message))

        json_output = dict()

        for value in outputs:
            json_output[value.Name] = value.Value

        return json_output

    def execute_model(self, request_client_id: str, client_id: str, model: ModelModel, original_payload: CaseInsensitiveDict[str, Any], calculation_id: str, token: str) -> dict[str, Any]:
        json_output = {}

        log_information = LogInformationModel()

        log_information.id = uuid4()
        log_information.create_date = datetime.datetime.now()
        log_information.calculation_id = calculation_id
        log_information.model_id = model.id
        log_information.client_id = client_id
        log_information.authorization_id = request_client_id
        log_information.model_version = model.version
        log_information.original_payload = json.dumps(dict(original_payload))

        try:
            if original_payload["modelinputs"] is None:
                raise Exception("Model inputs are null")

            inputs = CaseInsensitiveDict(original_payload["modelinputs"])

            included_properties = [p for p in inputs]
            properties_to_scrub = []

            inputs_copy = inputs.copy()

            # Get all the inputs that are null
            for key, value in inputs_copy.items():
                if value is None:
                    included_properties.remove(key)
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
                name_key = val.Name

                inputs[name_key] = val.Value

            # Get a distinct list of the inputs

            if original_payload.get("includeinresponse") is None:
                calculation_inputs_to_return_in_output = list()
            else:
                calculation_inputs_to_return_in_output = set(original_payload.get("includeinresponse"))

            for key, value in inputs.items():
                if key in calculation_inputs_to_return_in_output or model.debug_mode:
                    json_output[key] = value

            log_information.calculation_inputs = dict(inputs)

            calculation_output = self.perform_calculations(log_information, inputs, client_id, model.debug_mode)

            json_output = json_output | calculation_output

            log_information.calculation_outputs = json_output
        except SymbolNotFoundError as ex:
            # telemetry track exception
            log_information.error_message = ex

            if calculation_id != "" and not self._disable_logging:
                self._queued_logger.log_information(log_information)

            raise
        except Exception as ex:
            # telemetry track exception
            log_information.error_message = ex

            if calculation_id != "" and not self._disable_logging:
                self._queued_logger.log_information(log_information)

            raise

        if calculation_id != "" and not self._disable_logging:
            self._queued_logger.log_information(log_information)

        return json_output
