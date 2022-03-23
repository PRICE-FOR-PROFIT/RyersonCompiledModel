from unittest import TestCase
from api.service.interfaces import calcengineinterface


class BobEngine(CalcEngineInterface.CalcEngineInterface):
    def execute_model(self, client_id, model, model_input, calculation_id):
        pass


class TestStringMethods(TestCase):
    def test_up(self):
        self.engine = BobEngine()
        self.assertTrue(issubclass(BobEngine, CalcEngineInterface.CalcEngineInterface))
