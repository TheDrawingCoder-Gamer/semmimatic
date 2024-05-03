from nio import AsyncClient, MatrixRoom, InviteMemberEvent
import nio
import niobot
import os
import semmimatic
import asyncio
import markdown
import re

token = os.environ["TOKEN"]
home_server = os.environ["HOME_SERVER"]
user_id = os.environ["USER_ID"]
bot_owner = os.environ["BOT_OWNER"]
device_id = os.environ["DEVICE_ID"]

semmi = semmimatic.Semmimatic("semmi.txt")
bot = niobot.NioBot(
    homeserver=home_server,
    user_id=user_id,
    device_id=device_id,
    command_prefix="s$",
    owner_id=bot_owner,
    store_path='./store'
)

ping_regex=re.compile('<@(.+)>')

@bot.command()
async def semmimatic(ctx):
    res = semmi.model.make_sentence(tries=100)
    number = ping_regex.search(res)

    if number:
        for group in number.groups():
            my_user_id = f"@_discord_{group}:t2bot.io"
            username = "this_guy"
            try:
                user = await ctx.client.get_profile(my_user_id)
                if user.displayname != None:
                    username = user.displayname
            except:
                pass
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
bot.run(access_token=token)
