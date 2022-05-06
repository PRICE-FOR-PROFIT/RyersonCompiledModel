import sqlite3
import sys
from abc import ABC
from typing import Optional, Any

from api.model.automatedtuning import AutomatedTuningModel
from api.model.bwrating import BwRatingModel
from api.model.clcode import ClCodeModel
from api.model.costadjustment import CostAdjustmentModel
from api.model.customer import CustomerModel
from api.model.freightdefault import FreightDefaultModel
from api.model.ido import IdoModel
from api.model.locationgroup import LocationGroupModel
from api.model.materialsalesoffice import MaterialSalesOfficeModel
from api.model.milltoplantfreight import MillToPlantFreightModel
from api.model.opcode import OpCodeModel
from api.model.packagingcost import PackagingCostModel
from api.model.product import ProductModel
from api.model.sapfreight import SapFreightModel
from api.model.shipzone import ShipZoneModel
from api.model.sobwfloorprice import SoBwFloorPriceModel
from api.model.southfreight import SouthFreightModel
from api.model.southskidcharge import SouthSkidChargeModel
from api.model.tartgetmargin import TargetMarginModel
from api.model.tmadjustment import TmAdjustmentModel
from api.service.interfaces.lookupserviceinterface import LookupServiceInterface
from config import Config


def customer_from_row(row: Any) -> CustomerModel:
    customer = CustomerModel()

    customer.percent_adder = row["percentadder"]
    customer.customer_name = row["customername"]
    customer.dollar_adder = row["dollaradder"]
    customer.dso_adder = row["dsoadder"]
    customer.sap_ind = row["sapind"]
    customer.dso = row["dso"]
    customer.waive_skid = row["waive_skid"]
    customer.customer_sales_office = row["customersalesoffice"]
    customer.isr_office = row["isroffice"]
    customer.multi_market_name = row["multimarket_name"]
    customer.rc_mapping = row["rcmapping"]
    customer.customer_number = row["customernumber"]
    customer.unique_id = row["uniqueid"]

    return customer


def product_from_row(row: Any) -> ProductModel:
    product = ProductModel()

    product.bellwether_material = row["bellwethermaterial"]
    product.bellwether_base_cost = row["bellwetherbasecost"]
    product.dollar_adjustment = row["dollaradjustment"]
    product.exchangerate = row["exchangerate"]
    product.form = row["form"]
    product.index = row["index"]
    product.market_movement_adder = row["marketmovementadder"]
    product.material = row["material"]
    product.material_description = row["materialdescription"]
    product.modeled_cost = row["modeledcost"]
    product.product_name = row["product"]
    product.percent_adjustment = row["percentadjustment"]
    product.per_ton_packaging_cost = row["pertonpackagingcost"]
    product.per_ton_stocking_cost = row["pertonstockingcost"]
    product.rc_mapping = row["rcmapping"]
    product.unique_id = row["uniqueid"]
    product.unit_handling_cost = row["unithandlingcost"]

    return product


def packaging_cost_from_row(row: Any) -> PackagingCostModel:
    packaging_cost = PackagingCostModel()

    packaging_cost.overhead_group = row["overheadgroup"]
    packaging_cost.overhead_group_name = row["overheadgroupname"]
    packaging_cost.per_ton_packaging_cost = row["pertonpackagingcost"]
    packaging_cost.per_ton_stocking_cost = row["pertonstockingcost"]
    packaging_cost.unique_id = row["uniqueid"]
    packaging_cost.unit_handling_cost = row["unithandlingcost"]

    return packaging_cost


def tm_adjustment_from_row(row: Any) -> TmAdjustmentModel:
    tm_adjustment = TmAdjustmentModel()

    tm_adjustment.unique_id = row["uniqueid"]
    tm_adjustment.multi_market_name = row["multimarket_name"]
    tm_adjustment.product = row["product"]
    tm_adjustment.form = row["form"]
    tm_adjustment.weight_class_1 = row["weightclass1"]
    tm_adjustment.weight_class_200 = row["weightclass200"]
    tm_adjustment.weight_class_500 = row["weightclass500"]
    tm_adjustment.weight_class_1000 = row["weightclass1000"]
    tm_adjustment.weight_class_2000 = row["weightclass2000"]
    tm_adjustment.weight_class_5000 = row["weightclass5000"]
    tm_adjustment.weight_class_6500 = row["weightclass6500"]
    tm_adjustment.weight_class_10000 = row["weightclass10000"]
    tm_adjustment.weight_class_20000 = row["weightclass20000"]
    tm_adjustment.weight_class_24000 = row["weightclass24000"]
    tm_adjustment.weight_class_40000 = row["weightclass40000"]

    return tm_adjustment


