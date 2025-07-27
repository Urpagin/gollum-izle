import json
import logging

import requests


class PasteApi:
    def __init__(self, text: str, api_key: str):
        """
        Creates a paste.ee link.
        Go to https://paste.ee
        :param text: The text in the pastebin.
        """
        self._text = text
        self._api_key = api_key
        self.pastebin_url = self._get_pastebin()

    def _get_pastebin(self) -> str | None:

        if not isinstance(self._text, str) or not self._text:
            return None

        payload = {"sections": [{"contents": self._text, "syntax": "json"}]}
        headers = {"X-Auth-Token": self._api_key}

        try:
            # r = requests.post(url="https://api.paste.ee/v1/pastes",
            #                  json=payload, headers=headers, verify=False)

            r = requests.post(url="https://api.paste.ee/v1/pastes",
                              json=payload, headers=headers)

            response = json.loads(r.content)
            logging.debug(f"Paste.ee response: {response}")
            print(response)
            return response['link'].replace("/p/", "/r/")

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return None
