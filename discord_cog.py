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
    @commands.hybrid_command(name="gen")
    async def generate(self, ctx: commands.Context):
        res = self.model.model.make_sentence(tries=100)
        await ctx.send(res)
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
        interaction.response.defer(ephemeral=True)
        interaction.response.send_message(ephemeral=True, file=self.model.quote_path)
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.interest is None:
            return
        if message.author.id == self.interest:
            self.model.add_message(message.content)

