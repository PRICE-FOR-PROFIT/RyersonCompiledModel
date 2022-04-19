class MaskedError(Exception):
    def __init__(self, original_message: str, user_defined_message: str):
        super().__init__(original_message)

        self.user_defined_message = user_defined_message
