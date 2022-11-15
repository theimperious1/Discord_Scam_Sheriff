from collections import namedtuple

Match = namedtuple('Match', 'user_id user_name hash avatar_url similarity')

FlaggedUser = namedtuple('FlaggedUser', 'user_id nickname username avatar_url guild_id channel_id')
