import abc
from api.model.loginformation import LogInformationModel


class QueuedLoggerInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, 'log_information') and callable(subclass.execute_model)

    @abc.abstractmethod
    def log_information(self, log_information: LogInformationModel):
        """Execute the model"""
        raise NotImplementedError('users must define log_information to use this base class')
