import datetime
import logging
import os
import pathlib
import time
from typing import Literal

import discord
import pytz
from discord.ext import commands
from discord import app_commands

def mkdir_exported_channels(path: str):
    """
    Creates a directory: `exported_channels`
    :param path: The path of the directory
    :return: Nothing
    """
    if not os.path.isdir(path):
        os.mkdir(path)
        logging.info(f"Directory `{path}` created successfully!")


def filename(channel_name: str, extension: str) -> str:
    """
    Is doing the filename of the channel.txt.
    :param channel_name: channel name
    :param extension: .txt/.json/.csv...
    :return: Nothing
    """
    # Layout: [CHANNEL]-[YYYY-MM-DD]".EXT"
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    return f"{Export.CHANNEL_EXPORT_PATH}/{channel_name}-{date}.{extension}"


async def txt_format(ctx):
    """
    Sends a .txt file of the channel where !exp has been executed.
    :param ctx: ctx
    :return: Nothing
    """
    # Layout: [user][date][message][message_id]*

    begin = time.time()

    channel_history = ctx.channel.history(limit=None)
    channel_name = ctx.channel.name
    guild_name = ctx.guild.name
    filepath = filename(channel_name, "txt")

    equal_line = '=' * 62
    header = f"{equal_line}\nGuild: {guild_name}\nChannel: {channel_name}\n{equal_line}"
    message_count = 0

    try:
        with open(filepath, 'w+', encoding='utf-8') as f:

            f.write(header + '\n\n')
            async for msg in channel_history:
                message_count += 1
                username = msg.author.display_name
                user_tag = msg.author.discriminator
                msg_date = msg.created_at.astimezone(pytz.timezone('Europe/Paris')).strftime("%Y/%m/%d, %H:%M:%S")
                message = msg.clean_content

                line = f"[{msg_date}] {username}#{user_tag}\n{message}\n\n"
                f.write(line + '\n')

            footer = f"{equal_line}\nExported {message_count} message(s)\n{equal_line}"
            f.write(footer)

    except Exception as e:
        logging.exception(e)
        await send_file(ctx, e, begin)

    else:
        await send_file(ctx, filepath, begin)


async def csv_format(ctx):
    """Exports the channel to .csv"""
    # Layout: [AuthorID],[Author],[Tag],[Date],[Content]*
    begin = time.time()
    channel_history = ctx.channel.history(limit=None)
    channel_name = ctx.channel.name
    filepath = filename(channel_name, "csv")
    header = "AuthorID,Author,Tag,Date,Content"

    try:
        with open(filepath, 'w+', encoding='utf-8') as f:

            f.write(header + '\n')
            async for msg in channel_history:
                username = msg.author.display_name
                userid = msg.author.id
                user_tag = msg.author.discriminator
                msg_date = msg.created_at.astimezone(pytz.timezone('Europe/Paris')).strftime("%Y/%m/%d, %H:%M:%S")
                message = msg.clean_content

                line = f'"{userid}","{username}","{user_tag}","{msg_date}","{message}"'
                f.write(line + '\n')
    except Exception as e:
        logging.exception(e)
        await send_file(ctx, e, begin)
    else:
        await send_file(ctx, filepath, begin)


# async def json_format(ctx):
#     """Exports the channel to .json"""
#     # Layout: [user][date][message][message_id]*
#     begin = time.time()
#     channel_history = ctx.channel.history(limit=None)
#     channel_name = ctx.channel.name
#     filepath = filename(channel_name, "json")
#
#     try:
#         with open(filepath, 'w+', encoding='utf-8') as f:
#             for msg in channel_history:
#                 line = f""


async def send_file(ctx, path: str | Exception, begin: float):
    """
    Sends the formatted file into discord channel
    :param ctx: ctx
    :param path: path of the file
    :param begin: begin time
    :return: nothing
    """
    if type(path) is Exception:
        await ctx.followup.send(content=f'Cannot export the channel! -> {str(path)}')
    else:
        file = discord.File(path)
        runtime = round(time.time() - begin)
        await ctx.followup.send(content=f'Export done! In {runtime}s', file=file)


class Export(commands.Cog):
    PATH = os.path.normpath(pathlib.Path(__file__).parent.resolve())
    CHANNEL_EXPORT_PATH = f'{PATH}/exported_channels'

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("export.py - READY")
        mkdir_exported_channels(Export.CHANNEL_EXPORT_PATH)

    @app_commands.rename(format_='format')
    @app_commands.command(name="export", description="Exports the current text channel into a file.")
    async def export(self, ctx, format_: Literal["txt", "csv"]="txt"):

        logging.info(f"Exporting channel: {ctx.channel.name}")

        match format_:
            case "txt":
                await ctx.response.send_message("Exporting... (might take a long time)")
                await txt_format(ctx)
            case "csv":
                await ctx.response.send_message("Exporting... (might take a long time)")
                await csv_format(ctx)
            case _:
                await ctx.response.send_message(f"Invalid format! -> '{format_}'. Couldn't export the channel")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Export(bot))
