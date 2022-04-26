import abc
from typing import Optional

from api.model.costadjustment import CostAdjustmentModel
from api.model.customer import CustomerModel
from api.model.opcode import OpCodeModel
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
                (hasattr(subclass, 'lookup_location_group') and callable(subclass.lookup_location_group)) and
                (hasattr(subclass, 'lookup_op_code') and callable(subclass.lookup_op_code)) and
                (hasattr(subclass, 'lookup_cost_adjustment') and callable(subclass.lookup_cost_adjustment)) and
                (hasattr(subclass, 'lookup_exchange_rate') and callable(subclass.lookup_exchange_rate))
                )

    @abc.abstractmethod
    def lookup_customer(self, client_id: str, table_id: str, label: str, default_value: Optional[CustomerModel]) -> CustomerModel:
        """Locate a customer object by id"""
        pass

    @abc.abstractmethod
    def lookup_product(self, client_id: str, table_id: str, label: str, default_value: Optional[ProductModel]) -> ProductModel:
        """Locate a product by id"""
        pass

    @abc.abstractmethod
    def lookup_packaging_cost(self, client_id: str, table_id: str, label: str, default_value: Optional[PackagingCostModel]) -> PackagingCostModel:
        """Locate packaging cost by id"""
        pass

    @abc.abstractmethod
    def lookup_mill_to_plant_freight(self, client_id: str, table_id: str, label: str, default_value: Optional[MillToPlantFreightModel]) -> MillToPlantFreightModel:
        """Locate mill to plant freight cost by id"""
        pass

    @abc.abstractmethod
    def lookup_tm_adjustment(self, client_id: str, table_id: str, label: str, default_value: Optional[TmAdjustmentModel]) -> TmAdjustmentModel:
        """Locate tm adjustment by id"""
        pass

    @abc.abstractmethod
    def lookup_material_sales_office(self, client_id: str, table_id: str, label: str, default_value: Optional[MaterialSalesOfficeModel]) -> MaterialSalesOfficeModel:
        """Locate the material sales office by id"""
        pass

    @abc.abstractmethod
    def lookup_sap_freight(self, client_id, table_id: str, label: str, default_value: Optional[SapFreightModel]) -> SapFreightModel:
        """Locate the sap freight by sap id"""
        pass

    @abc.abstractmethod
    def lookup_op_code(self, op_code: str, adjusted_net_weight_of_sales_item: float, net_weight_of_sales_item: float) -> OpCodeModel:
        """Located the south skid charge by id"""
        pass

    @abc.abstractmethod
    def lookup_south_skid_charge(self, client_id: str, table_id: str, label: str, default_value: Optional[SouthSkidChargeModel]) -> SouthSkidChargeModel:
        """Located the south skid charge by id"""
        pass

    @abc.abstractmethod
    def lookup_south_freight(self, client_id: str, table_id: str, label: str, default_value: Optional[SouthFreightModel]) -> SouthFreightModel:
        """Locate the south freight by id"""
        pass

    @abc.abstractmethod
    def lookup_ship_zone(self, client_id: str, table_id: str, label: str, default_value: Optional[ShipZoneModel]) -> ShipZoneModel:
        """Locate the ship zone by id"""
        pass

    @abc.abstractmethod
    def lookup_so_bw_floor_price(self, client_id: str, table_id: str, label: str, default_value: Optional[SoBwFloorPriceModel]) -> SoBwFloorPriceModel:
        """Locate the sobw by id"""
        pass

    @abc.abstractmethod
    def lookup_bw_rating(self, client_id: str, table_id: str, label: str, default_value: Optional[BwRatingModel]) -> BwRatingModel:
        """Locate the bw rating by id"""
        pass

    @abc.abstractmethod
    def lookup_freight_default(self, client_id: str, table_id: str, label: str, default_value: Optional[FreightDefaultModel]) -> FreightDefaultModel:
        """Locate the freight default by id"""
        pass

    @abc.abstractmethod
    def lookup_target_margin(self, client_id: str, table_id: str, label: str, default_value: Optional[float]) -> float:
        """Locate the target margin by id"""
        pass

    @abc.abstractmethod
    def lookup_cl_code(self, client_id: str, table_id: str, label: str, default_value: Optional[ClCodeModel]) -> ClCodeModel:
        """Locate the cl code by id"""
        pass

    @abc.abstractmethod
    def lookup_ido(self, client_id: str, table_id: str, label: str, default_value: Optional[IdoModel]) -> IdoModel:
        """Locate the ido by id"""
        pass

    @abc.abstractmethod
    def bucketed_lookup(self, client_id: str, table_id: str, val: float, column: str) -> str:
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
    def lookup_automated_tuning(self, client_id: str, table_id: str, label: str, default_value: Optional[AutomatedTuningModel]) -> AutomatedTuningModel:
        """Locate the automated tuning record by id"""
        pass

    @abc.abstractmethod
    def lookup_location_group(self, client_id: str, table_id: str, label: str, default_value: Optional[LocationGroupModel]) -> LocationGroupModel:
        """Locate the location group by id"""
        pass

    @abc.abstractmethod
    def lookup_cost_adjustment(self, client_id: str, table_id: str, label: str, default_value: Optional[CostAdjustmentModel]) -> CostAdjustmentModel:
        """Locate the cost adjustment by id"""
        pass

    @abc.abstractmethod
    def lookup_exchange_rate(self, client_id: str, table_id: str, label: str, default_value: Optional[ProductModel]) -> ProductModel:
        """Locate the cost adjustment by id"""
        pass
