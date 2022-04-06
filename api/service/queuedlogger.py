from api.model.loginformation import LogInformationModel
from api.service.interfaces.queuedloggerinterface import QueuedLoggerInterface


class QueuedLogger(QueuedLoggerInterface):
    def log_information(self, log_information: LogInformationModel):
        pass
