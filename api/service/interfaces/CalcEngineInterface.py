import abc


class CalcEngineInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'execute_model') and
                callable(subclass.execute_model))

    @abc.abstractmethod
    def execute_model(self, json_data: str, calculation_id: str) -> str:
        """Execute the model"""
        raise NotImplementedError('users must define execute_model to use this base class')
