import discord
from discord.ext import commands
from discord import app_commands
import markovify
import os

with open("semmi.txt") as text_file:
    model = markovify.NewlineText(text_file.read())





intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot("$", intents=intents)
tree = bot.tree

@bot.command()
@commands.is_owner()
async def sync(ctx):
    synced = await ctx.bot.tree.sync()
    await ctx.send(f"Synced {len(synced)} commands globally")
@bot.event
async def on_ready():
    await tree.sync()

@tree.command()
async def semmimatic(ctx):
    res = model.make_sentence(tries=100)
    await ctx.response.send_message(res)



token = os.environ['TOKEN']

bot.run(token)
