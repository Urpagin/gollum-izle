# !/usr/bin/python
# -*- coding: utf-8 -*-

import html
import json
import logging
import os
import random
import sys
from pathlib import Path
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button
from discord.ui import View
from dotenv import load_dotenv

from src.utils import command_logger
from src.apis.minecraft_server_status_api import MinecraftServerStatusApi
from src.apis.paste_api import PasteApi
from src.apis.facts_api import FactsApi



# I can't find a way to normally import my files :/
# sys.path.append(f'{Path(__file__).parents[1]}')
# sys.path.append(f'{Path(__file__).parents[1]}\\apis')

# No import errors, it's OK
# from utils import command_logger
# from minecraft_server_status_api import MinecraftServerStatusApi
# from paste_api import PasteApi
# from facts_api import FactsApi
# solution


load_dotenv()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
PASTEBIN_TOKEN = os.environ['PASTEEE_TOKEN']
FACTS_TOKEN = os.environ['FACTS_API_TOKEN']
DISCORD_HANDLE = os.environ['DISCORD_HANDLE']

motd_ill_chars = [
    "§0", "§1", "§2", "§3", "§4", "§5",
    "§6", "§7", "§8", "§9", "§a", "§b",
    "§c", "§d", "§e", "§f", "§g", "§k",
    "§l", "§m", "§n", "§o", "§r", "*",
    "~", "`", "|"

]


def get_addr_info(addr: str) -> tuple[str, int] | tuple[None, None]:
    if not addr or not isinstance(addr, str):
        return None, None

    pair_one = addr.split(' ')
    if 1 > len(pair_one) < 2:
        if pair_one[0].isascii() and pair_one[1].isdigit():
            addr = addr.replace(' ', ':')

    if ' ' in addr:
        addr = addr.replace(' ', '')

    pair = addr.split(':')

    if not pair[0]:
        return None, None

    if not pair[0].isascii():
        return None, None

    if ' ' in pair[0]:
        pair[0].replace(' ', '')

    if len(pair) == 1:
        return pair[0], 25565

    if len(pair) == 2:
        if not pair[1].isdigit():
            return None, None
        return pair[0], int(pair[1])
    else:
        return None, None


def list_randomizer(a_list: list) -> str:
    """
    Takes a list in parameter and returns at random an item.
    :param: a_list: A list
    :return: str
    """
    try:
        return a_list[random.randint(0, len(a_list) - 1)]
    except Exception as e:
        logging.error(e)
        return ""


def motd_prettifier(motd: list, illegal_chars_list) -> str:
    """
    Takes a raw Minecraft motd with lots of weird characters (*;`;~;|;§) that can cause
    havoc if sent on Discord. (isn't aesthetic/readable)
    :param motd: list of a mc motd
    :param illegal_chars_list: list of illegal characters to ANNIHILATE
    :return: str - "prettified" motd
    """

    motd = ' '.join(motd)
    for ill_char in illegal_chars_list:
        motd = ' '.join(motd.split())
        motd = motd.replace(ill_char, "")

    return html.unescape(motd) if motd else ""


def plugins_to_pastebin(plugin_list: list):
    """Prettifies a list of plugins into a pastebin, return the pastebin's link."""
    if not plugin_list:
        return ''

    content: str = (f'There {"is" if len(plugin_list) <= 1 else "are"} {len(plugin_list)} '
                    f'{"plugin" if len(plugin_list) <= 1 else "plugins"}: \n\n')

    for index, plugin in enumerate(plugin_list):
        content += f'{index + 1}. {plugin}\n'
    return PasteApi(content, PASTEBIN_TOKEN).pastebin_url


def mods_to_pastebin(modlist: list[str, ...]) -> str:
    """Prettifies a list of mods into a pastebin, return the pastebin's link."""
    if not modlist:
        return ''

    content: str = (f'There {"is" if len(modlist) <= 1 else "are"} {len(modlist)} '
                    f'{"mod" if len(modlist) <= 1 else "mods"}: \n\n')

    for index, mod in enumerate(modlist):
        content += f'{index + 1}. {mod}\n'
    return PasteApi(content, PASTEBIN_TOKEN).pastebin_url


def players_to_pastebin(api_players: dict) -> str:
    """Returns a pastebin link with a well-formatted player list"""

    if not api_players:
        return ''
    player_online: int = api_players.get('online')
    player_max: int = api_players.get('max')
    player_list: list[str, ...] = api_players.get('list')
    player_uuids: dict = api_players.get('uuid')
    content: str = (f'There {"is" if player_online <= 1 else "are"} {player_online} out of {player_max} '
                    f'{"player" if player_max <= 1 else "players"} online:\n'
                    f'(username // uuid)\n\n')
    player_uuid_tuples = [(player, player_uuids[player]) if player_uuids
                          else (player, 'uuid not found') for player in player_list]
    for index, player_uuid in enumerate(player_uuid_tuples):
        content += f'{index + 1}. {player_uuid[0]} // {player_uuid[1]}\n'

    return PasteApi(content, PASTEBIN_TOKEN).pastebin_url


def dict_to_pastebin(a_dict: dict) -> str:
    prettified = json.dumps(a_dict, indent=4)
    return PasteApi(prettified, PASTEBIN_TOKEN).pastebin_url


def get_fact() -> str:
    """Returns a random fact"""
    try:
        fact_api = FactsApi(api_key=FACTS_TOKEN)
        fact: str = fact_api.get_fact()[0].get('fact')
        return fact
    except Exception as e:
        logging.error(f'Error getting fact: {e}')
    return 'Error, please '



