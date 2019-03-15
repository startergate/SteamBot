import asyncio
import discord
import requests

app = discord.Client()

token = 'NTU1MzM5MjM2MDM1OTE5ODgy.D2p1kA.hM6p3MhaLbuJnS7H0hUeRrfG2ys'


@app.event
async def on_ready():
    print("로그인 정보>")
    print(app.user.name)
    print(app.user.id)
    print("=============")

    await app.change_presence(game=discord.Game(name="st!help to get help", type=1))


@app.event
async def on_message(message):
    if message.author.bot:
        return None
    msg = message.content.split(' ')
    print(msg)
    if msg[0] == "st!help":
        em = discord.Embed(title='SteamBot', description='Thank you for using SteamBot')
        em.add_field(name='st!help', value='Help! Call help when you don\'t know what to do.', inline=False)
        em.add_field(name='st!game', value='Steam Game Functions', inline=False)
        em.add_field(name='st!game recent (Player)', value='Get player\'s recent played game.', inline=False)
        await app.send_message(message.channel, embed=em)
        if len(msg) > 1:
            await app.send_message(message.channel, "help 명령어는 st!help만 쓰셔도 작동합니다.")
    elif msg[0] == "st!game":
        if len(msg) == 1:
            await app.send_message(message.channel, "Use more specified message.")
        if msg[1] == 'recent':
            await app.send_message(message.channel, "st!game recent.")

app.run(token)
