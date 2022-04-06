import abc
from typing import Any
from api.model.model import ModelModel


class CalcEngineInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, 'execute_model') and callable(subclass.execute_model)

    @abc.abstractmethod
    def execute_model(self, request_client_id: str, client_id: str, mode: ModelModel, original_payload: dict[str, Any], calculation_id: str) -> dict[str, Any]:
        """Execute the model"""
        raise NotImplementedError('users must define execute_model to use this base class')
