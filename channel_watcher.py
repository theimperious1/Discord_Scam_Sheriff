from discord.ext import tasks
from models.data_classes import FlaggedUser


class ChannelMonitor:

    def __init__(self, bot, blacklist):
        self.bot = bot
        self.blacklist = blacklist
        self.monitored_channels = {}
        self.flagged_users = []

    @tasks.loop(seconds=30.0)
    async def monitor(self):
        print('MONITOR WAS CALLED')
        channels = self.bot.get_all_channels()
        monitor_channel_ids = set()
        for conf in self.bot.server_configs:
            monitor_channel_ids.add(conf[2])

        for channel in channels:
            if channel.id not in monitor_channel_ids:
                continue

            channel_id = str(channel.id)
            if channel_id not in self.monitored_channels:
                self.monitored_channels[channel_id] = {}

            async for message in channel.history(limit=100):

                if message.author.id in self.monitored_channels[channel_id]:

                    if self.monitored_channels[channel_id][message.author.id][0] != message.author.nick or \
                            self.monitored_channels[channel_id][message.author.id][1] != message.author.display_avatar.url:

                        self.flagged_users.append(FlaggedUser(
                            message.author.id, message.author.nick, message.author.name,
                            message.author.display_avatar.url, message.guild.id, channel_id
                        ))

                self.monitored_channels[channel_id][message.author.id] = (
                    message.author.nick, message.author.display_avatar.url
                )

    @tasks.loop(minutes=1.0)
    async def check_flagged_users(self):
        for _user in self.flagged_users:
            user = self.bot.get_user(_user.user_id)
            guild = self.bot.get_guild(_user.guild_id)
            username_check_passed, avatar_check_passed = await self.blacklist.do_all(user, guild)
            if not username_check_passed or not avatar_check_passed:
                del self.monitored_channels[5][user.id]

        self.flagged_users = []
