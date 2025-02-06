import requests


class UnipileService(object):

    def __init__(self, authorization_key: str, subdomain: str, port: int):
        self.authorization_key = authorization_key
        self.subdomain = subdomain
        self.port = port

        self.BASE_URL = f"https://{self.subdomain}.unipile.com:{self.port}/api/v1/"

        self.session = requests.Session()

    def retrieve_profile(self, account_retrieving: str, account_id: str) -> dict:
        uri = self.BASE_URL + f"users/{account_id}"

        headers = {
            "accept": "application/json",
            "X-API-KEY": self.authorization_key
        }

        response = self.session.get(uri, headers=headers, params=dict(account_id=account_retrieving))

        response.raise_for_status()

        return response.json()

    def retrieve_chat_messages(self, chat_id: str, limit: int) -> dict:
        uri = self.BASE_URL + f"chats/{chat_id}/messages"

        headers = {
            "accept": "application/json",
            "X-API-KEY": self.authorization_key
        }

        response = self.session.get(uri, headers=headers, params=dict(limit=limit))

        response.raise_for_status()

        return response.json()

    def send_message(self, chat_id: str, text: str):
        uri = self.BASE_URL + f"chats/{chat_id}/messages"

        headers = {
            "accept": "application/json",
            "X-API-KEY": self.authorization_key
        }

        data = {
            "text": text
        }

        response = self.session.post(uri, headers=headers, json=data)

        response.raise_for_status()

        return response.json()
