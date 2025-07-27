import json
import logging
import os
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_ID: str = os.environ['DISCORD_ID']


@dataclass
class FactsApi:
    api_key: str
    limit: int = 1
    BASE_URL: str = 'https://api.api-ninjas.com/v1/facts'

    def get_fact(self, is_premium: bool = False) -> list[dict[str, str]]:
        """Returns a list of dicts varying with `limit`: [{"fact": "abc1"}, {"fact", "abc2"}]"""

        url: str = f'{self.BASE_URL}?limit={self.limit}' if is_premium else self.BASE_URL
        response = requests.get(url, headers={'X-Api-Key': self.api_key})
        if response.status_code == requests.codes.ok:
            logging.debug(f'Successfully got a response from FactsApi: {response.text}')
            return json.loads(response.text)
        else:
            logging.error(f"Error: HTTP code {response.status_code}; text: {response.text}")
            return [{'fact': f'Error, please contact <@{DISCORD_ID}>!'}]
