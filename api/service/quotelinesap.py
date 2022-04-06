from typing import Any

from api.service.interfaces.calcengineinterface import CalcEngineInterface
from api.model.model import ModelModel


class QuoteLineSap(CalcEngineInterface):

    def execute_model(self, request_client_id: str, client_id: str, model: ModelModel, original_payload: dict[str, Any], calculation_id: str, token: str) -> dict[str, Any]:
        return {"modelId": model.id, "quoteLines": [{"itemNumber": "000010", "recommendedPricePerPound": "9.801"}]}