def material_sales_office_from_row(row: Any) -> MaterialSalesOfficeModel:
    material_sales_office = MaterialSalesOfficeModel()

    material_sales_office.unique_id = row["uniqueid"]
    material_sales_office.material = row["material"]
    material_sales_office.isr_office = row["isroffice"]
    material_sales_office.start_effective_date = row["starteffectivedate"]
    material_sales_office.end_effective_date = row["endeffectivedate"]
    material_sales_office.red_margin_threshold = row["redmarginthreshold"]
    material_sales_office.yellow_margin_threshold = row["yellowmarginthreshold"]
    material_sales_office.price_adjustment = row["priceadjustment"]

    return material_sales_office


def sap_freight_from_row(row: Any) -> SapFreightModel:
    sap_freight = SapFreightModel()

    sap_freight.unique_id = row["uniqueid"]
    sap_freight.ship_plant = row["shipplant"]
    sap_freight.zip_code = row["zipcode"]
    sap_freight.weight_class_0 = row["weightclass0"]
    sap_freight.weight_class_1 = row["weightclass1"]
    sap_freight.weight_class_200 = row["weightclass200"]
    sap_freight.weight_class_500 = row["weightclass500"]
    sap_freight.weight_class_1000 = row["weightclass1000"]
    sap_freight.weight_class_2000 = row["weightclass2000"]
    sap_freight.weight_class_5000 = row["weightclass5000"]
    sap_freight.weight_class_6500 = row["weightclass6500"]
    sap_freight.weight_class_10000 = row["weightclass10000"]
    sap_freight.weight_class_20000 = row["weightclass20000"]
    sap_freight.weight_class_24000 = row["weightclass24000"]
    sap_freight.weight_class_40000 = row["weightclass40000"]
    sap_freight.minimum_freight_charge = row["minimumfreightcharge"]

    return sap_freight


def south_skid_charge_from_row(row: Any) -> SouthSkidChargeModel:
    south_skid_charge = SouthSkidChargeModel()

    south_skid_charge.unique_id = row["uniqueid"]
    south_skid_charge.product = row["product"]
    south_skid_charge.form = row["form"]
    south_skid_charge.weight_per_skid = row["weightperskid"]
    south_skid_charge.skid_charge = row["skidcharge"]

    return south_skid_charge


def op_code_from_row(row: Any) -> OpCodeModel:
    op_code = OpCodeModel()

    op_code.unique_id = row["uniqueid"]
    op_code.op_code_value = row["opcode"]
    op_code.cutting_operation = row["cuttingoperation"]
    op_code.fab_indicator = row["fabindicator"]
    op_code.net_weight_low = row["netweightlow"]
    op_code.net_weight_high = row["netweighthigh"]
    op_code.pieces_weight_low = row["pieceweightlow"]
    op_code.pieces_weight_high = row["pieceweighthigh"]
    op_code.long_base_pull_time = row["longbasepulltime"]
    op_code.op_code_type = row["opcodetype"]

    return op_code


def south_freight_from_row(row: Any) -> SouthFreightModel:
    south_freight = SouthFreightModel()

    south_freight.unique_id = row["uniqueid"]
    south_freight.ship_plant = row["shipplant"]
    south_freight.zone = row["zone"]
    south_freight.weight_class_0 = row["weightclass0"]
    south_freight.weight_class_1 = row["weightclass1"]
    south_freight.weight_class_200 = row["weightclass200"]
    south_freight.weight_class_500 = row["weightclass500"]
    south_freight.weight_class_1000 = row["weightclass1000"]
    south_freight.weight_class_2000 = row["weightclass2000"]
    south_freight.weight_class_5000 = row["weightclass5000"]
    south_freight.weight_class_6500 = row["weightclass6500"]
    south_freight.weight_class_10000 = row["weightclass10000"]
    south_freight.weight_class_20000 = row["weightclass20000"]
    south_freight.weight_class_24000 = row["weightclass24000"]
    south_freight.weight_class_40000 = row["weightclass40000"]
    south_freight.minimum_freight_charge = row["minimumfreightcharge"]

    return south_freight


