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
        elif msg[1] == 'recent':
            if len(msg) == 3:
                steamid = get_steam_id(msg[2])
                recents = requests.get('http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=B6137C92F67299965B5E6BF287ECA4AE&steamid=' + steamid + '&format=json')
                recents = recents.json()
                print(recents)
                em = discord.Embed(title='Here\'s your recent played game list, ' + message.author.name + '!', description='And again, Thanks for Using!\nYou played ' + str(recents['response']['total_count']) + ' games in last 2 weeks.')
                for text in recents['response']['games']:
                    em.add_field(name=text['name'] + ' (' + str(text['appid']) + ')', value='Played for ' + str("%.2f" % (text['playtime_2weeks'] / 60)) + ' hours in last 2 weeks\nPlayed for ' + str("%.2f" % (text['playtime_forever'] / 60)) + ' hours in your lifetime', inline=False)

                await app.send_message(message.channel, embed=em)
            else:
                await app.send_message(message.channel, "Enter Your ID")


def get_steam_id(name):
    if isNumber(name) and len(name) > 17:
        return name
    jsons = requests.get('https://api.steamid.uk/request.php?api=9295K4J61YKD3357E6WA&player=' + name +'&request_type=5&format=json')
    jsons = jsons.json()

    return jsons['linked_users']['steamid64']


def isNumber(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

app.run(token)
