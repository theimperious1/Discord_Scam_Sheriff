import traceback

from models.data_classes import Match
from typing import Union
import discord
from helpers.utils import fetch_media, diff_hash, send_embed

default_pfp_hashes = ['18289040487109922684', '18289040452749660028']  # TODO: Don't forget finishing this!


class Blacklister:

    def __init__(self, bot, db_manager):
        self.bot = bot
        self.db_manager = db_manager

    async def do_all(self, user: discord.Member, guild: discord.Guild,
                     output_channel: discord.TextChannel = None) -> tuple:
        username_check_passed = await self.check_username(user, guild)
        print(username_check_passed)
        if not username_check_passed:
            await self.punish_blacklisted_username(user, guild, output_channel)

        matches = await self.check_avatar(user, guild)
        avatar_check_passed = matches is None

        if not avatar_check_passed:
            await self.punish_blacklisted_pfp(user, guild, output_channel, matches)

        return username_check_passed, avatar_check_passed

    async def check_username(self, user: discord.Member, guild: discord.Guild) -> bool:
        banned_usernames = await self.db_manager.get_blacklisted_usernames(guild.id)
        username_mode = self.bot.server_configs[str(guild.id)].get_name_blacklist_mode()
        print(username_mode)
        print(user.name)
        print(user.nick)
        if (username_mode == 'usernames' or username_mode == 'both') and user.name in banned_usernames:
            return False

        if (username_mode == 'nicknames' or username_mode == 'both') and user.nick in banned_usernames:
            return False
        return True

    async def check_avatar(self, user: discord.Member, guild: discord.Guild) -> Union[list, None]:
        avatar_url = user.display_avatar.url
        if media := fetch_media(avatar_url):
            img_hash = diff_hash(media)
            if img_hash in default_pfp_hashes:
                return

            img_hashes = await self.db_manager.get_blacklisted_pfps(guild.id)

            def get_matches():
                for item in img_hashes:
                    compared = int(((64 - bin(img_hash ^ int(item)).count('1')) * 100.0) / 64.0)
                    if compared >= 95:
                        yield Match(user.id, user.name, img_hash, avatar_url, compared)

            matches = [*get_matches()]
            if len(matches) >= 1:
                return matches
            return

    async def punish_blacklisted_username(self, user: discord.Member, guild: discord.Guild,
                                          output_channel: discord.TextChannel) -> None:
        auto_ban = self.bot.server_configs[str(guild.id)].get_action_mode_username() == 'autoban'
        await send_embed(discord, 'WARNING! This account matches a banned username!',
                         description=f'**ID**: {user.id}\n'
                                     f'**Name**: {user.name}\n'
                                     f'**Nickname**: {user.nick}\n'
                                     f'**Auto-banned**: {"true" if auto_ban else "false"}',
                         output_channel=output_channel)

        if auto_ban:
            await guild.ban(user,
                            reason=f'Banned by {self.bot.config["bot_name"]} for having a blacklisted username',
                            delete_message_seconds=3600)

    async def punish_blacklisted_pfp(self, user: Union[discord.User, discord.Member], guild: discord.Guild,
                                     output_channel: discord.TextChannel,
                                     matches: list) -> None:
        msg = 'This users profile picture matches to {0} banned users.'.format(len(matches))
        auto_ban = self.bot.server_configs[str(guild.id)].get_action_mode_pfp() == 'autoban'
        await send_embed(discord, msg,
                         description=f'**ID**: {user.id}\n'
                                     f'**Name**: {user.name}\n'
                                     f'**Nickname**: {user.nick}\n'
                                     f'**Avatar URL**: {user.display_avatar}\n'
                                     f'**Auto-banned**: {"true" if auto_ban else "false"}',
                         output_channel=output_channel)

        if auto_ban:
            await guild.ban(user,
                            reason=f'Banned by {self.bot.config["bot_name"]} for having a blacklisted profile picture',
                            delete_message_seconds=3600)
