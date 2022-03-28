import base64
import json


class AuthenticationHelper:
    @staticmethod
    def extract_client_id(encrypted_token: str) -> str:
        try:
            token_items = encrypted_token.split(".")

            if len(token_items) < 3:
                raise Exception("Error:  Invalid token " + encrypted_token)

            pad_length = len(token_items[1]) + (len(token_items[1]) * 3) % 4

            padded_token = token_items[1].ljust(pad_length, "=")
            decoded_token = base64.b64decode(padded_token)

            jwt = json.loads(decoded_token)

            if "client_id" in jwt:
                client_id = jwt["client_id"]
            elif "appid" in jwt:
                client_id = jwt["appid"]
            elif "name" in jwt:
                client_id = jwt["name"]
            else:
                client_id = "unknown"

            return client_id
        except Exception as ex:
            print(ex)