def ship_zone_from_row(row: Any) -> ShipZoneModel:
    ship_zone = ShipZoneModel()

    ship_zone.unique_id = row["uniqueid"]
    ship_zone.customer_id = row["customerid"]
    ship_zone.ship_plant = row["shipplant"]
    ship_zone.zone = row["zone"]

    return ship_zone


def so_bw_floor_price_from_row(row: Any) -> SoBwFloorPriceModel:
    so_bw_floor_price = SoBwFloorPriceModel()

    so_bw_floor_price.unique_id = row["uniqueid"]
    so_bw_floor_price.isr_office = row["isroffice"]
    so_bw_floor_price.bellwether_material = row["bellwethermaterial"]
    so_bw_floor_price.floor_price = row["floorprice"]

    return so_bw_floor_price


def bw_rating_from_row(row: Any) -> BwRatingModel:
    bw_rating = BwRatingModel()

    bw_rating.unique_id = row["uniqueid"]
    bw_rating.multi_market_name = row["multimarketname"]
    bw_rating.bellwether_material = row["bellwethermaterial"]
    bw_rating.bw_rating_value = row["bwrating"]
    bw_rating.bw_ratting_adder = row["bwratingadder"]

    return bw_rating


def freight_default_from_row(row: Any) -> FreightDefaultModel:
    freight_default = FreightDefaultModel()

    freight_default.unique_id = row["uniqueid"]
    freight_default.ship_plant = row["shipplant"]
    freight_default.state = row["state"]
    freight_default.default_freight_charge_per_100_pounds = row["defaultfreightchargeper100pounds"]
    freight_default.default_minimum_freight_charge = row["defaultminimumfreightcharge"]

    return freight_default


def target_margin_from_row(row: Any) -> TargetMarginModel:
    target_margin = TargetMarginModel()

    target_margin.unique_id = row["uniqueid"]
    target_margin.isr_office = row["isroffice"]
    target_margin.bell_wether_material = row["bellwethermaterial"]
    target_margin.target_margin_value = row["targetmargin"]

    return target_margin


def cl_code_from_row(row: Any) -> ClCodeModel:
    cl_code = ClCodeModel()

    cl_code.unique_id = row["uniqueid"]
    cl_code.customer_number = row["customernumber"]
    cl_code.customer_sales_office = row["customersalesoffice"]
    cl_code.product = row["product"]
    cl_code.cl_code_value = row["clcode"]
    cl_code.form = row["form"]
    cl_code.cl_discount = row["cldiscount"]

    return cl_code


def ido_from_row(row: Any) -> IdoModel:
    ido = IdoModel()

    ido.unique_id = row["uniqueid"]
    ido.stock_plant = row["stockplant"]
    ido.ship_plant = row["shipplant"]
    ido.ido_per_pound = row["idoperpound"]
    ido.ido_max = row["idomax"]
    ido.ido_min = row["idomin"]

    return ido


