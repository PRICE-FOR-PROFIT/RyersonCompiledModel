class ParameterModel:
    def __init__(self, name: str, parameter_type: str, is_required: bool, default_value: str):
        self.name = name
        self.parameter_type = parameter_type
        self.is_required = is_required
        self.default_value = default_value
