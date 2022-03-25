from .calculation import CalculationApi


def initialize_routes(api):
    api.add_resource(CalculationApi, '/ces/clients/<string:client_id>/calculations/<string:model_id>')
