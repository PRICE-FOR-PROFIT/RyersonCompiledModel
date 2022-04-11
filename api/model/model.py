import datetime


class ModelModel:
    def __init__(self):
        self.id = ""
        self.name = ""
        self.version = 0
        self.is_active = False
        self.calculations = []
        self.model_inputs = []
        self.create_date = datetime.datetime.now()
        self.last_updated = datetime.datetime.now()
        self.last_updated_by = ""
        self.debug_mode = False
        self.read_only = False
