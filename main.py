import discord
from discord.ext import commands
import os
from configobj import ConfigObj
from models import Base, connect_to_database
from funcs import (add_message_to_table, get_channels_from_table, save_attachments, update_message_in_table,
                   get_last_message_published, save_new_messages, update_messages)
from commands import (add_channel_to_tracking, delete_channel_from_tracking, show_all_channels_list,
                      change_message_update_limit, change_bot_status)


def load_config():
    return ConfigObj('config.ini', encoding='utf-8')

# config = configparser.ConfigParser()
# config.read('config.ini')
config = load_config()

intents = discord.Intents.all()
intents.guilds = True
intents.members = True
intents.presences = True
intents.message_content = True
intents.messages = True

PREFIX = config['bot']['BOT_PREFIX']
GUILD_ID = config['bot']['GUILD_ID']
STATUS = config['bot']['STATUS']

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

if config['database']['USE_ENV'].lower() == 'yes':
    ENV = config['database']['ENV_NAME']
    DATABASE_URL = (os.environ[ENV])
    print('USING ENV')

if config['database']['USE_ENV'].lower() == 'no':
    DATABASE_URL = config['database']['DATABASE_URL']


session = connect_to_database(DATABASE_URL)
Base.metadata.create_all(session.bind)

# Commands

ADD_CMD = config['commands_aliases']['add_channel']
DEl_CMD = config['commands_aliases']['delete_channel']
CFG_SET_LIM_CMD = config['commands_aliases']['config_set_message_update_limit']
CFG_SET_STATUS_CMD = config['commands_aliases']['config_set_bot_status']

add_channel_to_tracking(bot, session, ADD_CMD)
delete_channel_from_tracking(bot, session, DEl_CMD)
show_all_channels_list(bot, session)
change_message_update_limit(bot, CFG_SET_LIM_CMD, config)
change_bot_status(bot, CFG_SET_STATUS_CMD, config)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    channels = get_channels_from_table(session)

    if channels:
        for channel_id in channels:
            last_message_published = get_last_message_published(session, channel_id)
            channel = bot.get_channel(channel_id)

            await bot.loop.create_task(save_new_messages(session, channel, last_message_published))

    await bot.loop.create_task(update_messages(bot, session, config))
    await bot.change_presence(activity=discord.Game(name=STATUS))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if GUILD_ID and message.guild.id != int(GUILD_ID):
        return

    channels = get_channels_from_table(session)

    if message.channel.id in channels:
        base_path = f'data/{message.channel.id}/{message.id}'
        os.makedirs(base_path, exist_ok=True)
        attachment_paths = await save_attachments(message, base_path)

        add_message_to_table(
            session,
            channel_id=message.channel.id,
            message_id=message.id,
            username=message.author.name,
            message=message.content,
            published=message.created_at,
            path=base_path if attachment_paths else None
        )

    await bot.process_commands(message)


@bot.event
async def on_raw_message_edit(payload):
    channel_id = payload.channel_id
    message_id = payload.message_id

    if channel_id and message_id:
        channel = bot.get_channel(channel_id)
        if channel:
            message = await channel.fetch_message(message_id)
            if message and message.author != bot.user:
                channels = get_channels_from_table(session)

                if channel_id in channels:
                    update_message_in_table(
                        session,
                        channel_id=channel_id,
                        message_id=message_id,
                        message=message.content,
                        updated=message.edited_at
                    )


if config['api']['USE_ENV'].lower() == 'yes':
    ENV = config['api']['ENV_NAME']
    api_key = (os.environ[ENV])

if config['api']['USE_ENV'].lower() == 'no':
    PATH = config['api']['API_KEY_PATH']
    api_key = open(PATH, 'r').read()

# api_key = open('key.txt', 'r').read()
bot.run(api_key)
