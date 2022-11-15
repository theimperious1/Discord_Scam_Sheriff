"""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.3

Discord-PFP-Blacklist-Bot by theimperious1 using Krypton's fabulous template!
"""

import asyncio
import json
import os
import platform
import random
import sys
import time
import traceback
from blacklister import Blacklister
from helpers import db_manager
import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from models.server_configuration import ServerConfiguration

import exceptions

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

"""	
Setup bot intents (events restrictions)
For more information about intents, please go to the following websites:
https://discordpy.readthedocs.io/en/latest/intents.html
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents


Default Intents:
intents.bans = True
intents.dm_messages = True
intents.dm_reactions = True
intents.dm_typing = True
intents.emojis = True
intents.emojis_and_stickers = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_scheduled_events = True
intents.guild_typing = True
intents.guilds = True
intents.integrations = True
intents.invites = True
intents.messages = True # `message_content` is required to get the content of the messages
intents.reactions = True
intents.typing = True
intents.voice_states = True
intents.webhooks = True

Privileged Intents (Needs to be enabled on developer portal of Discord), please use them only if you need them:
intents.members = True
intents.message_content = True
intents.presences = True
"""

intents = discord.Intents.default()

"""
Uncomment this if you don't want to use prefix (normal) commands.
It is recommended to use slash commands and therefore not use prefix commands.

If you want to use prefix commands, make sure to also enable the intent below in the Discord developer portal.
"""
intents.message_content = True
intents.members = True

bot = Bot(command_prefix=commands.when_mentioned_or(
    config["prefix"]), intents=intents, help_command=None)

blacklist = Blacklister(bot, db_manager)


async def init_db():
    async with aiosqlite.connect("database/database.db") as db:
        with open("database/schema.sql") as file:
            await db.executescript(file.read())
        await db.commit()


async def load_configs():
    bot.server_configs = await db_manager.get_config_options()
    print('Loaded server configurations')


"""
Create a bot variable to access the config file in cogs so that you don't need to import it every time.

The config is available using the following code:
- bot.config # In this file
- self.bot.config # In cogs
"""
bot.config = config
bot.server_configs = None


@bot.event
async def on_ready() -> None:
    """
    The code in this event is executed when the bot is ready
    """
    print(f"Logged in as {bot.user.name}")
    print(f"discord.py API version: {discord.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()
    if config["sync_commands_globally"]:
        print("Syncing commands globally...")
        await bot.tree.sync()


@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    """
    The code in this event is executed every time the bot has joined a new server.
    It initializes a configuration for that server and logs the event.
    :param guild: The guild that the bot has joined
    """
    try:
        await db_manager.init_config(guild.id, 0, 0)
        now = time.time()
        bot.server_configs[str(guild.id)] = ServerConfiguration(
            guild.id, 0, 0, 'INITIAL_PHRASE', 'warn', 'warn', 'both', True, now, now)
        print(f'{config["bot_name"]} has joined a new guild called {guild.name}!')

    except:
        traceback.print_exc()


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if not bot.server_configs[str(after.guild.id)].get_matching_enabled() != 1:
        return
    print('Member updated: Checking blacklist...')
    now = time.time()
    if (now - before.joined_at.timestamp()) <= (86400 * 7):  # 7 days
        output_channel_id = int(bot.server_configs[str(after.guild.id)].get_output_channel_id())
        output_channel = bot.get_channel(output_channel_id)
        username_check_passed, avatar_check_passed = await blacklist.do_all(after, after.guild, output_channel)
        if not username_check_passed or not avatar_check_passed:
            print(f'Member failed blacklist check during member update on: {after.guild.name}')


@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Setup the game status task of the bot
    """
    statuses = ["How To Catch a Scammer", "Toss the Scammer", "with kittens"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    The code in this event is executed every time someone sends a message, with or without the prefix

    :param message: The message that was sent.
    """

    if message.author == bot.user or message.author.bot:
        return

    if bot.server_configs[str(message.guild.id)].get_matching_enabled() != 1:
        return

    monitor_channel_id = int(bot.server_configs[str(message.guild.id)].get_monitor_channel_id())
    trigger_phrase = bot.server_configs[str(message.guild.id)].get_welcome_trigger_phrase()
    if message.channel.id == monitor_channel_id and message.content.startswith(trigger_phrase):
        # TODO: Make sure user is guide/mod/team. Ok. And get the user that the person saying "banned" is replying to
        #  We only check for ban permissions. Maybe need more?
        output_channel_id = int(bot.server_configs[str(message.guild.id)].get_output_channel_id())
        output_channel = bot.get_channel(output_channel_id)

        user = bot.get_guild(message.guild.id).get_member(message.author.id)
        username_check_passed, avatar_check_passed = await blacklist.do_all(user, message.guild, output_channel)
        if not username_check_passed or not avatar_check_passed:
            print(f'User failed blacklist check on {message.guild.name}.')
    else:
        await bot.process_commands(message)


@bot.event
async def on_command_completion(context: Context) -> None:
    """
    The code in this event is executed every time a normal command has been *successfully* executed
    :param context: The context of the command that has been executed.
    """
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if context.guild is not None:
        print(
            f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})")
    else:
        print(
            f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs")


@bot.event
async def on_command_error(context: Context, error) -> None:
    """
    The code in this event is executed every time a normal valid command catches an error
    :param context: The context of the normal command that failed executing.
    :param error: The error that has been faced.
    """
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            title="Hey, please slow down!",
            description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserBlacklisted):
        """
        The code here will only execute if the error is an instance of 'UserBlacklisted', which can occur when using
        the @checks.not_blacklisted() check in your command, or you can raise the error by yourself.
        """
        embed = discord.Embed(
            title="Error!",
            description="You are blacklisted from using the bot.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserNotOwner):
        """
        Same as above, just for the @checks.is_owner() check.
        """
        embed = discord.Embed(
            title="Error!",
            description="You are not the owner of the bot!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="You are missing the permission(s) `" + ", ".join(
                error.missing_permissions) + "` to execute this command!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            # We need to capitalize because the command arguments have no capital letter in the code.
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await context.send(embed=embed)
    raise error


async def load_cogs() -> None:
    """
    The code in this function is executed whenever the bot will start.
    """
    for file in os.listdir(f"./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")


asyncio.run(init_db())
asyncio.run(load_configs())
asyncio.run(load_cogs())
bot.run(config["token"])