def automated_tuning_from_row(row: Any) -> AutomatedTuningModel:
    automated_tuning = AutomatedTuningModel()

    automated_tuning.unique_id = row["uniqueid"]
    automated_tuning.condensed_form = row["condensedform"]
    automated_tuning.location_group = row["locationgroup"]
    automated_tuning.price_down_active_flag = row["pricedownactiveflag"]
    automated_tuning.price_down_measurement_level = row["pricedownmeasurementlevel"]
    automated_tuning.price_down_concentration = row["pricedownconcentration"]
    automated_tuning.price_down_magnitude = row["pricedownmagnitude"]
    automated_tuning.price_down_min_win_rate_diff = row["pricedownminwinratediff"]
    automated_tuning.price_down_obs_req = row["pricedownobsreq"]
    automated_tuning.price_down_power = row["pricedownpower"]
    automated_tuning.price_down_realization = row["pricedownrealization"]
    automated_tuning.price_down_sig_level = row["pricedownsiglevel"]
    automated_tuning.price_up_active_flag = row["priceupactiveflag"]
    automated_tuning.price_up_measurement_level = row["priceupmeasurementlevel"]
    automated_tuning.price_up_concentration = row["priceupconcentration"]
    automated_tuning.price_up_magnitude = row["priceupmagnitude"]
    automated_tuning.price_up_min_win_rate_diff = row["priceupminwinratediff"]
    automated_tuning.price_up_obs_req = row["priceupobsreq"]
    automated_tuning.price_up_power = row["priceuppower"]
    automated_tuning.price_up_realization = row["priceuprealization"]
    automated_tuning.price_up_sig_level = row["priceupsiglevel"]
    automated_tuning.product = row["product"]
    automated_tuning.salt_value = row["saltvalue"]

    return automated_tuning


def cost_adjustment_from_row(row: Any) -> CostAdjustmentModel:
    cost_adjustment = CostAdjustmentModel()

    cost_adjustment.product = row["product"]
    cost_adjustment.cost = row["cost"]
    cost_adjustment.form = row["form"]
    cost_adjustment.material = row["material"]
    cost_adjustment.material_classification = row["materialclassification"]
    cost_adjustment.material_description = row["materialdescription"]
    cost_adjustment.stock_plant = row["stockplant"]
    cost_adjustment.target_margin = row["targetmargin"]
    cost_adjustment.unique_id = row["uniqueid"]

    return cost_adjustment


def location_group_from_row(row: Any) -> LocationGroupModel:
    location_group = LocationGroupModel()

    location_group.unique_id = row["uniqueid"]
    location_group.location_group_value = row["locationgroup"]
    location_group.rc_mapping = row["rcmapping"]
    location_group.region = row["region"]

    return location_group;


def mill_to_plant_freight_from_row(row: Any) -> PackagingCostModel:
    mill_to_plant_freight = MillToPlantFreightModel()

    mill_to_plant_freight.unique_id = row["uniqueid"]
    mill_to_plant_freight.bellwether_material = row["bellwethermaterial"]
    mill_to_plant_freight.ship_plant = row["shipplant"]
    mill_to_plant_freight.mill_to_plant_freight_value = float(row["milltoplantfreight"])

    return mill_to_plant_freight


