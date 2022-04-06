import datetime


class LogInformationModel:
    def __init__(self):
        self.id = ""
        self.calculation_id = ""
        self.model_version = ""
        self.model_id = ""
        self.client_id = ""
        self.authorization_id = ""
        self.create_date = datetime.date
        self.calculation_inputs = {}
        self.intermediate_calculations = {}
        self.calculation_outputs = {}
        self.original_payload = {}
        self.error_message = ""
