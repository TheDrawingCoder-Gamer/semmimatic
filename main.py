import discord
from discord.ext import commands
from discord import app_commands
import markovify
import os
import time
import semmimatic

semmi_id = 415825875146375168
semmi = semmimatic.Semmimatic("semmi.txt")
# hack for bad code
semmi.user_id = semmi_id

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
    res = semmi.model.make_sentence(tries=100)
    await ctx.send(res)

@bot.hybrid_command(description="Reloads bot model")
@commands.is_owner()
async def reload(ctx):
    await ctx.defer(ephemeral=True)
    start = time.perf_counter() 
    semmi.build_model()
    end = time.perf_counter()
    elapsed = end - start
    await ctx.send(content=f"Done reloading (elapsed {elapsed})", ephemeral=True)


@bot.hybrid_command(description="Fetches current semmi data")
async def fetch(ctx):
    if ctx.interaction:
        await ctx.send(file=discord.File(semmi.quote_path), ephemeral=True)
    else:
        await ctx.author.send(file=discord.File(semmi.quote_path))


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author.id == semmi.user_id:
        semmi.add_message(message.content)




token = os.environ['TOKEN']

bot.run(token)
