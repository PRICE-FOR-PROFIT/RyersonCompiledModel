import json

from api.model.parameter import ParameterModel
from api.model.calculationinput import CalculationInputModel


class CalculationHelper:
    @staticmethod
    def is_defaultable(parameter: ParameterModel, calc_input_name: set) -> bool:
        return not parameter.is_required and parameter.default_value is not None and parameter.name.lower() not in calc_input_name

    @staticmethod
    def get_default_value(parameter: ParameterModel) -> any:
        if parameter.parameter_type.casefold() == "int":
            return int(parameter.default_value)
        elif parameter.parameter_type.casefold() == "double":
            return float(parameter.default_value)
        elif parameter.parameter_type.casefold() == "bool":
            return bool(parameter.default_value)
        elif parameter.parameter_type.casefold() == "array":
            return parameter.default_value
        elif parameter.parameter_type.casefold() == "objectarray":
            return parameter.default_value
        elif parameter.parameter_type.casefold() == "literal":
            return parameter
        else:
            return parameter.default_value

    @staticmethod
    def get_defaulted_calculation_input(parameter: ParameterModel) -> CalculationInputModel:
        input_model = CalculationInputModel()

        input_model.Name = parameter.name
        input_model.Value = CalculationHelper.get_default_value(parameter)

        return input_model

    @staticmethod
    def get_defaulted_optional_inputs_json(model_inputs: list[ParameterModel], calculation_inputs: dict) -> list[CalculationInputModel]:
        calc_input_names = [key.lower() for key in calculation_inputs.keys()]

        inputs = [CalculationHelper.get_defaulted_calculation_input(mi) for mi in model_inputs if CalculationHelper.is_defaultable(mi, calc_input_names)]

        return inputs
