from nio import AsyncClient, MatrixRoom, InviteMemberEvent
import nio
import niobot
import os
import semmimatic
import asyncio
import markdown
import re
import matrix_store
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
bot = niobot.NioBot(
    homeserver=home_server,
    user_id=user_id,
    device_id=device_id,
    command_prefix=prefix,
    owner_id=bot_owner,
    store_path='./store'
)

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
async def semmimatic(ctx):
    async with niobot.utils.Typing(ctx.client, ctx.room.room_id):
        res = semmi.model.make_sentence(tries=100)
        can_ping = False
        if bot.store:
            if bot.store.database:
                with matrix_store.RoomExtras.bind_ctx(bot.store.database):
                    model = matrix_store.RoomExtras.get_or_none(matrix_store.RoomExtras.room_id == ctx.room.room_id)
                    if model:
                        can_ping = model.ping  
        number = ping_regex.search(res)

        if number != None:
            for group in number.groups():
                my_user_id = f"@_discord_{group}:t2bot.io"
                username = str(group)
                try:
                    user = await ctx.client.get_profile(my_user_id)
                    if user.displayname != None:
                        username = user.displayname
                # to document my sanity loss
                except KeyError:
                    pass
                if can_ping:
                    res = res.replace(f"<@{group}>", f"[{username}](https://matrix.to/#/{my_user_id})")
                else:
                    res = res.replace(f"<@{group}>", f"PING {username}")
    await ctx.respond(res)
@bot.command()
async def reload(ctx):
    if not ctx.client.is_owner(ctx.message.sender):
        return
    async with niobot.Typing(ctx.client, ctx.room.room_id):
        semmi.build_model()
    await ctx.respond("Reloaded")
@bot.command()
async def leave(ctx):
    if not ctx.client.is_owner(ctx.message.sender):
        return
    await ctx.client.room_leave(ctx.room.room_id)

@bot.command(description="Change if this will attempt to ping directly in this room")
@sender_has_power(50)
async def set_ping(ctx: niobot.Context, ping: bool):
    if bot.store:
        if bot.store.database:
            with bot.store.database.bind_ctx([matrix_store.RoomExtras]):
                matrix_store.RoomExtras.insert(
                        room_id = ctx.room.room_id,
                        ping = ping
                        ).on_conflict_replace().execute()
    await ctx.respond("Done")



@bot.on_event("ready")
async def ready(result):
    if bot.store:
        if bot.store.database:
            with bot.store.database.bind_ctx([matrix_store.RoomExtras]):
                bot.store.database.create_tables([matrix_store.RoomExtras])


bot.run(access_token=token)
