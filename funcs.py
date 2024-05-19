import aiohttp
import os
import discord
from sqlalchemy import func
from models import AllowedChannels, create_channel_table
from datetime import datetime, timezone
from discord.ext import tasks


def add_channel_to_table(session, channel_id):
    existing_channel = session.query(AllowedChannels).get(channel_id)

    if not existing_channel:
        new_channel = AllowedChannels(channel_id=channel_id)
        create_channel_table(session, channel_id)
        session.add(new_channel)
        session.commit()
        return None
    else:
        return 'Channel has already been added.'


def delete_channel_from_table(session, channel_id):
    channel = session.query(AllowedChannels).get(channel_id)

    if channel:
        session.delete(channel)
        session.commit()
        return None
    else:
        return 'Channel has not been added.'


def get_channels_from_table(session):
    result = session.query(AllowedChannels.channel_id).all()
    result = [id[0] for id in result]
    return result


def get_last_message_published(session, channel_id):
    Message = create_channel_table(session, channel_id)

    last_published = session.query(func.max(Message.published)).scalar()
    if last_published:
        return last_published.replace(tzinfo=timezone.utc)
    else:
        return datetime.fromtimestamp(1420070400, timezone.utc)  # 01-01-2015 00:00:00 UTC


def add_message_to_table(session, channel_id, message_id, username, message, published, updated=None, path=None ):
    Message = create_channel_table(session, channel_id)
    existing_message = session.query(Message).get(message_id)

    if existing_message is None:
        new_message = Message(
            message_id=message_id,
            username=username,
            message=message,
            published=published,
            updated=updated,
            path=path
        )

        session.add(new_message)
        session.commit()
    else:
        print('ERROR: Message already exists.')


def update_message_in_table(session, channel_id, message_id, message, updated):
    Message = create_channel_table(session, channel_id)
    row = session.query(Message).get(message_id)

    if row:
        row.message = message
        row.updated = updated
        session.commit()
    else:
        print('ERROR: Message does not exist.')


async def save_attachments(message, base_path):
    if not message.attachments:
        return None

    attachment_paths = []
    for attachment in message.attachments:
        file_path = os.path.join(base_path, attachment.filename)
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status == 200:
                    with open(file_path, 'wb') as f:
                        f.write(await resp.read())
                    attachment_paths.append(file_path)

    return attachment_paths


async def update_messages(bot, session, config):
    channels = get_channels_from_table(session)

    LIMIT = int(config['bot']['MESSAGE_LIMIT'])

    for channel_id in channels:
        channel = bot.get_channel(channel_id)
        if channel:
            async for message in channel.history(limit=LIMIT):
                update_message_in_table(
                    session,
                    channel_id=channel.id,
                    message_id=message.id,
                    message=message.content,
                    updated=message.edited_at
                )


async def save_new_messages(session, channel, last_message_published):
    # print(f'Fetching messages after: {last_message_published}')

    async for message in channel.history(after=last_message_published):
        base_path = f'data/{channel.id}/{message.id}'
        os.makedirs(base_path, exist_ok=True)
        attachment_paths = await save_attachments(message, base_path)
        updated_at = message.edited_at if message.edited_at else None
        # print(f'Message: {message.id}, {message.content}')

        add_message_to_table(
            session,
            channel_id=channel.id,
            message_id=message.id,
            username=message.author.name,
            message=message.content,
            published=message.created_at,
            updated=updated_at,
            path=base_path if attachment_paths else None
        )
