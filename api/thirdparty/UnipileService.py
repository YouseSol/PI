import requests


class UnipileService(object):

    def __init__(self, authorization_key: str, subdomain: str, port: int):
        self.session = requests.Session()
        self.session.headers =  {
            "accept": "application/json",
            "X-API-KEY": authorization_key
        }

        self.base_url = f"https://{subdomain}.unipile.com:{port}/api/v1/"

    def retrieve_profile(self, account_retrieving: str, account_id: str) -> dict:
        uri = self.base_url + f"users/{account_id}"

        response = self.session.get(uri, params=dict(account_id=account_retrieving))

        response.raise_for_status()

        return response.json()

    def retrieve_chat_messages(self, chat_id: str, limit: int) -> dict:
        uri = self.base_url + f"chats/{chat_id}/messages"

        response = self.session.get(uri, params=dict(limit=limit))

        response.raise_for_status()

        return response.json()

    def send_message(self, chat_id: str, text: str):
        uri = self.base_url + f"chats/{chat_id}/messages"

        response = self.session.post(uri, json=dict(text=text))

        response.raise_for_status()

        return response.json()
