import discord
from discord.ext import commands
from discord import app_commands
import markovify
import os

with open("semmi.txt") as text_file:
    model = markovify.NewlineText(text_file.read())



semmi_id = 415825875146375168

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot("s$", intents=intents)
tree = bot.tree

@bot.command()
@commands.is_owner()
async def sync(ctx):
    synced = await ctx.bot.tree.sync()
    await ctx.send(f"Synced {len(synced)} commands globally")
@bot.event
async def on_ready():
    await tree.sync()

@bot.hybrid_command(description="Generates semmi text.")
async def semmimatic(ctx):
    res = model.make_sentence(tries=100)
    await ctx.send(res)

@bot.hybrid_command(description="Reloads bot model")
@commands.is_owner()
async def reload(ctx):
    with open("semmi.txt") as text_file:
        model = markovify.NewlineText(text_file.read())
    await ctx.send("Reloaded model")

@bot.hybrid_command(description="Fetches current semmi data")
@commands.check_any(commands.dm_only(), commands.is_owner())
async def fetch(ctx):
    await ctx.send(file=discord.File("semmi.txt"))


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author.id == semmi_id:
        with open("semmi.txt", "a") as text_file:
            text_file.write(message.content)
            text_file.write("\r\r\r\n")




token = os.environ['TOKEN']

bot.run(token)
