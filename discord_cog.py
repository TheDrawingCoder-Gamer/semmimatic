import discord
from discord.ext import commands
from discord import app_commands
import semmimatic
import time

def set_name(cmd, name):
    if isinstance(cmd, commands.HybridCommand):
        if cmd.app_command is not None:
            cmd.app_command.name = name
    cmd.name = name
def replace(cmd, name):
    if cmd.name == "gen":
        set_name(cmd, f"{name}matic")
        return
    if cmd.name == "reload":
        set_name(cmd, f"reload_{name}")
        return
    if cmd.name == "fetch":
        set_name(cmd, f"fetch_{name}")
        return
def replace_ping(bot):
    async def inner(user_id):
        res = await bot.fetch_user(user_id)
        if res is None:
            out = str(user_id)
        else:
            out = res.global_name if res.global_name is not None else str(res)
        return f"PING {out}"
    return inner

class QuoteGenerator(commands.Cog):
    def __init__(self, bot, model: semmimatic.Semmimatic, name="semmi", interest=None):
        self.bot = bot
        self.model = model
        self.interest = interest
        self.__cog_name__ = f"{name}cog"
        for cmd in self.get_commands():
#            if not isinstance(cmd, commands.Command):
#                continue
            replace(cmd, name)
        for cmd in self.get_app_commands():
#            if not isinstance(cmd, app_commands.Command):
#                continue
            replace(cmd, name)
    @app_commands.command(name="gen")
    @app_commands.user_install()
    async def generate(self, interaction):
        await interaction.response.defer()
        res = await self.model.make_sentence_full(replace_ping(self.bot))
        await interaction.response.send_message(content=res)
    @commands.hybrid_command()
    @commands.is_owner()
    async def reload(self, ctx):
        await ctx.defer(ephemeral=True)
        start = time.perf_counter()
        self.model.build_model()
        end = time.perf_counter()
        elapsed = end - start
        await ctx.send(content=f"Done reloading (elapsed {elapsed})", ephemeral=True)
    @app_commands.command()
    async def fetch(self, interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.response.edit_original_response(attachments=[discord.File(self.model.quote_path)])
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.interest is None:
            return
        if message.author.id == self.interest:
            self.model.add_message(message.content)


