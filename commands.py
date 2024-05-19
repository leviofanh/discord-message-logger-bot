import discord
from discord.ext import commands
import os
from funcs import add_channel_to_table, delete_channel_from_table, get_channels_from_table, save_new_messages, get_last_message_published


def add_channel_to_tracking(bot:commands.Bot, session, command):

    @bot.command(aliases=(command, ))
    @commands.has_permissions(administrator=True)
    async def add_channel(ctx, channel: discord.TextChannel):
        channel_id = channel.id
        result = add_channel_to_table(session, channel_id)
        if result is None:
            os.makedirs(f'data/{channel_id}', exist_ok=True)
            await ctx.send(f'Channel {channel.name} has been added.')

            channels = get_channels_from_table(session)

            if channels:
                for channel_id in channels:
                    last_message_published = get_last_message_published(session, channel_id)
                    channel = bot.get_channel(channel_id)

                    await bot.loop.create_task(save_new_messages(session, channel, last_message_published))
        else:
            await ctx.send(result)


def delete_channel_from_tracking(bot:commands.Bot, session, command):

    @bot.command(aliases=(command, ))
    @commands.has_permissions(administrator=True)
    async def delete_channel(ctx, channel: discord.TextChannel):
        channel_id = channel.id
        result = delete_channel_from_table(session, channel_id)
        if result is None:
            await ctx.send(f'Channel {channel.name} has been deleted.')
        else:
            await ctx.send(result)


def show_all_channels_list(bot:commands.Bot, session):

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def test(ctx):
        result = get_channels_from_table(session)
        await ctx.send(result)


def change_message_update_limit(bot:commands.Bot, command, config):
    from main import load_config

    @bot.command(aliases=(command,))
    @commands.has_permissions(administrator=True)
    async def config_set_message_update_limit(ctx, number: str):
        if not number.isdigit():
            await ctx.send(f'Error: {number} is not a valid number.')
            return

        config['bot']['MESSAGE_LIMIT'] = number
        config.write()
        await ctx.send(f'Value has been set to {number}')
        load_config()


def change_bot_status(bot:commands.Bot, command, config):
    @bot.command(aliases=(command,))
    @commands.has_permissions(administrator=True)
    async def config_set_bot_status(ctx, *, status: str):

        config['bot']['STATUS'] = status
        config.write()
        await ctx.send(f'Status is set to \"{status}\"')
        await bot.change_presence(activity=discord.Game(name=status))
