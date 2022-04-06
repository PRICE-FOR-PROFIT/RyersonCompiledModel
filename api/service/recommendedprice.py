from typing import Any

import config

from api.service.interfaces.calcengineinterface import CalcEngineInterface
from api.service.interfaces.lookupserviceinterface import LookupServiceInterface
from api.service.interfaces.queuedloggerinterface import QueuedLoggerInterface
from api.model.model import ModelModel


class RecommendedPrice(CalcEngineInterface):
    def __init__(self, lookup_service: LookupServiceInterface, queued_logger: QueuedLoggerInterface, configuration: config, quote_line_sap: CalcEngineInterface):
        _lookup_service = lookup_service
        _config = config
        _quote_line_sap = quote_line_sap

    def execute_model(self, request_client_id: str, client_id: str, model: ModelModel, original_payload: dict[str, Any], calculation_id: str, token: str) -> dict[str, Any]:
        return {"modelId": model.id, "quoteLines": [{"itemNumber": "000010", "recommendedPricePerPound": "9.801"}]}
