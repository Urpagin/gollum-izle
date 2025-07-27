# Api: https://api.mcsrvstat.us/

import requests
import logging
import json


class MinecraftServerStatusApi:
    """Takes a Minecraft server ip and port, returns information about it. E.g: players, motd, ..."""

    _JAVA_API_URL = "https://api.mcsrvstat.us/2/"
    _BEDROCK_API_URL = "https://api.mcsrvstat.us/bedrock/2/"
    _ICON_ENDPOINT = "https://api.mcsrvstat.us/icon/"

    def __init__(self, ip: str, port: int, bedrock: bool = False):
        self._ip = ip
        self._port = port
        self._bedrock = bedrock

        self.online = False
        self.ip = ""
        self.ip_input = ""  # Will be set to user input
        self.port = 0
        self.port_input = 0  # Will be set to user input
        self.debug = {}
        self.motd = {}
        self.players = {}
        self.version = ""
        self.protocol = 0
        self.hostname = ""
        self.b64icon = ""
        self.software = ""
        self.map = ""
        self.gamemode = ""  # BEDROCK
        self.server_id = ""  # BEDROCK
        self.plugins = {}
        self.mods = {}
        self.info = {}
        self.raw_data = {}

        self.errors = []

        data = MinecraftServerStatusApi._fetch_data(self)
        self._assign_attributes(data)

    def __str__(self):
        return (
            f"{'*' * 80}\n"
            f"online: {self.online}\n"
            f"ip: {self.ip}\n"
            f"port: {self.port}\n"
            f"debug: {self.debug}\n"
            f"motd: {self.motd}\n"
            f"players: {self.players}\n"
            f"version: {self.version}\n"
            f"protocol: {self.protocol}\n"
            f"hostname: {self.hostname}\n"
            f"b64icon: {self.b64icon}\n"
            f"software: {self.software}\n"
            f"map: {self.map}\n"
            f"gamemode: {self.gamemode}\n"
            f"server_id: {self.server_id}\n"
            f"plugins: {self.plugins}\n"
            f"mods: {self.mods}\n"
            f"info: {self.info}\n"
            f"raw_data: {self.raw_data}\n"
            f"{'*' * 80}"
        )

    def _get_url(self):
        """Returns the Minecraft Server Status API url for java/bedrock. E.g: https://api.mcsrvstat.us/2/<address>"""

        url = ""

        if self._bedrock:
            if self.port == 19132:  # Minecraft's default bedrock server port
                url = f"{self._BEDROCK_API_URL}{self._ip}"
            else:
                url = f"{self._BEDROCK_API_URL}{self._ip}:{self._port}"

        if not self._bedrock:
            if self._port == 25565:  # Minecraft's default java server port
                url = f"{self._JAVA_API_URL}{self._ip}"
            else:
                url = f"{self._JAVA_API_URL}{self._ip}:{self._port}"

        return url

    def _fetch_data(self) -> dict | None:
        """Gets the data from the url"""

        url = self._get_url()

        try:
            logging.debug(f"Fetching data with: {url}")
            data = requests.get(url)
        except Exception as e:
            logging.error(f"Cannot fetch url. {e}")
            self.errors.append(e)
            return None

        return json.loads(data.text)

    def _get_icon(self) -> str:
        """Gets the icon url from the api"""
        url = f"{self._ICON_ENDPOINT}{self.ip}{f':{self.port}' if self.port is not 25565 else ''}"
        return url

    def _assign_attributes(self, data: dict):

        self.online = data.get('online')
        self.ip = data.get('ip')
        self.ip_input = self._ip  # Set to user input
        self.port = data.get('port')
        self.port_input = self._port  # Set to user input
        self.debug = data.get('debug')
        self.motd = data.get('motd')
        self.players = data.get('players')
        self.version = data.get('version')
        self.protocol = data.get('protocol')
        self.hostname = data.get('hostname')
        self.b64icon = data.get('icon')
        self.icon_link = self._get_icon()
        self.software = data.get('software')
        self.map = data.get('map')
        self.gamemode = data.get('gamemode')  # BEDROCK
        self.server_id = data.get('serverid')  # BEDROCK
        self.plugins = data.get('plugins')
        self.mods = data.get('mods')
        self.info = data.get('info')
        self.raw_data = data
