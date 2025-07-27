# !/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
import sys
from pathlib import Path
from typing import Literal
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
#
# sys.path.append(f'{Path(__file__).parents[1]}')
# sys.path.append(f'{Path(__file__).parents[1]}\\apis')
# from latest_api import LatestApi
# from utils import command_logger

# from apis.latest_api import LatestApi

from src.utils import command_logger
from src.apis.latest_api import LatestApi


def make_embed(latest_obj: LatestApi) -> discord.Embed:
    """Creates the embed"""
    noun = 'video' if len(latest_obj.video_titles) <= 1 else 'videos'

    embed = discord.Embed(
        title=f"**{latest_obj.channel_name}**",
        url=f"https://www.youtube.com/channel/{latest_obj.channel_id}",
        description=f"Here's the latest {noun} from **{latest_obj.channel_name}**",
        timestamp=datetime.datetime.now(),
        color=0x189216,
    )

    embed.set_author(
        name=latest_obj.ctx.user.name,
        icon_url=latest_obj.ctx.user.avatar.url
    )

    embed.set_thumbnail(url=latest_obj.channel_icon)

    for i in range(len(latest_obj.video_titles)):
        embed.add_field(name=latest_obj.video_titles[i], value=f"https://youtu.be/{latest_obj.video_ids[i]}",
                        inline=False)
    embed.set_footer(text='\u200b', icon_url="https://i.imgur.com/v39VXSP.png")

    return embed


class Latest(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.describe(youtuber="Enter a YouTuber", prior_to="The number of videos you want to see",
                           ephemeral="If True, the message will be sent to you only.")
    @app_commands.rename(ephemeral='hidden')
    @app_commands.command(name="latest", description="Gets the latest videos of your favorite YouTuber")
    async def latest(self, ctx: discord.Interaction, youtuber: str,
                     prior_to: Optional[Literal[1, 2, 3, 4, 5, 6, 7, 8, 9]] = 1,
                     ephemeral: Optional[bool] = False):

        latest_obj = LatestApi(youtuber, prior_to, ctx)
        embed = make_embed(latest_obj)
        if latest_obj.success:
            logging.info(command_logger(self.latest, ctx, locals(), youtuber, prior_to, ephemeral))
            await ctx.response.send_message(embed=embed, ephemeral=ephemeral)
        else:
            logging.info(command_logger(self.latest, ctx, locals(), youtuber, prior_to, ephemeral, success=False))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Latest(bot))
