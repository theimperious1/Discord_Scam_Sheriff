""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.3
"""
import traceback

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks, db_manager
from helpers.utils import fetch_media, diff_hash


class Moderation(commands.Cog, name="moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="set_output_channel",
        description="Sets the channel for outputting matches",
    )
    @commands.has_permissions(administrator=True)
    @checks.not_blacklisted()
    @app_commands.describe(channel="The channel that I should output matches to.")
    async def set_output_channel(self, context: Context, channel: discord.TextChannel) -> None:
        """
        Sets the output channel for ban notifications.

        :param context: The hybrid command context.
        :param channel: The channel that I should output logs to.
        """
        try:
            result = await db_manager.set_config_option(context.guild.id, ('output_channel_id', channel.id))
            if not result:
                raise Exception(f'Error occurred when setting output channel: {context.guild.name}')
            embed = discord.Embed(
                title="Success!",
                description="The match output channel has been successfully set! :)",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        except:
            traceback.print_exc()
            embed = discord.Embed(
                title="Uh Oh!",
                description="An error occurred while trying to set the output channel. Make sure I have the appropriate permissions!",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="set_monitor_channel",
        description="Sets the welcome channel to monitor for matching users",
    )
    @commands.has_permissions(administrator=True)
    @checks.not_blacklisted()
    @app_commands.describe(channel="The channel that Scam Sheriff should monitor for matches")
    async def set_monitor_channel(self, context: Context, channel: discord.TextChannel) -> None:
        """
        Sets the channel that Scam Sheriff should monitor for matches.

        :param context: The hybrid command context.
        :param channel: The channel that I should output logs to.
        """
        try:
            result = await db_manager.set_config_option(context.guild.id, ('monitor_channel_id', channel.id))
            if not result:
                raise Exception  # TODO: Make sure this works

            embed = discord.Embed(
                title="Success!",
                description="The monitor channel has been successfully set! :)",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        except:
            traceback.print_exc()
            embed = discord.Embed(
                title="Uh Oh!",
                description="An error occurred while trying to set the monitor channel. Make sure I have the appropriate permissions!",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="blacklist_pfp",
        description="Lets you blacklist a users profile picture from being used to join the server again.",
    )
    @commands.has_permissions(administrator=True)
    @checks.not_blacklisted()
    @app_commands.describe(user="The target user")
    async def blacklist_profile_picture(self, context: Context, user: discord.User) -> None:
        """
        Sets the channel that Scam Sheriff should monitor for matches.

        :param context: The hybrid command context.
        :param user: The user that we want to blacklist.
        """
        try:
            avatar_url = user.display_avatar.url
            if media := fetch_media(avatar_url):
                img_hash = diff_hash(media)
                await db_manager.blacklist_pfp(context.guild.id, user.id, user.name, img_hash, avatar_url)
            embed = discord.Embed(
                title="Success!",
                description=f"{user.name} has been blacklisted via magical means!\n"
                            "They won't be able to join again using that profile picture.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        except:
            traceback.print_exc()
            embed = discord.Embed(
                title="Uh Oh!",
                description="An error occurred while trying to blacklist the user. Make sure I have the appropriate permissions!",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="blacklist_username",
        description="Lets you blacklist a users username or nickname from being used to join the server again.",
    )
    @commands.has_permissions(administrator=True)
    @checks.not_blacklisted()
    @app_commands.describe(user="The target user")
    async def blacklist_username(self, context: Context, user: discord.User) -> None:
        """
        Sets the channel that Scam Sheriff should monitor for matches.

        :param context: The hybrid command context.
        :param user: The user that we want to blacklist.
        """
        try:
            await db_manager.blacklist_username(context.guild.id, user.name)
            embed = discord.Embed(
                title="Success!",
                description=f"{user.name} has been blacklisted via mysterious means!\n"
                            "No one will be able to join again using their username.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        except:
            traceback.print_exc()
            embed = discord.Embed(
                title="Uh Oh!",
                description="An error occurred while trying to blacklist the user. Make sure I have the appropriate permissions!",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="set_action_mode",
        description='Set the action mode to either "warn" or "autoban".',
    )
    @commands.has_permissions(administrator=True)
    @checks.not_blacklisted()
    @app_commands.describe(action_type='The type of action mode. Either "username" or "picture"',
                           mode='The action mode. Either "warn" or "autoban"')
    async def set_action_mode(self, context: Context, action_type: str, mode: str) -> None:
        """
        Sets the action modes that Scam Sheriff should use.

        :param context: The hybrid command context.
        :param action_type The action type we want to set
        :param mode: The action mode that we want to set.
        """
        try:
            if (action_type != 'picture' and action_type != 'username') or (mode != 'warn' and mode != 'autoban'):
                raise Exception(f'User used invalid action or mode type when setting action mode: {action_type}:{mode}')

            if action_type == 'picture':
                action = 'action_mode_pfp'
                self.bot.server_configs[str(context.guild.id)].set_action_mode_pfp(mode)
            else:
                action = 'action_mode_username'
                self.bot.server_configs[str(context.guild.id)].set_action_mode_username(mode)

            await db_manager.set_config_option(context.guild.id, (action, mode))

            embed = discord.Embed(
                title="Success!",
                description=f"{action_type} action mode has been set to {mode}!",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        except:
            traceback.print_exc()
            embed = discord.Embed(
                title="Uh Oh!",
                description='An error occurred while trying to set the action mode.',
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="set_trigger_phrase",
        description='Set the phrase that triggers scanning users',
    )
    @commands.has_permissions(administrator=True)
    @checks.not_blacklisted()
    @app_commands.describe(
        phrase='The phrase to trigger. E.g "Welcome to MyServerName" where the end would contain a @username.')
    async def set_trigger_phrase(self, context: Context, phrase: str) -> None:
        """
        Sets the trigger phrase that Scam Sherrif should use.

        :param context: The hybrid command context.
        :param phrase The trigger phrase
        """
        try:
            self.bot.server_configs[str(context.guild.id)].set_welcome_trigger_phrase(phrase)
            await db_manager.set_config_option(context.guild.id, ('welcome_trigger_phrase', phrase))

            embed = discord.Embed(
                title="Success!",
                description=f'The trigger phrase has been set to "{phrase}"',
                color=0xE02B2B
            )
            await context.send(embed=embed)

        except:
            traceback.print_exc()
            embed = discord.Embed(
                title="Uh Oh!",
                description='An error occurred while trying to set the trigger phrase.',
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="toggle_bot",
        description='This command toggles the bot on or off per server.',
    )
    @commands.has_permissions(administrator=True)
    @checks.not_blacklisted()
    @app_commands.describe(status='The status you want the bot to be in. Either on, or off.')
    async def toggle_bot(self, context: Context, status: str) -> None:
        """
        This command toggles Scam Sheriff on or off per server.

        :param context: The hybrid command context.
        :param status: The toggle status
        """
        status = status.lower()
        try:
            if status != "on" and status != "off":
                raise Exception(f'Someone attempted to set Scam Sheriff to a value other than on or off: {status}')
            status_value = True if status == "on" else False

            self.bot.server_configs[str(context.guild.id)].set_matching_enabled(status_value)
            await db_manager.set_config_option(context.guild.id, ('matching_enabled', status_value))

            embed = discord.Embed(
                title="Success!",
                description=f"Scam Sheriff has been turned {status}.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        except:
            traceback.print_exc()
            embed = discord.Embed(
                title="Uh Oh!",
                description="An error occurred while trying to toggle Scam Sheriff on or off.",
                color=0xE02B2B
            )
            await context.send(embed=embed)


    @commands.hybrid_command(
        name="configure_name_blacklist",
        description='Configure whether nicknames, usernames, or both should be checked against the blacklist.',
    )
    @commands.has_permissions(administrator=True)
    @checks.not_blacklisted()
    @app_commands.describe(status='Either "nicknames", "usernames", or "both".')
    async def configure_name_blacklist(self, context: Context, status: str) -> None:
        """
        Configure how Scam Sheriff handles the name blacklist.

        :param context: The hybrid command context.
        :param status: The toggle status
        """
        status = status.lower()
        try:
            if status != "nicknames" and status != "usernames" and status != "both":
                raise Exception("Someone attempted to configure Scam Sheriff's name "
                                f"blacklist mode to a value other than the defined ones: {status}")
            self.bot.server_configs[str(context.guild.id)].set_name_blacklist_mode(status)
            await db_manager.set_config_option(context.guild.id, ('name_blacklist_mode', status))
            embed = discord.Embed(
                title="Success!",
                description=f'Scam Sheriff\'s name blacklist has been configured to "{status}"',
                color=0xE02B2B
            )
            await context.send(embed=embed)

        except:
            traceback.print_exc()
            embed = discord.Embed(
                title="Uh Oh!",
                description="An error occurred while trying to configure the name blacklist mode.",
                color=0xE02B2B
            )
            await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
