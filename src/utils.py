from typing import Callable

import discord


def command_logger(func: discord.ext.commands or Callable, ctx: discord.Interaction, locals_vars: locals(),
                   *args, success: bool = True) -> str:
    """Produces a string that documents the success or failure of a command by returning a string."""
    if success:
        if isinstance(func, Callable):
            func_name = func.__name__
        else:
            func_name = func.name
        arg_info = {}
        success = (f'Command `{func_name}` successfully executed by '
                   f'{ctx.user.global_name}#{ctx.user.discriminator} - @{ctx.user.name} -(args)-> [')

        for key, value in locals_vars.items():
            if value in args:
                arg_info.update({key: value})

        for key, value in arg_info.items():
            success += f"{key}: {value}, "

        success = success[:-2] + "]"
        return success
    else:
        if isinstance(func, Callable):
            func_name = func.__name__
        else:
            func_name = func.name
        arg_info = {}
        failure = (f'Command `{func_name}` UNSUCCESSFULLY executed by '
                   f'{ctx.user.global_name}#{ctx.user.discriminator} - @{ctx.user.name} -(args)-> [')

        for key, value in locals_vars.items():
            if value in args:
                arg_info.update({key: value})

        for key, value in arg_info.items():
            failure += f"{key}: {value}, "

        failure = failure[:-2] + "]"
        return failure
