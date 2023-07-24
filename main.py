import random
import sys
from typing import Optional, Literal

import discord
from discord.ext import commands
from discord.ext.commands import Greedy, Context

from functions.dice import roll
from functions.eightball import eightball

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())
token = sys.argv[1]


@client.hybrid_command(name='echo')
async def cmd_echo(ctx):
    await ctx.send('Echo!')


@client.hybrid_command(name='repeat')
async def cmd_repeat(ctx, *, message_to_repeat: str):
    await ctx.send(message_to_repeat)


@client.hybrid_command(name='8ball')
async def cmd_eightball(ctx, *, query: Optional[str]):
    await ctx.send(eightball(query))


@client.hybrid_command(name='roll')
async def cmd_roll(ctx, *, query: Optional[str]):
    await ctx.send(roll(query))


# Umbra's Sync
@client.command()
@commands.guild_only()
async def sync(
        ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
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
async def on_message(msg):
    # if msg.author != client.user:
    #     await msg.channel.send('haha')
    await client.process_commands(msg)


client.run(token)
