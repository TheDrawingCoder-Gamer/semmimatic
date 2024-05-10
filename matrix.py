from nio import AsyncClient, MatrixRoom, InviteMemberEvent
import nio
import niobot
import os
import semmimatic
import asyncio
import markdown
import re
import matrix_store
import matrix_module
import logging
from typing import Optional

token = os.environ["TOKEN"]
home_server = os.environ["HOME_SERVER"]
user_id = os.environ["USER_ID"]
bot_owner = os.environ["BOT_OWNER"]
device_id = os.environ["DEVICE_ID"]
prefix = "s$"
if "SEMMIMATIC_PREFIX" in os.environ:
    prefix = os.environ["SEMMIMATIC_PREFIX"]

semmi = semmimatic.Semmimatic("semmi.txt")
bulby_model = semmimatic.Semmimatic("bulby.txt")
bot = niobot.NioBot(
    homeserver=home_server,
    user_id=user_id,
    device_id=device_id,
    command_prefix=prefix,
    owner_id=bot_owner,
    store_path='./store'
)

SEMMI_MODULE = matrix_module.GeneratorModule(bot, semmi, name="semmi")
BULBY_MODULE = matrix_module.GeneratorModule(bot, bulby_model, name="bulby")

ping_regex=re.compile('<@(.+)>')

def sender_has_power(power: int, name: Optional[str] = None):

    async def predicate(ctx):
        power_levels = await ctx.client.room_get_state_event(ctx.room.room_id, "m.room.power_levels")

        try:
            user_power_level = power_levels.content["users"][ctx.message.sender]
        except KeyError:
            user_power_level = power_levels.content["users_default"]
        
        if user_power_level >= power:
            return True
        raise niobot.InsufficientPower(name, needed=power, have=user_power_level)

    return niobot.check(predicate, name)
@bot.command()
async def leave(ctx):
    if not ctx.client.is_owner(ctx.message.sender):
        return
    await ctx.client.room_leave(ctx.room.room_id)




@bot.on_event("ready")
async def ready(result):
    pass


matrix_module.mount_dynmodule(bot, SEMMI_MODULE)
matrix_module.mount_dynmodule(bot, BULBY_MODULE)
bot.run(access_token=token)
