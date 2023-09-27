import asyncio
from datetime import datetime
from os import path
from pyrogram import Client, filters
from pyrogram import types
import csv
import configparser

from pyrogram.enums import UserStatus

# в файл config.ini потрібно вписати api_id, api_hash, та дані для проксі.

config = configparser.ConfigParser()
config.read("config.ini")
app = Client("account", api_id=int(config["pyrogram"]["api_id"]), api_hash=config["pyrogram"]["api_hash"])

key_words: set[str] = {"test", "test2", "test3"}


async def get_entity_id(url: str) -> int:
    """
    Get the entity ID from a given URL.

    Args:
        url (str): The URL to extract the entity ID from.

    Returns:
        int: The extracted entity ID.
    """
    try:
        chat_info = await app.get_chat(url)
        return chat_info.id
    except Exception as ex:
        print(ex)


async def get_chat_name(message: types.Message):
    return message.text.split()[1].split("/")[-1]


@app.on_message(filters.command("tag_all", prefixes=["/", "."]))
async def tag_all(client: Client, message: types.Message):

    """Example of command: /tag_all https://t.me/test Message to send"""

    chat_name = await get_chat_name(message=message)
    chat_id = await get_entity_id(url=chat_name)
    message_to_send = message.text.split(maxsplit=2)[-1]
    chat_members = client.get_chat_members(chat_id=chat_id)
    tag_message = ""
    async for member in chat_members:
        tag_message += f"@{member.user.username} "

    try:
        tag_message_id = (await client.send_message(chat_id=chat_id, text=f"{message_to_send} {tag_message}")).id
        await client.edit_message_text(chat_id=chat_id, text=message_to_send, message_id=tag_message_id)
    except Exception as e:
        print(e)


@app.on_message(filters.command("tag_active", prefixes=["/", "."]))
async def tag_active(client: Client, message: types.Message):

    """Example of command: /tag_active https://t.me/test Message to send"""

    chat_name = await get_chat_name(message=message)
    chat_id = await get_entity_id(url=chat_name)
    message_to_send = message.text.split(maxsplit=2)[-1]
    chat_members = client.get_chat_members(chat_id=chat_id)
    tag_message = ""
    async for member in chat_members:
        if member.user.status in (UserStatus.RECENTLY, UserStatus.LAST_MONTH, UserStatus.LAST_WEEK, UserStatus.ONLINE):
            tag_message += f"@{member.user.username} "

    try:
        tag_message_id = (await client.send_message(chat_id=chat_id, text=f"{message_to_send} {tag_message}")).id
        await client.edit_message_text(chat_id=chat_id, text=message_to_send, message_id=tag_message_id)
    except Exception as e:
        print(e)


@app.on_message(filters.command("tag_by_keywords", prefixes=["/", "."]))
async def tag_by_keywords(client: Client, message: types.Message):

    """
    Example of command: /tag_by_keywords https://t.me/test 30 Message to send
    third argument - limit messages
    """

    chat_name = await get_chat_name(message=message)
    chat_id = await get_entity_id(url=chat_name)
    limit_messages = int(message.text.split()[2])
    message_to_send = message.text.split(maxsplit=3)[-1]
    message_history = client.get_chat_history(chat_id=chat_id, limit=limit_messages)
    tag_message = ""
    usernames = []
    async for m in message_history:
        for keyword in key_words:
            if keyword in m.text:
                if m.from_user.username not in usernames:
                    usernames.append(m.from_user.username)
    for username in usernames:
        tag_message += f"@{username} "

    try:
        tag_message_id = (await client.send_message(chat_id=chat_id, text=f"{message_to_send} {tag_message}")).id
        await client.edit_message_text(chat_id=chat_id, text=message_to_send, message_id=tag_message_id)
    except Exception as e:
        print(e)


@app.on_message(filters.command("tag_by_date", prefixes=["/", "."]))
async def tag_by_keywords(client: Client, message: types.Message):

    """
    Example of command: /tag_by_keywords https://t.me/test 30 Message to send
    third argument - limit messages
    fourth argument - date in format 20.09.2023 (d.m.y)
    """

    chat_name = await get_chat_name(message=message)
    chat_id = await get_entity_id(url=chat_name)
    limit_messages = int(message.text.split()[2])
    last_activity_date = datetime.strptime(message.text.split()[3], "%d.%m.%Y").date()
    message_to_send = message.text.split(maxsplit=4)[-1]
    message_history = client.get_chat_history(chat_id=chat_id, limit=limit_messages)
    tag_message = ""
    usernames = []
    async for m in message_history:
        message_date = m.date.date()
        if last_activity_date == message_date:
            if m.from_user.username not in usernames:
                usernames.append(m.from_user.username)

    for username in usernames:
        tag_message += f"@{username} "

    try:
        tag_message_id = (await client.send_message(chat_id=chat_id, text=f"{message_to_send} {tag_message}")).id
        await asyncio.sleep(0.5)
        await client.edit_message_text(chat_id=chat_id, text=message_to_send, message_id=tag_message_id)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    app.run()
