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
    def lookup_customer(self, client_id: str, customer_id: str, label: str, default_value: CustomerModel) -> CustomerModel:
        pass

    def lookup_product(self, client_id: str, product_id: str, label: str, default_value: ProductModel) -> ProductModel:
        pass

    def lookup_packaging_cost(self, client_id: str, packaging_cost_id: str, label: str, default_value: PackagingCostModel) -> PackagingCostModel:
        pass

    def lookup_mill_to_plant_freight(self, client_id: str, plant_id: str, label: str, default_value: MillToPlantFreightModel) -> MillToPlantFreightModel:
        pass

    def lookup_tm_adjustment(self, client_id: str, adjustment_id: str, label: str, default_value: TmAdjustmentModel) -> TmAdjustmentModel:
        pass

    def lookup_material_sales_office(self, client_id: str, sales_office_id: str, label: str, default_value: MaterialSalesOfficeModel) -> MaterialSalesOfficeModel:
        pass

    def lookup_sap_freight(self, client_id, sap_id: str, label: str, default_value: SapFreightModel) -> SapFreightModel:
        pass

    def lookup_south_skid_charge(self, client_id: str, skid_id: str, label: str, default_value: SouthSkidChargeModel) -> SouthSkidChargeModel:
        pass

    def lookup_south_freight(self, client_id: str, freight_id: str, label: str, default_value: SouthFreightModel) -> SouthFreightModel:
        pass

    def lookup_ship_zone(self, client_id: str, ship_id: str, label: str, default_value: ShipZoneModel) -> ShipZoneModel:
        pass

    def lookup_so_bw_floor_price(self, client_id: str, so_bw_id: str, label: str, default_value: SoBwFloorPriceModel) -> SoBwFloorPriceModel:
        pass

    def lookup_bw_rating(self, client_id: str, bw_id: str, label: str, default_value: BwRatingModel) -> BwRatingModel:
        pass

    def lookup_freight_default(self, client_id: str, freight_id: str, label: str, default_value: FreightDefaultModel) -> FreightDefaultModel:
        pass

    def lookup_target_margin(self, client_id: str, margin_id: str, label: str, default_value: float) -> float:
        pass

    def lookup_cl_code(self, client_id: str, cl_code_id: str, label: str, default_value: ClCodeModel) -> ClCodeModel:
        pass

    def lookup_ido(self, client_id: str, ido_id: str, label: str, default_value: IdoModel) -> IdoModel:
        pass

    def bucketed_lookup(self, client_id: str, item_id: str, val: float, column: str) -> str:
        pass

    def get_customer_without_office(self, customer_number: str) -> CustomerModel:
        pass

    def get_default_office(self, customer_sales_office: str) -> CustomerModel:
        pass

    def lookup_automated_tuning(self, client_id: str, tuning_id: str, label: str, default_value: AutomatedTuningModel) -> AutomatedTuningModel:
        pass

    def lookup_location_group(self, client_id: str, group_id: str, label: str, default_value: LocationGroupModel) -> LocationGroupModel:
        pass
