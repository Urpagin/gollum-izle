# !/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
import os
import pathlib
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
PASTEBIN_TOKEN = os.environ['PASTEEE_TOKEN']
PRESENCE = os.environ['PRESENCE']


class GollumIzle(commands.Bot):

    def __init__(self) -> None:
        super().__init__(
            command_prefix='%',
            intents=discord.Intents.all(),
        )

    async def setup_hook(self) -> None:
        for filename in os.listdir('src/cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'src.cogs.{filename[:-3]}')
                logging.info(f'Loaded cog: {filename}')
        synced = await bot.tree.sync()
        logging.info(f'Synced {len(synced)} command(s)')

    async def on_ready(self) -> None:
        logging.info(f'{self.user} has connected to Discord!')
        if PRESENCE:
            #activity = discord.Activity(type="type!", name=PRESENCE)
            activity = discord.Game(name=PRESENCE)
            await bot.change_presence(status=None, activity=activity)


def logging_init() -> None:
    current_path = os.path.normpath(pathlib.Path(__file__).parent.resolve())

    if not os.path.isdir(f'{current_path}/logs'):
        os.makedirs(f'{current_path}/logs')

    log_filename = f"{current_path}/logs/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] - [%(levelname)8s] - [%(funcName)12s] - %(message)s",
        handlers=[
            logging.FileHandler(log_filename, 'w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> None:
    logging_init()


if __name__ == '__main__':
    main()

    bot = GollumIzle()
    bot.run(DISCORD_TOKEN)
