from typing import Optional

from api.model.automatedtuning import AutomatedTuningModel
from api.model.bwrating import BwRatingModel
from api.model.clcode import ClCodeModel
from api.model.customer import CustomerModel
from api.model.freightdefault import FreightDefaultModel
from api.model.ido import IdoModel
from api.model.locationgroup import LocationGroupModel
from api.model.materialsalesoffice import MaterialSalesOfficeModel
from api.model.milltoplantfreight import MillToPlantFreightModel
from api.model.packagingcost import PackagingCostModel
from api.model.product import ProductModel
from api.model.sapfreight import SapFreightModel
from api.model.shipzone import ShipZoneModel
from api.model.sobwfloorprice import SoBwFloorPriceModel
from api.model.southfreight import SouthFreightModel
from api.model.southskidcharge import SouthSkidChargeModel
from api.model.tmadjustment import TmAdjustmentModel
from api.service.interfaces.lookupserviceinterface import LookupServiceInterface


class SqlLiteLookupService(LookupServiceInterface):
    def lookup_customer(self, client_id: str, table_id: str, label: str, default_value: Optional[CustomerModel]) -> CustomerModel:
        pass

    def lookup_product(self, client_id: str, table_id: str, label: str, default_value: Optional[ProductModel]) -> ProductModel:
        pass

    def lookup_packaging_cost(self, client_id: str, table_id: str, label: str, default_value: Optional[PackagingCostModel]) -> PackagingCostModel:
        pass

    def lookup_mill_to_plant_freight(self, client_id: str, table_id: str, label: str, default_value: Optional[MillToPlantFreightModel]) -> MillToPlantFreightModel:
        pass

    def lookup_tm_adjustment(self, client_id: str, table_id: str, label: str, default_value: Optional[TmAdjustmentModel]) -> TmAdjustmentModel:
        pass

    def lookup_material_sales_office(self, client_id: str, table_id: str, label: str, default_value: Optional[MaterialSalesOfficeModel]) -> MaterialSalesOfficeModel:
        pass

    def lookup_sap_freight(self, client_id, table_id: str, label: str, default_value: Optional[SapFreightModel]) -> SapFreightModel:
        pass

    def lookup_south_skid_charge(self, client_id: str, table_id: str, label: str, default_value: Optional[SouthSkidChargeModel]) -> SouthSkidChargeModel:
        pass

    def lookup_south_freight(self, client_id: str, table_id: str, label: str, default_value: Optional[SouthFreightModel]) -> SouthFreightModel:
        pass

    def lookup_ship_zone(self, client_id: str, table_id: str, label: str, default_value: Optional[ShipZoneModel]) -> ShipZoneModel:
        pass

    def lookup_so_bw_floor_price(self, client_id: str, table_id: str, label: str, default_value: Optional[SoBwFloorPriceModel]) -> SoBwFloorPriceModel:
        pass

    def lookup_bw_rating(self, client_id: str, table_id: str, label: str, default_value: Optional[BwRatingModel]) -> BwRatingModel:
        pass

    def lookup_freight_default(self, client_id: str, table_id: str, label: str, default_value: Optional[FreightDefaultModel]) -> FreightDefaultModel:
        pass

    def lookup_target_margin(self, client_id: str, table_id: str, label: str, default_value: Optional[float]) -> float:
        pass

    def lookup_cl_code(self, client_id: str, table_id: str, label: str, default_value: Optional[ClCodeModel]) -> ClCodeModel:
        pass

    def lookup_ido(self, client_id: str, table_id: str, label: str, default_value: Optional[IdoModel]) -> IdoModel:
        pass

    def bucketed_lookup(self, client_id: str, table_id: str, val: float, column: str) -> str:
        pass

    def get_customer_without_office(self, customer_number: str) -> CustomerModel:
        c = CustomerModel()

        c.percent_adder = 0.1
        c.customer_name = "Bob Maurer"
        c.dollar_adder = 0.01
        c.dso_adder = 0.02
        c.sap_ind = "N"
        c.dso = "a"
        c.waive_skid = "y"
        c.customer_sales_office = "Cleveland"
        c.isr_office = "1014"
        c.multi_market_name = "insight"
        c.rc_mapping = "43"
        c.customer_number = "123456"
        c.unique_id = "123456"

        return c

    def get_default_office(self, customer_sales_office: str) -> CustomerModel:
        pass

    def lookup_automated_tuning(self, client_id: str, table_id: str, label: str, default_value: Optional[AutomatedTuningModel]) -> AutomatedTuningModel:
        pass

    def lookup_location_group(self, client_id: str, table_id: str, label: str, default_value: Optional[LocationGroupModel]) -> LocationGroupModel:
        pass
