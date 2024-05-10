# simple file that just loads a single user and runs it

import discord
from discord.ext import commands
from discord import app_commands
import markovify
import os
import time
import semmimatic
import discord_cog

source_data = "semmi.txt"
if "SOURCE_DATA" in os.environ:
    source_data = os.environ["SOURCE_DATA"]



cmd_prefix = "s$"
if "CMD_PREFIX" in os.environ:
    cmd_prefix = os.environ["CMD_PREFIX"]

interest_name = "semmi"
if "INTEREST_NAME" in os.environ:
    interest_name = os.environ["INTEREST_NAME"]

interest_id = None
if "INTEREST_ID" in os.environ:
    interest_id = int(os.environ["INTEREST_ID"])

do_newline = True
if "DO_NEWLINE" in os.environ:
    do_newline = os.environ["DO_NEWLINE"] == 'True'


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(cmd_prefix, intents=intents)
tree = bot.tree

semmi = semmimatic.Semmimatic(source_data, do_newline)

@bot.command()
@commands.is_owner()
async def sync(ctx):
    synced = await ctx.bot.tree.sync()
    await ctx.send(f"Synced {len(synced)} commands globally")
@bot.event
async def on_ready():
    await bot.add_cog(discord_cog.QuoteGenerator(bot,semmi,name=interest_name,interest=interest_id))
    await tree.sync()

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    await bot.invoke(ctx)

token = os.environ['TOKEN']

bot.run(token)
