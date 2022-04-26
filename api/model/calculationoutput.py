from typing import Any


class CalculationOutputModel:
    def __init__(self, name: str, passthrough: bool, value: Any):
        self.Name = name
        self.Passthrough = passthrough
        self.Value = value
