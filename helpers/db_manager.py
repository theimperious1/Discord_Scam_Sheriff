""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.3
"""
import time
from models.server_configuration import ServerConfiguration
import aiosqlite


async def is_blacklisted(user_id: int) -> bool:
    """
    This function will check if a user is blacklisted.

    :param user_id: The ID of the user that should be checked.
    :return: True if the user is blacklisted, False if not.
    """
    async with aiosqlite.connect("database/database.db") as db:
        async with db.execute("SELECT * FROM blacklist WHERE user_id=?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None


async def add_user_to_blacklist(user_id: int) -> int:
    """
    This function will add a user based on its ID in the blacklist.

    :param user_id: The ID of the user that should be added into the blacklist.
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("INSERT INTO blacklist(user_id) VALUES (?)", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def remove_user_from_blacklist(user_id: int) -> int:
    """
    This function will remove a user based on its ID from the blacklist.

    :param user_id: The ID of the user that should be removed from the blacklist.
    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute("DELETE FROM blacklist WHERE user_id=?", (user_id,))
        await db.commit()
        rows = await db.execute("SELECT COUNT(*) FROM blacklist")
        async with rows as cursor:
            result = await cursor.fetchone()
            return result[0] if result is not None else 0


async def blacklist_pfp(server_id: int, user_id: int, user_name: str, img_hash: int, avatar_url: str) -> bool:
    """

    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute(
            "INSERT INTO pfp_blacklist(server_id, user_id, user_name, hash, avatar_url, timestamp) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
            (str(server_id), str(user_id), user_name, str(img_hash), avatar_url, str(time.time())))
        await db.commit()
        return True


async def get_blacklisted_pfps(server_id: int) -> list:
    async with aiosqlite.connect("database/database.db") as db:
        rows = await db.execute('SELECT hash FROM pfp_blacklist WHERE server_id = {0}'.format(str(server_id)))
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(row[0])
            return result_list


async def blacklist_username(server_id: int, user_name: str) -> bool:
    """

    """
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute(
            "INSERT INTO name_blacklist(server_id, username, timestamp) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
            (str(server_id), user_name, str(time.time())))
        await db.commit()
        return True


async def get_blacklisted_usernames(server_id: int) -> list:
    async with aiosqlite.connect("database/database.db") as db:
        rows = await db.execute('SELECT username FROM name_blacklist WHERE server_id = {0}'.format(str(server_id)))
        async with rows as cursor:
            result = await cursor.fetchall()
            result_list = []
            for row in result:
                result_list.append(row[0])
            return result_list


async def set_config_option(server_id: int, options: tuple) -> bool:
    async with aiosqlite.connect("database/database.db") as db:
        await db.execute(
            "UPDATE server_configurations SET {0} = ?, updated_on = ? WHERE server_id = ?".format(options[0]),
            (options[1], time.time(), str(server_id)))
        await db.commit()
        return True


async def get_config_options() -> dict:
    async with aiosqlite.connect("database/database.db") as db:
        rows = await db.execute('SELECT * FROM server_configurations')
        async with rows as cursor:
            result = await cursor.fetchall()
            result_dict = {}
            for row in result:
                result_dict[row[0]] = ServerConfiguration(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            return result_dict


async def init_config(server_id: int, output_channel_id: int, monitor_channel_id: int) -> bool:
    """

    """
    async with aiosqlite.connect("database/database.db") as db:
        now = time.time()
        await db.execute(
            "INSERT INTO server_configurations(server_id, output_channel_id, monitor_channel_id, welcome_trigger_phrase, action_mode_pfp, action_mode_username, matching_enabled, created_on, updated_on) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
            (str(server_id), str(output_channel_id), str(monitor_channel_id), 'INITIAL_PHRASE', 'warn', 'warn', True, now, now))
        await db.commit()
        return True
