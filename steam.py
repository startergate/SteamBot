import asyncio
import discord

app = discord.Client()

token = 'NTU1MzM5MjM2MDM1OTE5ODgy.D2p1kA.hM6p3MhaLbuJnS7H0hUeRrfG2ys'


@app.event
async def on_ready():
    print("로그인 정보>")
    print(app.user.name)
    print(app.user.id)
    print("=============")

    await app.change_presence(game=discord.Game(name="Steam", type=1))


@app.event
async def on_message(message):
    if message.author.bot:
        return None

    if message.content == "st!help":
        await app.send_message(message.channel, "Here")

app.run(token)
