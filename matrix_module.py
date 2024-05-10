import asyncio

import niobot
import semmimatic
import typing
import matrix_store
import re
import logging

ping_regex=re.compile('<@(.+)>')

def replace_ping(self):
    async def inner(user_id):
        uid = f"@_discord_{str(user_id)}:t2bot.io"
        username = str(user_id)
        user = await self.get_profile(uid)
        if hasattr(user, "displayname"):
            if user.displayname != None:
                username = user.displayname
        return f"PING {username}"
    return inner
async def generate(self, ctx):
    async with niobot.utils.Typing(ctx.client, ctx.room.room_id):
        res = await self.model.make_sentence_full(replace_ping(ctx.client))
        
        
    await ctx.respond(res)

async def reload(self, ctx):
    if not ctx.client.is_owner(ctx.message.sender):
        return
    async with niobot.Typing(ctx.client, ctx.room.room_id):
        self.model.build_model()
    await ctx.respond("Reloaded")

class DynamicModule(niobot.Module):
    def __init__(self, bot, name: typing.Optional[str] = None):
        super().__init__(bot)
        self.__cog_name__ = name if name is not None else type(self).__name__
class GeneratorModule(DynamicModule):
    def __init__(self, bot, model: semmimatic.Semmimatic, name: str = "semmi"):
        super().__init__(bot, name=f"{name}cog")
        self.model = model
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

