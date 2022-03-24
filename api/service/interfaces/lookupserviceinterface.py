import abc
from api.model.customer import CustomerModel
from api.model.product import ProductModel
from api.model.packagingcost import PackagingCostModel
from api.model.milltoplantfreight import MillToPlantFreightModel
from api.model.tmadjustment import TmAdjustmentModel
from api.model.materialsalesoffice import MaterialSalesOfficeModel
from api.model.sapfreight import SapFreightModel
from api.model.southskidcharge import SouthSkidChargeModel
from api.model.southfreight import SouthFreightModel
from api.model.shipzone import ShipZoneModel
from api.model.sobwfloorprice import SoBwFloorPriceModel
from api.model.bwrating import BwRatingModel
from api.model.freightdefault import FreightDefaultModel
from api.model.clcode import ClCodeModel
from api.model.ido import IdoModel
from api.model.automatedtuning import AutomatedTuningModel
from api.model.locationgroup import LocationGroupModel


class LookupServiceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return ((hasattr(subclass, 'lookup_customer') and callable(subclass.lookup_customer)) and
                (hasattr(subclass, 'lookup_product') and callable(subclass.lookup_product)) and
                (hasattr(subclass, 'lookup_packaging_cost') and callable(subclass.lookup_packaging_cost)) and
                (hasattr(subclass, 'lookup_mill_to_plant_freight') and callable(subclass.lookup_mill_to_plant_freight)) and
                (hasattr(subclass, 'lookup_tm_adjustment') and callable(subclass.lookup_tm_adjustment)) and
                (hasattr(subclass, 'lookup_material_sales_office') and callable(subclass.lookup_material_sales_office)) and
                (hasattr(subclass, 'lookup_sap_freight') and callable(subclass.lookup_sap_freight)) and
                (hasattr(subclass, 'lookup_south_skid_charge') and callable(subclass.lookup_south_skid_charge)) and
                (hasattr(subclass, 'lookup_south_freight') and callable(subclass.lookup_south_freight)) and
                (hasattr(subclass, 'lookup_ship_zone') and callable(subclass.lookup_ship_zone)) and
                (hasattr(subclass, 'lookup_so_bw_floor_price') and callable(subclass.lookup_so_bw_floor_price)) and
                (hasattr(subclass, 'lookup_bw_rating') and callable(subclass.lookup_bw_rating)) and
                (hasattr(subclass, 'lookup_freight_default') and callable(subclass.lookup_freight_default)) and
                (hasattr(subclass, 'lookup_target_margin') and callable(subclass.lookup_target_margin)) and
                (hasattr(subclass, 'lookup_cl_code') and callable(subclass.lookup_cl_code)) and
                (hasattr(subclass, 'lookup_ido') and callable(subclass.lookup_ido)) and
                (hasattr(subclass, 'bucketed_lookup') and callable(subclass.bucketed_lookup)) and
                (hasattr(subclass, 'get_customer_without_office') and callable(subclass.get_customer_without_office)) and
                (hasattr(subclass, 'get_default_office') and callable(subclass.get_default_office)) and
                (hasattr(subclass, 'lookup_automated_tuning') and callable(subclass.lookup_automated_tuning)) and
                (hasattr(subclass, 'lookup_location_group') and callable(subclass.lookup_location_group)))

    @abc.abstractmethod
    def lookup_customer(self, client_id: str, customer_id: str, label: str, default_value: CustomerModel) -> CustomerModel:
        """Locate a customer object by id"""
        pass

    @abc.abstractmethod
    def lookup_product(self, client_id: str, product_id: str, label: str, default_value: ProductModel) -> ProductModel:
        """Locate a product by id"""
        pass

    @abc.abstractmethod
    def lookup_packaging_cost(self, client_id: str, packaging_cost_id: str, label: str, default_value: PackagingCostModel) -> PackagingCostModel:
        """Locate packaging cost by id"""
        pass

    @abc.abstractmethod
    def lookup_mill_to_plant_freight(self, client_id: str, plant_id: str, label: str, default_value: MillToPlantFreightModel) -> MillToPlantFreightModel:
        """Locate mill to plant freight cost by id"""
        pass

    @abc.abstractmethod
    def lookup_tm_adjustment(self, client_id: str, adjustment_id: str, label: str, default_value: TmAdjustmentModel) -> TmAdjustmentModel:
        """Locate tm adjustment by id"""
        pass

    @abc.abstractmethod
    def lookup_material_sales_office(self, client_id: str, sales_office_id: str, label: str, default_value: MaterialSalesOfficeModel) -> MaterialSalesOfficeModel:
        """Locate the material sales office by id"""
        pass

    @abc.abstractmethod
    def lookup_sap_freight(self, client_id, sap_id: str, label: str, default_value: SapFreightModel) -> SapFreightModel:
        """Locate the sap freight by sap id"""
        pass

    @abc.abstractmethod
    def lookup_south_skid_charge(self, client_id: str, skid_id: str, label: str, default_value: SouthSkidChargeModel) -> SouthSkidChargeModel:
        """Located the south skid charge by id"""
        pass

    @abc.abstractmethod
    def lookup_south_freight(self, client_id: str, freight_id: str, label: str, default_value: SouthFreightModel) -> SouthFreightModel:
        """Locate the south freight by id"""
        pass

    @abc.abstractmethod
    def lookup_ship_zone(self, client_id: str, ship_id: str, label: str, default_value: ShipZoneModel) -> ShipZoneModel:
        """Locate the ship zone by id"""
        pass

    @abc.abstractmethod
    def lookup_so_bw_floor_price(self, client_id: str, so_bw_id: str, label: str, default_value: SoBwFloorPriceModel) -> SoBwFloorPriceModel:
        """Locate the sobw by id"""
        pass

    @abc.abstractmethod
    def lookup_bw_rating(self, client_id: str, bw_id: str, label: str, default_value: BwRatingModel) -> BwRatingModel:
        """Locate the bw rating by id"""
        pass

    @abc.abstractmethod
    def lookup_freight_default(self, client_id: str, freight_id: str, label: str, default_value: FreightDefaultModel) -> FreightDefaultModel:
        """Locate the freight default by id"""
        pass

    @abc.abstractmethod
    def lookup_target_margin(self, client_id: str, margin_id: str, label: str, default_value: float) -> float:
        """Locate the target margin by id"""
        pass

    @abc.abstractmethod
    def lookup_cl_code(self, client_id: str, cl_code_id: str, label: str, default_value: ClCodeModel) -> ClCodeModel:
        """Locate the cl code by id"""
        pass

    @abc.abstractmethod
    def lookup_ido(self, client_id: str, ido_id: str, label: str, default_value: IdoModel) -> IdoModel:
        """Locate the ido by id"""
        pass

    @abc.abstractmethod
    def bucketed_lookup(self, client_id: str, item_id: str, val: float, column: str) -> str:
        """Locate a row by the bucket it belongs to"""
        pass

    @abc.abstractmethod
    def get_customer_without_office(self, customer_number: str) -> CustomerModel:
        """Locate the customer by id"""
        pass

    @abc.abstractmethod
    def get_default_office(self, customer_sales_office: str) -> CustomerModel:
        """Locate the customer by sales office"""
        pass

    @abc.abstractmethod
    def lookup_automated_tuning(self, client_id: str, tuning_id: str, label: str, default_value: AutomatedTuningModel) -> AutomatedTuningModel:
        """Locate the automated tuning record by id"""
        pass

    @abc.abstractmethod
    def lookup_location_group(self, client_id: str, group_id: str, label: str, default_value: LocationGroupModel) -> LocationGroupModel:
        """Locate the location group by id"""
        pass