def mcping_online_embed(mc_api, ctx: discord.Interaction) -> discord.Embed:
    embed = discord.Embed(
        title=f"**{mc_api.ip_input.upper()}:{mc_api.port_input}**",
        url=f"https://www.google.com/search?q={mc_api.ip_input}",
        description=get_fact(),
        color=0x00de12
        # color=0x0e2daa
    )

    embed.set_author(
        name=ctx.user.global_name,
        icon_url=ctx.user.avatar.url
    )

    embed.set_thumbnail(url=mc_api.icon_link)

    embed.add_field(name="Status", value=":white_check_mark: Online", inline=False)

    if mc_api.motd:
        embed.add_field(name="Motd", value=motd_prettifier(mc_api.motd.get('clean'), motd_ill_chars), inline=False)
    if mc_api.players:
        _players_online = "{:,}".format(mc_api.players.get('online'))
        _players_max = "{:,}".format(mc_api.players.get('max'))
        embed.add_field(name="Players", value=f"{_players_online} / {_players_max}", inline=False)
    if mc_api.version or mc_api.software:
        version = mc_api.version if mc_api.version else ''
        software = mc_api.software if mc_api.software else ''
        embed.add_field(name="Version", value=f"{software} {version}", inline=False)
    if mc_api.plugins:
        embed.add_field(name="Plugins", value=plugins_to_pastebin(mc_api.plugins.get('raw')), inline=False)
    if mc_api.mods:
        embed.add_field(name="Mods", value=mods_to_pastebin(mc_api.mods.get('raw')), inline=False)
    if mc_api.players:
        if 'list' in mc_api.players:
            embed.add_field(name="Player-list", value=players_to_pastebin(mc_api.players), inline=False)
    if mc_api.map:
        embed.add_field(name="Map", value=mc_api.map, inline=False)
    if mc_api.info:
        embed.add_field(name="Info", value=motd_prettifier(mc_api.info.get('clean'), motd_ill_chars), inline=False)
    if mc_api.hostname:
        embed.add_field(name="Hostname", value=mc_api.hostname, inline=False)
    if mc_api.ip:
        embed.add_field(name="Ip", value=mc_api.ip, inline=False)
    if mc_api.port:
        embed.add_field(name="Port", value=mc_api.port, inline=False)
    if mc_api.protocol:
        embed.add_field(name="Protocol", value=mc_api.protocol, inline=False)
    if mc_api.debug:
        embed.add_field(name="Debug", value=dict_to_pastebin(mc_api.debug), inline=False)

    return embed


def mcping_offline_embed(mc_api, ctx: discord.Interaction) -> discord.Embed:
    embed = discord.Embed(
        title=f"**{mc_api.ip_input.upper()}:{mc_api.port_input}**",
        url=f"https://www.google.com/search?q={mc_api.ip_input}",
        description="Cannot reach the Minecraft server.",
        color=0xff0000
    )
    embed.set_author(name=ctx.user.global_name, icon_url=ctx.user.avatar.url)
    embed.set_thumbnail(url="https://i.ibb.co/G7kvVzx/Bedrock.webp")

    embed.add_field(name="Status", value=":no_entry_sign: Offline", inline=False)
    if mc_api.ip:
        embed.add_field(name="Ip", value=mc_api.ip, inline=False)
    if mc_api.port:
        embed.add_field(name="Port", value=mc_api.port, inline=False)
    if mc_api.hostname:
        embed.add_field(name="Hostname", value=mc_api.hostname, inline=False)
    embed.set_footer(text=f"If you think this is abnormal please contact {DISCORD_HANDLE}.")

    return embed


def add_json_button(mc_api) -> discord.ui.View:
    button = Button(label="Full Json", url=dict_to_pastebin(mc_api.raw_data), emoji='🔧')

    view = View()
    view.add_item(button)

    return view


class Mcping(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.describe(address="Enter a Minecraft server ip. ('<SERVERIP>' or '<SERVERIP>:<PORT>')",
                           ephemeral="If enabled, only you could see the bot's response.")
    @app_commands.rename(ephemeral='hidden')
    @app_commands.command(name="mcping", description="Shows useful information about a Minecraft server")
    async def mcping(self, interaction: discord.Interaction, address: str,
                     ephemeral: Optional[bool] = False) -> None:
        await interaction.response.send_message("Your request is being processed, please wait...",
                                                ephemeral=ephemeral)
        ip, port = get_addr_info(address)
        print(f"ip: {ip}, port: {port}")
        if not ip or not port:
            await interaction.edit_original_response(content="The provided arguments were not valid, command aborted.")
            logging.info(command_logger(self.mcping, interaction, locals(), address, ephemeral, success=False))
            return
        mc_api = MinecraftServerStatusApi(ip, port)

        if mc_api.online:
            embed = mcping_online_embed(mc_api, interaction)
            view = add_json_button(mc_api)
            await interaction.edit_original_response(content='\u2068', embed=embed, view=view)
            logging.info(command_logger(self.mcping, interaction, locals(), address, ephemeral))
        else:
            embed = mcping_offline_embed(mc_api, interaction)
            view = add_json_button(mc_api)
            await interaction.edit_original_response(content='\u2068', embed=embed, view=view)
            logging.info(command_logger(self.mcping, interaction, locals(), address, ephemeral, success=False))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Mcping(bot))
