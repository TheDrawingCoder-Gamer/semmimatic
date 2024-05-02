from nio import AsyncClient, MatrixRoom, RoomMessageText
import niobot
import os
import semmimatic
import asyncio
import markdown

token = os.environ["TOKEN"]
home_server = os.environ["HOME_SERVER"]
user_id = os.environ["USER_ID"]
bot_owner = os.environ["BOT_OWNER"]
device_id = os.environ["DEVICE_ID"]

semmi = semmimatic.Semmimatic("semmi.txt")
bot = niobot.NioBot(
    homeserver=home_server,
    user_id=user_id,
    device_id="nio-bot",
    command_prefix="s$",
    owner_id=bot_owner
)


@bot.command(name="semmimatic")
async def semmimatic(ctx):
    res = semmi.model.make_sentence(tries=100)
    await ctx.respond(res)
@bot.command()
async def reload(ctx):
    if not ctx.client.is_owner(ctx.message.sender):
        return
    async with niobot.Typing(ctx.client, ctx.room.room_id):
        semmi.build_model()
    await ctx.respond("Reloaded")

bot.run(access_token=token)