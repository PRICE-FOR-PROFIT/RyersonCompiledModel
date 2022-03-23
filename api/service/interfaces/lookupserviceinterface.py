import abc
from api.model.customer import CustomerModel
from api.model.product import ProductModel
from api.model.packagingcost import PackagingCostModel
from api.model.milltoplantfreight import MillToPlantFreightModel
from api.model.tmadjustment import TmAdjustmentModel
from api.model.materialsalesoffice import MaterialSalesOfficeModel
from api.model.sapfreight import SapFreightModel


class LookupServiceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'execute_model') and
                callable(subclass.execute_model))

    @abc.abstractmethod
    def lookup_customer(self, client_id: str, customer_id: str, label: str, default_value: CustomerModel) -> CustomerModel:
        """Locate a customer object by id"""
        pass

    def lookup_product(self, client_id: str, product_id: str, label: str, default_value: ProductModel) -> ProductModel:
        """Locate a product by id"""
        pass

    def lookup_packaging_cost(self, client_id: str, packaging_cost_id: str, label: str, default_value: PackagingCostModel) -> PackagingCostModel:
        """Locate packaging cost by id"""
        pass

    def lookup_mill_to_plant_freight(self, client_id: str, plant_id: str, label: str, default_value: MillToPlantFreightModel) -> MillToPlantFreightModel:
        """Locate mill to plant freight cost by id"""
        pass

    def lookup_tm_adjustment(self, client_id: str, adjustment_id: str, label: str, default_value: TmAdjustmentModel) -> TmAdjustmentModel:
        """Locate tm adjustment by id"""
        pass

    def lookup_material_sales_office(self, client_id: str, sales_office_id: str, label: str, default_value: MaterialSalesOfficeModel) -> MaterialSalesOfficeModel:
        """Locate the material sales office by id"""
        pass

    def lookup_sap_freight(self, client_id, sap_id:str, label: str, default_value: SapFreightModel) -> SapFreightModel:
        """Locate sap freight by sap id"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

    def lookup_customer(self):
        """Short descripotion"""
        pass

