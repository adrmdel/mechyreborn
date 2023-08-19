import asyncio
import random
import re
import sys
import time
from typing import Optional, Literal

import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Greedy, Context

from functions.dice import roll, main_regex, cod_regex, exalted_regex
from functions.eightball import eightball
from functions.reminder import reminder, check_and_clear_reminders
from functions.quote import quote
from database import connect

client = commands.Bot(command_prefix='.', intents=discord.Intents.all())
token = sys.argv[1]
database_uri = sys.argv[2]

database = connect(database_uri)['public']
reminders_table = database['reminders']
quotes_table = database['quotes']


@client.hybrid_command(name='echo')
async def cmd_echo(ctx):
    await ctx.send(format_response(ctx.author, 'Echo!'))


@client.hybrid_command(name='repeat')
async def cmd_repeat(ctx, *, message_to_repeat: str):
    await ctx.send(format_response(ctx.author, message_to_repeat))


@client.hybrid_command(name='8ball')
async def cmd_eightball(ctx, *, query: Optional[str]):
    response = eightball(query)
    await ctx.send(format_response(ctx.author, response))


@client.hybrid_command(name='choose')
async def cmd_choose(ctx, *, query):
    response = random.choice(query.split(','))
    await ctx.send(format_response(ctx.author, response))


@client.hybrid_command(name='roll')
async def cmd_roll(ctx, *, query: Optional[str]):
    response = roll(query)
    await ctx.send(format_response(ctx.author, response))


@client.hybrid_command(name='remind')
async def cmd_reminder(ctx, *, query: str):
    response = reminder(ctx, query, reminders_table)
    await ctx.send(format_response(ctx.author, response))


@client.hybrid_command(name='checkreminders')
async def cmd_check_reminder(_ctx: Optional[Context]):
    result = check_and_clear_reminders(reminders_table)
    for x in result:
        await client.get_channel(x['chan_id']).send('{}: {}'.format(x['author'], x['message']))


@client.hybrid_command("quote")
async def cmd_quote(ctx, *, query: Optional[str]):
    response = quote(ctx, query, quotes_table)
    await ctx.send(format_response(ctx.author, response))


# Umbra's Sync
@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


@client.event
async def on_message(msg: Message):
    if msg.author != client.user:
        if (type(msg.clean_content) is str and len(msg.clean_content) > 0 and msg.clean_content[0].isnumeric()) and \
                (len(re.findall(main_regex, msg.clean_content)) > 0 or
                 len(re.findall(cod_regex, msg.clean_content)) > 0 or
                 len(re.findall(exalted_regex, msg.clean_content)) > 0):
            await msg.channel.send(format_response(msg.author, roll(msg.clean_content)))
    await client.process_commands(msg)


@client.event
async def on_ready():
    client.loop.create_task(reminder_schedule(60))


async def reminder_schedule(delay):
    next_time = time.time() + delay
    while True:
        await asyncio.sleep(max(0, next_time - time.time()))
        await cmd_check_reminder(None)
        next_time += (time.time() - next_time) // delay * delay + delay


def format_response(author, response):
    return author.mention + ': ' + response


client.run(token)
