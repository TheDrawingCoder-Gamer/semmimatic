import asyncio

import niobot
import semmimatic
import typing
import matrix_store
import re
import logging

ping_regex=re.compile('<@(.+)>')
async def generate(self, ctx):
    async with self.lock:
        async with niobot.utils.Typing(ctx.client, ctx.room.room_id):
            res = self.model.make_sentence(tries=100)
            number = ping_regex.search(res)

            if number != None:
                for group in number.groups():
                    my_user_id = f"@_discord_{group}:t2bot.io"
                    username = str(group)
                    try:
                        user = await ctx.client.get_profile(my_user_id)
                        if user.displayname != None:
                            username = user.displayname
                    except KeyError:
                        pass
                    res = res.replace(f"<@{group}>", f"PING {username}")
        await ctx.respond(res)
async def reload(self, ctx):
    if not ctx.client.is_owner(ctx.message.sender):
        return
    async with niobot.Typing(ctx.client, ctx.room.room_id):
        ctx.model.build_model()
    await ctx.respond("Reloaded")

class DynamicModule(niobot.Module):
    def __init__(self, bot, name: typing.Optional[str] = None):
        super().__init__(bot)
        self.__cog_name__ = name if name is not None else type(self).__name__
class GeneratorModule(DynamicModule):
    def __init__(self, bot, model: semmimatic.Semmimatic, name: str = "semmi"):
        super().__init__(bot, name=f"{name}cog")
        logging.getLogger(__name__).setLevel(10)
        self.model = model
        self.lock = asyncio.Lock()
        # god is dead
        @niobot.command(f"{name}matic")
        async def stinky_generate(self, ctx):
            await generate(self, ctx)
        @niobot.command(f"reload_{name}")
        async def stinky_reload(self, ctx):
            await reload(self, ctx)
        self.generate = stinky_generate
        self.reload = stinky_reload

def mount_dynmodule(bot, module: DynamicModule):
    if not hasattr(bot, "_dynmodules"):
        bot._dynmodules = dict()
    if module.__cog_name__ in bot._dynmodules:
        raise ValueError("%r is already loaded." % module.__cog_name__)
    module.__setup__()
    bot._dynmodules[module.__cog_name__] = module

def unmount_dynmodule(bot, name: str):
    bot._dynmodules[name].__teardown__()

