# !/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
import logging
import random
import re
from typing import Optional, Literal

import discord
from discord import app_commands
from discord.ext import commands
from mcstatus import JavaServer
from src.utils import command_logger
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_ID: str = os.environ['DISCORD_ID']


async def get_servers(filepath: str) -> set[str, ...]:
    with open(filepath, 'r', encoding='utf-8') as file:
        # Json file must be : {"servers": ["S1", "S2", ...]}
        return set(json.load(file).get('servers'))


async def is_valid(addr: str) -> bool:
    """Validate if a Minecraft server is online given its address"""
    if ':25565' in addr:
        addr = addr.replace(':25565', '')
    try:
        assert JavaServer.lookup(addr).status().latency
        return True
    except Exception:
        pass
    return False


async def pick_random_servers(_servers: set[str, ...], count: int = 1, only_digits: bool = False) -> list[str, ...]:
    chosen_servers: list[str, ...] = []

    if only_digits:
        # Define a regex pattern to match valid IPs - just digits and dots
        ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
        # Filter the IPs based on the pattern
        filtered_ips = list(filter(ip_pattern.match, _servers))
        while len(chosen_servers) < count:
            rand_serv: str = random.choice(filtered_ips)
            if await is_valid(rand_serv) and rand_serv not in chosen_servers:
                chosen_servers.append(rand_serv)

    while len(chosen_servers) < count:
        rand_serv: str = random.choice(list(_servers))
        if await is_valid(rand_serv) and rand_serv not in chosen_servers:
            chosen_servers.append(rand_serv)

    if not chosen_servers or len(chosen_servers) != count or None in chosen_servers:
        logging.error(f'chosen_servers = {chosen_servers}')
        raise Exception('chosen_servers is not valid')
    return chosen_servers


async def get_embed(ctx: discord.Interaction, picks: list[str, ...]) -> discord.Embed:
    # TODO check root `picks` not empty of has None init
    embed = discord.Embed(
        title=('RANDOM MINECRAFT SERVERS' if len(picks) > 1 else 'RANDOM MINECRAFT SERVER'),
        description=('Here you have a list of **online** Minecraft IPs, enjoy!' if len(picks) > 1
                     else 'Here is your **online** Minecraft Ip!'),
        color=random.randint(0, 0xFFFFFF),  # Cyan
        timestamp=datetime.datetime.now(),
    )

    embed.set_author(
        name=f'{ctx.user.global_name}',
        icon_url=ctx.user.avatar.url
    )
    if len(picks) > 1:
        for index, pick in enumerate(picks):
            embed.add_field(name=f'Server {index + 1}', value=pick, inline=False)
    else:
        embed.add_field(name='Server', value=picks[0], inline=False)

    embed.set_footer(text='\u200b', icon_url='https://i.imgur.com/v39VXSP.png')
    return embed


class Randserver(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.SERVERS_FILEPATH: str = 'src/online-mc-servers.json'

    @app_commands.describe(count='Number of server ips.',
                           only_digits='Provides only ips made out of digits instead of hypixel.net for instance.',
                           ephemeral="If enabled, only you could see the bot's response.")
    @app_commands.rename(ephemeral='hidden')
    @app_commands.command(name='randserver', description="Will get you a random online minecraft server address!")
    async def randserver(self, ctx: discord.Interaction, count: Optional[Literal[1, 2, 3, 4, 5]] = 1,
                         only_digits: bool = False, ephemeral: Optional[bool] = False) -> None:

        await ctx.response.send_message("Your request is being processed, please wait...", ephemeral=ephemeral)
        try:
            servers: set[str, ...] = await get_servers(self.SERVERS_FILEPATH)
            picks: list[str, ...] = await pick_random_servers(servers, count=count, only_digits=only_digits)
            await ctx.edit_original_response(content='', embed=await get_embed(ctx, picks))
            logging.info(command_logger(self.randserver, ctx, locals(), count, only_digits, ephemeral, success=True))
            return
        except Exception as e:
            logging.error(e)
            logging.error(command_logger(self.randserver, ctx, locals(), count, only_digits, ephemeral, success=False))
        await ctx.edit_original_response(content=f'Error, please contact <@{DISCORD_ID}>!')
        logging.info(command_logger(self.randserver, ctx, locals(), count, only_digits, ephemeral, success=False))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Randserver(bot))
