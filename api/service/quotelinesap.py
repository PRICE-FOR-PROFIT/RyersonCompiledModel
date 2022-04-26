from typing import Any

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

    def execute_model(self, request_client_id: str, client_id: str, model: ModelModel, original_payload: dict[str, Any], calculation_id: str, token: str) -> dict[str, Any]:

        a = self._lookup_service.lookup_customer(client_id, "customers", "0000000000|T09", None)
        b = self._lookup_service.lookup_product(client_id, "products", "WESTMEX|100000901", None)
        c = self._lookup_service.lookup_packaging_cost(client_id, "packaging_cost_lookups", "99GB100000", None)
        d = self._lookup_service.lookup_tm_adjustment(client_id, "tm_adjustments", "CAL-MEX|ALUMINUM|FLAT", None)
        e = self._lookup_service.lookup_mill_to_plant_freight(client_id, "mill_to_plant_freights", "160000885|1004", None)
        f = self._lookup_service.lookup_material_sales_office(client_id, "MaterialSalesOfficeLookups", "160006249|3030", None)
        g = self._lookup_service.lookup_sap_freight(client_id, "sap_freight_lookups", "1001|131", None)
        h = self._lookup_service.lookup_south_skid_charge(client_id, "south_skid_charge_lookup", "STAINLESS|PLATE", None)
        i = self._lookup_service.lookup_op_code("ABM", 100.0, 10.0)
        j = self._lookup_service.lookup_south_freight(client_id, "south_freight_lookups", "2001|1", None)
        k = self._lookup_service.lookup_ship_zone(client_id, "ship_zone_lookups", "0000000000|2031", None)
        l = self._lookup_service.lookup_so_bw_floor_price(client_id, "so_bw_floor_price_lookup", "1004|100018313", None)
        m = self._lookup_service.lookup_bw_rating(client_id, "bw_rating_lookup", "CAL-MEX|160001700", None)
        o = self._lookup_service.lookup_freight_default(client_id, "freight_defaults", "4806|WI", None)
        p = self._lookup_service.lookup_target_margin(client_id, "target_margin_lookups", "T19|26228", None)
        q = self._lookup_service.lookup_cl_code(client_id, "cl_codes", "0010050438|1021|STAINLESS|FLAT", None)
        r = self._lookup_service.lookup_ido(client_id, "ido_lookup", "2000|2000", None)
        s = self._lookup_service.get_customer_without_office("0000000003")
        t = self._lookup_service.get_default_office("T07")
        u = self._lookup_service.lookup_automated_tuning(client_id, "automated_tuning_lookup", "CANADA|ALUMINUM|FR", None)
        v = self._lookup_service.lookup_location_group(client_id, "location_group_lookup", "CDNEAST", None)
        z = self._lookup_service.bucketed_lookup(client_id, "weight_class", 300.0, "totalquotepounds")

        return {"itemNumber": "000010", "recommendedPricePerPound": "9.801"}