class SqlLiteLookupService(LookupServiceInterface, ABC):
    def __init__(self, configuration: Config):
        connection_string = configuration.connection

        self._connection = sqlite3.connect(connection_string)

    def lookup_customer(self, client_id: str, table_id: str, label: str, default_value: Optional[CustomerModel]) -> CustomerModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return customer_from_row(row)

    def lookup_product(self, client_id: str, table_id: str, label: str, default_value: Optional[ProductModel]) -> ProductModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return product_from_row(row)

    def lookup_packaging_cost(self, client_id: str, table_id: str, label: str, default_value: Optional[PackagingCostModel]) -> PackagingCostModel:
        query = f"select pkl.* from packaging_cost_lookups pkl inner join OverheadGroupLookups ogl on pkl.uniqueid = ogl.overheadgroup where ogl.uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return packaging_cost_from_row(row)

    def lookup_tm_adjustment(self, client_id: str, table_id: str, label: str, default_value: Optional[TmAdjustmentModel]) -> TmAdjustmentModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return tm_adjustment_from_row(row)

    def lookup_mill_to_plant_freight(self, client_id: str, table_id: str, label: str, default_value: Optional[MillToPlantFreightModel]) -> MillToPlantFreightModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return mill_to_plant_freight_from_row(row)

    def lookup_material_sales_office(self, client_id: str, table_id: str, label: str, default_value: Optional[MaterialSalesOfficeModel]) -> MaterialSalesOfficeModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return material_sales_office_from_row(row)

    def lookup_sap_freight(self, client_id, table_id: str, label: str, default_value: Optional[SapFreightModel]) -> SapFreightModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return sap_freight_from_row(row)

    def lookup_south_skid_charge(self, client_id: str, table_id: str, label: str, default_value: Optional[SouthSkidChargeModel]) -> SouthSkidChargeModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return south_skid_charge_from_row(row)

    def lookup_op_code(self, op_code: str, adjusted_net_weight_of_sales_item: float, net_weight_of_sales_item: float) -> OpCodeModel:
        query = f"SELECT * from opcodes WHERE opcode = '{op_code}' and netweightlow <= {adjusted_net_weight_of_sales_item} and netweighthigh > {adjusted_net_weight_of_sales_item} and pieceweightlow <= {net_weight_of_sales_item} and pieceweighthigh > {net_weight_of_sales_item} COLLATE NOCASE"

        cursor = self._connection.cursor()

        cursor.execute(query)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return op_code_from_row(row)

    def lookup_south_freight(self, client_id: str, table_id: str, label: str, default_value: Optional[SouthFreightModel]) -> SouthFreightModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return south_freight_from_row(row)

    def lookup_ship_zone(self, client_id: str, table_id: str, label: str, default_value: Optional[ShipZoneModel]) -> ShipZoneModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return ship_zone_from_row(row)

    def lookup_so_bw_floor_price(self, client_id: str, table_id: str, label: str, default_value: Optional[SoBwFloorPriceModel]) -> SoBwFloorPriceModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return so_bw_floor_price_from_row(row)

    def lookup_bw_rating(self, client_id: str, table_id: str, label: str, default_value: Optional[BwRatingModel]) -> BwRatingModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return bw_rating_from_row(row)

    def lookup_freight_default(self, client_id: str, table_id: str, label: str, default_value: Optional[FreightDefaultModel]) -> FreightDefaultModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return freight_default_from_row(row)

    def lookup_target_margin(self, client_id: str, table_id: str, label: str, default_value: Optional[float]) -> float:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return target_margin_from_row(row).target_margin_value

    def lookup_cl_code(self, client_id: str, table_id: str, label: str, default_value: Optional[ClCodeModel]) -> ClCodeModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return cl_code_from_row(row)

    def lookup_ido(self, client_id: str, table_id: str, label: str, default_value: Optional[IdoModel]) -> IdoModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return ido_from_row(row)

    def bucketed_lookup(self, client_id: str, table_id: str, val: float, column: str) -> str:
        query = f"SELECT * FROM {table_id} WHERE coalesce(min, {sys.maxsize}) <= {val} and coalesce(max, {sys.maxsize}) >= {val} COLLATE NOCASE"

        cursor = self._connection.cursor()

        cursor.execute(query)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return row[column]

    def get_customer_without_office(self, customer_number: str) -> CustomerModel:
        query = f"SELECT * FROM customers WHERE customernumber = '{customer_number}' COLLATE NOCASE"

        cursor = self._connection.cursor()

        cursor.execute(query)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return customer_from_row(row)

    def get_default_office(self, customer_sales_office: str) -> CustomerModel:
        query = f"SELECT * FROM customers WHERE customersalesoffice = '{customer_sales_office}' COLLATE NOCASE"

        cursor = self._connection.cursor()

        cursor.execute(query)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return customer_from_row(row)

    def lookup_automated_tuning(self, client_id: str, table_id: str, label: str, default_value: Optional[AutomatedTuningModel]) -> AutomatedTuningModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return automated_tuning_from_row(row)

    def lookup_location_group(self, client_id: str, table_id: str, label: str, default_value: Optional[LocationGroupModel]) -> LocationGroupModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return location_group_from_row(row)

    def lookup_cost_adjustment(self, client_id: str, table_id: str, label: str, default_value: Optional[CostAdjustmentModel]) -> CostAdjustmentModel:
        query = f"SELECT * FROM {table_id} WHERE uniqueid = :label COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return cost_adjustment_from_row(row)

    def lookup_exchange_rate(self, client_id: str, table_id: str, label: str, default_value: Optional[ProductModel]) -> ProductModel:
        query = f"SELECT * FROM {table_id} WHERE rcMapping = :label limit 1 COLLATE NOCASE"

        params = {"label": label}

        cursor = self._connection.cursor()

        cursor.execute(query, params)

        cursor.row_factory = sqlite3.Row

        row = cursor.fetchone()

        if row is None:
            return None

        return product_from_row(row)
