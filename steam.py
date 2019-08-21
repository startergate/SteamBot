# -*- coding: utf-8 -*-
# https://discordapp.com/oauth2/authorize?client_id=555339236035919882&scope=bot&permissions=67584
import asyncio
import discord
import random
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from modules.help import Help
from modules.liveupdate import *
from modules.steamapi import *
import modules.setting

app = discord.Client()
help = Help()

token = modules.setting.token

loop = asyncio.get_event_loop()


@app.event
async def on_ready():
    print("로그인 정보>")
    print(app.user.name)
    print(app.user.id)
    print("=============")

    await app.change_presence(game=discord.Game(name="도움말을 받으려면 st!help ", type=1))

    loop.create_task(realtime())


@app.event
async def on_message(message):
    if message.author.bot:
        return None
    msg = message.content.split(' ')
    if msg[0] == "st!help":
        if len(msg) == 1:
            await app.send_message(message.channel, embed=help.getHelp())
        else:
            await app.send_message(message.channel, embed=help.getSpecificHelp(msg[1]))
    if msg[0] == 'st!add':
        await app.send_message(message.channel, "아래 링크로 들어가서 SteamBot을 서버에 추가할 수 있어요!\n`https://discordapp.com/oauth2/authorize?client_id=555339236035919882&permissions=0&scope=bot`")
    elif msg[0] == "st!game":
        if len(msg) == 1:
            await app.send_message(message.channel, ":x: 명령어를 제대로 입력해주세요!.")
            await app.send_message(message.channel, embed=help.getSpecificHelp("game"))
        elif msg[1] == 'search':
            if len(msg) < 3:
                await app.send_message(message.channel, ":x: 검색어를 입력해주세요!.")
                return

            query = message.content.replace('st!game search ', '')
            src = requests.get('https://store.steampowered.com/search/?term={}'.format(query.lower().replace(' ', '+'))).text
            src = BeautifulSoup(src, 'html.parser')
            games = src.find_all('a', class_='search_result_row')
            if not games:
                await app.send_message(message.channel, ":x: 게임을 전혀 찾을 수 없었어요.")
                return
            output_text = ''
            for game in games:
                price = game.find('div', class_='search_price').getText().strip();
                temp = price.split('₩')
                if len(temp) >= 3:
                    price = '₩ {} ~~₩ {}~~ ({})'.format(temp[2], temp[1], game.find('div', class_='search_discount').find('span').text)
                if not price:
                    price = '기록 없음'
                output_text += '\n' + game.find('span', class_='title').getText() + '  |  ' + price
            em = discord.Embed(title='"{}"을 검색한 결과, {}개의 게임을 찾았어요!'.format(query, len(games)), description=output_text, colour=discord.Colour(0x1b2838))
            await app.send_message(message.channel, embed=em)
        elif msg[1] == 'bestseller':
            if len(msg) == 2:
                bestseller_src = requests.get('https://store.steampowered.com/search/?filter=topsellers')
                bestseller_src = BeautifulSoup(bestseller_src.text, 'html.parser')
                bst_seller = bestseller_src.find_all('a', class_='search_result_row')

                output_text = '스팀의 최고 판매 제품 목록이에요.'
                for product in bst_seller:
                    price = product.find('div', class_='search_price').getText().strip();
                    temp = price.split('₩')
                    if len(temp) >= 3:
                        price = '₩ ' + temp[2] + ' ~~₩ ' + temp[1] + '~~'
                    output_text += '\n' + product.find('span', class_='title').getText() + ' | ' + price

                em = discord.Embed(title='스팀 최고 판매 제품', description=output_text, colour=discord.Colour(0x1b2838))
                await app.send_message(message.channel, embed=em)
            elif msg[2] == 'new':
                bestseller_src = requests.get('https://store.steampowered.com/explore/new/')
                bestseller_src = BeautifulSoup(bestseller_src.text, 'html.parser')
                bst_seller = bestseller_src.find('div', id='tab_newreleases_content')
                bst_seller = bst_seller.find_all('a', class_='tab_item')
                output_text = '스팀의 신제품 최고 판매 제품 목록이에요.'
                previous_title = ''
                for product in bst_seller:
                    if previous_title == product.find('div', class_='tab_item_name').getText():
                        continue
                    previous_title = product.find('div', class_='tab_item_name').getText()
                    if(product.find('div', class_='discount_final_price')):
                        price = product.find('div', class_='discount_final_price').getText().strip()
                    else:
                        price = '기록 없음'
                    if product.find('div', class_='discount_original_price'):
                        price += ' ~~' + product.find('div', class_='discount_original_price').getText().strip() + '~~'
                    output_text += '\n' + product.find('div', class_='tab_item_name').getText() + ' | ' + price

                em = discord.Embed(title='스팀 최고 판매 제품', description=output_text, colour=discord.Colour(0x1b2838))
                await app.send_message(message.channel, embed=em)
            elif msg[2] == 'oncoming':
                bestseller_src = requests.get('https://store.steampowered.com/explore/upcoming/')
                bestseller_src = BeautifulSoup(bestseller_src.text, 'html.parser')
                bst_seller = bestseller_src.find('div', id='tab_popular_comingsoon_content')
                bst_seller = bst_seller.find_all('a', class_='tab_item')

                output_text = '스팀의 인기순 출시 예정 목록이에요.'
                previous_title = ''
                for product in bst_seller:
                    if previous_title == product.find('div', class_='tab_item_name').getText():
                        continue
                    previous_title = product.find('div', class_='tab_item_name').getText()
                    price = ''
                    if product.find('div', class_='discount_final_price'):
                        price = ' | '
                        price += product.find('div', class_='discount_final_price').getText().strip()
                        if product.find('div', class_='discount_original_price'):
                            price += ' ~~' + product.find('div', class_='discount_original_price').getText().strip() + '~~'
                    output_text += '\n' + product.find('div', class_='tab_item_name').getText() + price

                em = discord.Embed(title='스팀 최고 인기 출시 예정 제품', description=output_text, colour=discord.Colour(0x1b2838))
                await app.send_message(message.channel, embed=em)
        elif msg[1] == 'new':
            new_src = requests.get('https://store.steampowered.com/search/?sort_by=Released_DESC')
            new_src = BeautifulSoup(new_src.text, 'html.parser')
            new_prd = new_src.find_all('a', class_='search_result_row')

            output_text = '스팀의 최신 출시 제품 목록이에요.'
            for product in new_prd:
                if product.find('div', class_='search_price').getText().strip() != '':
                    price = product.find('div', class_='search_price').getText().strip();
                    temp = price.split('₩')
                    if len(temp) >= 3:
                        price = '₩ {} ~~₩ {}~~'.format(temp[2], temp[1])
                else:
                    price = "기록 없음"
                output_text += '\n{}  |  {}'.format(product.find('span', class_='title').getText(), price)

            em = discord.Embed(title='스팀 최신 출시 제품', description=output_text, colour=discord.Colour(0x1b2838))
            await app.send_message(message.channel, embed=em)
        elif msg[1] == 'specials':
            new_src = requests.get('https://store.steampowered.com/search/?specials=1')
            new_src = BeautifulSoup(new_src.text, 'html.parser')
            new_prd = new_src.find_all('a', class_='search_result_row')

            output_text = '스팀의 인기 할인 제품 목록이에요.'
            for product in new_prd:
                if product.find('div', class_='search_price').getText().strip() != '':
                    price = product.find('div', class_='search_price').getText().strip();
                    temp = price.split('₩')
                    if len(temp) >= 3:
                        price = '₩ ' + temp[2] + ' ~~₩ ' + temp[1] + '~~'
                else:
                    price = "기록 없음"
                output_text += '\n' + product.find('span', class_='title').getText() + '  |  ' + price

            em = discord.Embed(title='스팀 인기 할인 제품', description=output_text, colour=discord.Colour(0x1b2838))
            await app.send_message(message.channel, embed=em)
        elif msg[1] == 'hot':
            if len(msg) > 2:
                try:
                    requested_length = int(msg[3])
                except ValueError:
                    await app.send_message(message.channel, ":x: 게임 갯수는 정수를 사용해주세요.")
                    return
            else:
                requested_length = 10

            hot_src = requests.get('https://store.steampowered.com/stats/?l=koreana')
            hot_src = BeautifulSoup(hot_src.text, 'html.parser')
            hot_prd = hot_src.find_all('tr', class_='player_count_row')
            if len(hot_prd) < requested_length:
                requested_length = len(hot_prd)
            if requested_length > 25:
                requested_length = 25
            em = discord.Embed(title='스팀 최다 플레이어', description='스팀의 현재 최다 플레이어 수 목록이에요.', colour=discord.Colour(0x1b2838))
            i = 0
            for product in hot_prd:
                if i == requested_length:
                    break
                name = '{} ({})'.format(product.find('a', class_='gameLink').getText(), product.find('a', class_='gameLink')['href'].replace('https://store.steampowered.com/app/', '').split('/')[0])
                value = "현재 플레이어: {}명 | 오늘 최고 기록: {}명".format(product.find_all('span', class_='currentServers')[0].getText(), product.find_all('span', class_='currentServers')[1].getText())
                em.add_field(name=name, value=value, inline=False)

                i += 1

            await app.send_message(message.channel, embed=em)
        elif msg[1] == 'news':
            if len(msg) > 2:
                requested_length = 10
                halflife3 = ['halflife 3', 'hl3', 'halflife3', 'hl 3']
                if (message.content.replace('st!game news ', '').lower() in halflife3):
                    await app.send_message(message.channel, ':x: 이미 뒤진 게임이에요.')
                    return
                id = get_game_id(message.content.replace('st!game news ', ''))
                if id == {}:
                    await app.send_message(message.channel, ':x: 게임을 찾을 수 없어요.')
                    return
                await app.send_message(message.channel, ":white_check_mark: 로딩 중 입니다.")
                keys = list(id.keys())
                news_src = requests.get('http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={}&count={}&maxlength=300&format=json'.format(keys[0], requested_length))
                news_src = news_src.json()

                news_text = news_src['appnews']['newsitems']
                if requested_length > len(news_text):
                    requested_length = len(news_text)
                em = discord.Embed(title=id[keys[0]], description="{}개의 뉴스를 가져왔어요.".format(requested_length))
                i = 0
                for news in news_text:
                    if i > requested_length:
                        break
                    em.add_field(name='{} - {}'.format(news['feedlabel'], news['title']), value=md(news['contents']) + ' **[자세히 보기]({})**'.format(news['url']))
                    i += 1
                await app.send_message(message.channel, embed=em)
            else:
                await app.send_message(message.channel, ':x: 게임 이름을 입력해주세요.')
        elif msg[1] == 'realtime':
            if len(msg) > 2:
                if msg[2] == 'stop':
                    if message.channel not in realtimeList:
                        await app.send_message(message.channel, ':x: 등록되지 않은 채널이에요!')
                        return
                    realtimeList.remove(message.channel)
                    await app.send_message(message.channel, ':white_check_mark: 스팀 실시간 업데이트 수신을 중지했어요!')
                    return
            if message.channel in realtimeList:
                await app.send_message(message.channel, ':x: 이미 등록된 채널이에요!')
                return
            realtimeList.append(message.channel)
            await app.send_message(message.channel, ':white_check_mark: 지금부터 이 채널에서 스팀 실시간 업데이트를 받을 수 있어요!')
    elif msg[0] == "st!user":
        if len(msg) == 1:
            await app.send_message(message.channel, ":x: 명령어를 제대로 입력해주세요!.")
            await app.send_message(message.channel, embed=help.getSpecificHelp("user"))
        elif msg[1] == 'recent':
            if len(msg) == 2:
                await app.send_message(message.channel, ":x: 스팀 아이디를 입력해주세요!.")
            elif len(msg) == 3:
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await app.send_message(message.channel, ":x: 유효한 스팀 아이디를 사용해주세요.")
                    return
                recents = requests.get(
                    'http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=B6137C92F67299965B5E6BF287ECA4AE&steamid={}&format=json'.format(steamid))
                recents = recents.json()
                if recents['response']['total_count'] == 0:
                    await app.send_message(message.channel,
                                           ':frowning: 어떠한 게임도 불러오지 못했어요. 아무런 게임도 플레이하지 않으셨을수도 있고, 스팀 프로필이 비공개일수도 있어요.')
                    return
                em = discord.Embed(title='{} 님이 최근에 플레이하신 게임 목록이에요.'.format(msg[2]),
                                   description='지난 2주간 {}개의 게임을 플레이하셨어요.'.format(recents['response']['total_count']),
                                   colour=discord.Colour(0x1b2838))
                total_time = 0;
                for text in recents['response']['games']:
                    total_time += text['playtime_2weeks']
                    em.add_field(name='{} ({})'.format(text['name'], text['appid']),
                                 value='지난 2주간 {} 시간동안 플레이 함\n평생 동안 {} 시간동안 플레이 함'.format("%.2f" % (text['playtime_2weeks'] / 60), "%.2f" % (text['playtime_forever'] / 60)),
                                 inline=False)
                em.add_field(name='총 플레이 시간',
                             value=msg[2] + '님은 지난 2주간 {} 시간동안 플레이하셨어요!'.format("%.2f" % (total_time / 60)))
                await app.send_message(message.channel, embed=em)
            else:
                await app.send_message(message.channel, ":x: ID를 입력해주세요.")
        elif msg[1] == 'library':
            if len(msg) == 1:
                await app.send_message(message.channel, ":x: 명령어를 제대로 입력해주세요!.")
            else:
                if len(msg) == 2:
                    await app.send_message(message.channel, ":x: 스팀 아이디를 입력해주세요!.")
                    return
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await app.send_message(message.channel, ":x: 유효한 스팀 아이디를 사용해주세요.")
                    return
                userlib = requests.get(
                    'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=B6137C92F67299965B5E6BF287ECA4AE&steamid={}&include_appinfo=1&format=json'.format(steamid))
                userlib = userlib.json()
                games = userlib['response']['games']
                games = sorted(games, key=lambda game: game['playtime_forever'], reverse=True)
                if len(msg) > 3:
                    try:
                        requested_length = int(msg[3])
                    except ValueError:
                        if msg[3] == 'random':
                            game = random.choice(games)
                            playtime = '평생 {} 시간 플레이 함'.format('%.2f' % (game['playtime_forever'] / 60))
                            if 'playtime_2weeks' in game:
                                playtime += '\n지난 2주 간 {} 시간 플레이 함'.format('%.2f' % (game['playtime_2weeks'] / 60))
                            em = discord.Embed(title='{} ({})'.format(game['name'], game['appid']), description='{}\n플레이: steam://run/{}/'.format(playtime, game['appid']))
                            await app.send_message(message.channel, embed=em)
                            return
                        await app.send_message(message.channel, ":x: 게임 갯수는 정수를 사용해주세요.")
                        return
                else:
                    requested_length = 5
                if len(games) < requested_length:
                    requested_length = len(games)
                if requested_length > 25:
                    requested_length = 25
                i = 0
                em = discord.Embed(title='{} 님의 라이브러리에요.'.format(msg[2]),
                                   description='플레이시간 상위 {}개를 불러왔어요.'.format(requested_length), inline=False,
                                   colour=discord.Colour(0x1b2838))
                for game in games:
                    if i == requested_length:
                        break
                    playtime = '평생 {} 시간 플레이 함'.format('%.2f' % (game['playtime_forever'] / 60))
                    if 'playtime_2weeks' in game:
                        playtime += '\n지난 2주 간 {} 시간 플레이 함'.format('%.2f' % (game['playtime_2weeks'] / 60))

                    em.add_field(name='{} ({})'.format(game['name'], game['appid']),
                                 value='{}\n플레이: steam://run/{}/'.format(playtime, game['appid']), inline=False)
                    i += 1
                await app.send_message(message.channel, embed=em)
        elif msg[1] == 'wishlist':
            if len(msg) == 1:
                await app.send_message(message.channel, ":x: 명령어를 제대로 입력해주세요!.")
            else:
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await app.send_message(message.channel, ":x: 유효한 스팀 아이디를 사용해주세요.")
                    return
                userwish = requests.get(
                    'https://store.steampowered.com/wishlist/profiles/{}/wishlistdata/'.format(steamid))
                userwish = userwish.json()
                if len(msg) > 3:
                    try:
                        requested_length = int(msg[3])
                    except ValueError:
                        await app.send_message(message.channel, ":x: 게임 갯수는 정수를 사용해주세요.")
                        return
                else:
                    requested_length = 20
                if len(userwish) < requested_length:
                    requested_length = len(userwish)
                if requested_length > 50:
                    requested_length = 50
                sortedNumbers = sorted(userwish, key=lambda wish: userwish[wish]['priority'] if userwish[wish][
                                                                                                    'priority'] != 0 else requested_length + 1)
                sortedNumbers += sorted(userwish, key=lambda wish: userwish[wish]['priority'] if userwish[wish][
                                                                                                     'priority'] == 0 else requested_length + 1)
                i = 0
                output = '찜 목록에 있는 게임 {}개를 불러왔어요.\n'.format(requested_length)
                for num in sortedNumbers:
                    if i == requested_length:
                        break
                    output += '{} ({})'.format(userwish[num]['name'], num)
                    if userwish[num].get('subs', False):
                        if userwish[num]['subs'][0].get('price', False):
                            output += ' - ₩ {:,}'.format(int(userwish[num]['subs'][0]['price']) // 100)
                    output += '\n'
                    i += 1
                em = discord.Embed(title='{} 님의 찜 목록이에요.'.format(msg[2]),
                                   description=output, inline=False,
                                   colour=discord.Colour(0x1b2838))

                await app.send_message(message.channel, embed=em)
        elif msg[1] == "profile":
            if len(msg) < 3:
                await app.send_message(message.channel, ":x: 스팀 아이디를 입력해주세요!.")
                return
            xmls = get_steam_id(msg[2], True)
            if xmls == 0:
                await app.send_message(message.channel, ":x: 유효한 스팀 아이디를 사용해주세요.")
                return
            if xmls.find('onlineState').text == 'in-game':
                statusColor = discord.Colour(0x90ba3c)
            elif xmls.find('onlineState').text == 'online':
                statusColor = discord.Colour(0x57cbde)
            elif xmls.find('onlineState').text == 'offline':
                statusColor = discord.Colour(0x898989)
            em = discord.Embed(title=xmls.find('steamID').text,
                               description=xmls.find('stateMessage').text.replace('<br/>', ': '),
                               colour=statusColor).set_thumbnail(url=xmls.find('avatarIcon').text)
            em.add_field(name='요약', value=xmls.find('summary').text.replace('<br>', '\n'), inline=False)
            await app.send_message(message.channel, embed=em)


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


async def realtime():
    global isRealtimeAlive, realtimeQueue, wst
    await asyncio.sleep(0.1)

    while True:
        await asyncio.sleep(0.1)
        if not isRealtimeAlive:
            try:
               wst.start()
               isRealtimeAlive = True
            except RuntimeError:
                pass
        if len(realtimeQueue) < 1:
            continue
        recentRealtime = ''
        for realtimeText in realtimeQueue:
            recentRealtime += realtimeText + '\n'
        for channel in realtimeList:
            await app.send_message(app.get_channel(channel.id), recentRealtime)
        realtimeQueue.clear()


app.run(token)
