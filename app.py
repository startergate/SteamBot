# -*- coding: utf-8 -*-
# https://discordapp.com/oauth2/authorize?client_id=555339236035919882&scope=bot&permissions=67584
import asyncio
import os
import random

import discord
from dotenv import load_dotenv
from markdownify import markdownify as md

import data.urls as urls
from modules.liveupdate import *

from utils.help import Help
from utils.steamapi import *

load_dotenv()

client = discord.Client()
help = Help()

token = os.getenv('token')
steam_api_key = os.getenv('steam_api_key')
invite = os.getenv('invite')

loop = asyncio.get_event_loop()


@client.event
async def on_ready():
    print("로그인 정보>")
    print(client.user.name)
    print(client.user.id)
    print("=============")

    await client.change_presence(activity=discord.Activity(name="도움말을 받으려면 st!help ", type=1))

    loop.create_task(realtime())


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return None

    if message.content.startswith('st!'):
        message.content = message.content.replace('st!', '', 1)
    else:
        return None

    msg = message.content.split(' ')
    if msg[0] == "help":
        if len(msg) == 1:
            await message.channel.send(embed=help.getHelp())
        else:
            await message.channel.send(embed=help.getSpecificHelp(msg[1]))
    if msg[0] == 'add':
        await message.channel.send(f"아래 링크로 들어가서 SteamBot을 서버에 추가할 수 있어요!\n`{invite}`")
    elif msg[0] == "game":
        if len(msg) == 1:
            await message.channel.send(":x: 명령어를 제대로 입력해주세요!.")
            await message.channel.send(embed=help.getSpecificHelp("game"))
        elif msg[1] == 'search':
            if len(msg) < 3:
                await message.channel.send(":x: 검색어를 입력해주세요!.")
                return

            query = message.content.replace('st!game search ', '')
            src = requests.get(urls.STEAM_SEARCH.format(query.lower().replace(' ', '+'))).text
            src = BeautifulSoup(src, 'html.parser')
            games = src.find_all('a', class_='search_result_row')
            if not games:
                await message.channel.send(":x: 게임을 찾지 못했어요.")
                return
            output_text = ''
            for game in games:
                price = game.find('div', class_='search_price').getText().strip()
                temp = price.split('₩')
                if len(temp) >= 3:
                    price = '₩ {} ~~₩ {}~~ ({})'.format(temp[2], temp[1],
                                                        game.find('div', class_='search_discount').find('span').text)
                if not price:
                    price = '기록 없음'
                output_text += '\n' + game.find('span', class_='title').getText() + '  |  ' + price
            em = discord.Embed(title='"{}"을 검색한 결과, {}개의 게임을 찾았어요!'.format(query, len(games)), description=output_text,
                               colour=discord.Colour(0x1b2838))
            await message.channel.send(embed=em)
        elif msg[1] == 'bestseller':
            if len(msg) == 2:
                bestseller_src = requests.get(urls.STEAM_BESTSELLER)
                bestseller_src = BeautifulSoup(bestseller_src.text, 'html.parser')
                bst_seller = bestseller_src.find_all('a', class_='search_result_row')

                output_text = '스팀의 최고 판매 제품 목록이에요.'
                for product in bst_seller:
                    price = product.find('div', class_='search_price').getText().strip()
                    temp = price.split('₩')
                    if len(temp) >= 3:
                        price = '₩ ' + temp[2] + ' ~~₩ ' + temp[1] + '~~'
                    output_text += '\n' + product.find('span', class_='title').getText() + ' | ' + price

                em = discord.Embed(title='스팀 최고 판매 제품', description=output_text, colour=discord.Colour(0x1b2838))
                await message.channel.send(embed=em)
            elif msg[2] == 'new':
                bestseller_src = requests.get(urls.STEAM_BESTSELLER_NEW)
                bestseller_src = BeautifulSoup(bestseller_src.text, 'html.parser')
                bst_seller = bestseller_src.find('div', id='tab_newreleases_content')
                bst_seller = bst_seller.find_all('a', class_='tab_item')
                output_text = '스팀의 신제품 최고 판매 목록이에요.'
                previous_title = ''
                for product in bst_seller:
                    if previous_title == product.find('div', class_='tab_item_name').getText():
                        continue
                    previous_title = product.find('div', class_='tab_item_name').getText()
                    if product.find('div', class_='discount_final_price'):
                        price = product.find('div', class_='discount_final_price').getText().strip()
                    else:
                        price = '기록 없음'
                    if product.find('div', class_='discount_original_price'):
                        price += ' ~~' + product.find('div', class_='discount_original_price').getText().strip() + '~~'
                    output_text += '\n' + product.find('div', class_='tab_item_name').getText() + ' | ' + price

                em = discord.Embed(title='스팀 최고 판매 제품', description=output_text, colour=discord.Colour(0x1b2838))
                await message.channel.send(embed=em)
            elif msg[2] == 'upcoming':
                bestseller_src = requests.get(urls.STEAM_UPCOMING_GAME)
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
                            price += ' ~~' + product.find('div',
                                                          class_='discount_original_price').getText().strip() + '~~'
                    output_text += '\n' + product.find('div', class_='tab_item_name').getText() + price

                em = discord.Embed(title='스팀 최고 인기 출시 예정 제품', description=output_text, colour=discord.Colour(0x1b2838))
                await message.channel.send(embed=em)
        elif msg[1] == 'new':
            new_src = requests.get(urls.STEAM_NEW_GAME)
            new_src = BeautifulSoup(new_src.text, 'html.parser')
            new_prd = new_src.find_all('a', class_='search_result_row')

            output_text = '스팀의 최신 출시 제품 목록이에요.'
            for product in new_prd:
                if product.find('div', class_='search_price').getText().strip() != '':
                    price = product.find('div', class_='search_price').getText().strip()
                    temp = price.split('₩')
                    if len(temp) >= 3:
                        price = '₩ {} ~~₩ {}~~'.format(temp[2], temp[1])
                else:
                    price = "기록 없음"
                output_text += '\n{}  |  {}'.format(product.find('span', class_='title').getText(), price)

            em = discord.Embed(title='스팀 최신 출시 제품', description=output_text, colour=discord.Colour(0x1b2838))
            await message.channel.send(embed=em)
        elif msg[1] == 'specials':
            new_src = requests.get(urls.STEAM_SPECIALS)
            new_src = BeautifulSoup(new_src.text, 'html.parser')
            new_prd = new_src.find_all('a', class_='search_result_row')

            output_text = '스팀의 인기 할인 제품 목록이에요.'
            for product in new_prd:
                if product.find('div', class_='search_price').getText().strip() != '':
                    price = product.find('div', class_='search_price').getText().strip()
                    temp = price.split('₩')
                    if len(temp) >= 3:
                        price = '₩ ' + temp[2] + ' ~~₩ ' + temp[1] + '~~'
                else:
                    price = "기록 없음"
                output_text += '\n' + product.find('span', class_='title').getText() + '  |  ' + price

            em = discord.Embed(title='스팀 인기 할인 제품', description=output_text, colour=discord.Colour(0x1b2838))
            await message.channel.send(embed=em)
        elif msg[1] == 'hot':
            if len(msg) > 2:
                try:
                    requested_length = int(msg[3])
                except ValueError:
                    await message.channel.send(":x: 게임 갯수는 정수를 사용해주세요.")
                    return
            else:
                requested_length = 10

            hot_src = requests.get(urls.STEAM_HOT_GAME)
            hot_src = BeautifulSoup(hot_src.text, 'html.parser')
            hot_prd = hot_src.find_all('tr', class_='player_count_row')
            if len(hot_prd) < requested_length:
                requested_length = len(hot_prd)
            if requested_length > 25:
                requested_length = 25
            em = discord.Embed(title='스팀 최다 플레이어', description='스팀의 현재 최다 플레이어 수 목록이에요.',
                               colour=discord.Colour(0x1b2838))
            i = 0
            for product in hot_prd:
                if i == requested_length:
                    break
                name = '{} ({})'.format(product.find('a', class_='gameLink').getText(),
                                        product.find('a', class_='gameLink')['href'].replace(
                                            'https://store.steampowered.com/app/', '').split('/')[0])
                value = "현재 플레이어: {}명 | 오늘 최고 기록: {}명".format(
                    product.find_all('span', class_='currentServers')[0].getText(),
                    product.find_all('span', class_='currentServers')[1].getText())
                em.add_field(name=name, value=value, inline=False)

                i += 1

            await message.channel(embed=em)
        elif msg[1] == 'news':
            if len(msg) > 2:
                requested_length = 10
                halflife3 = ['halflife 3', 'hl3', 'halflife3', 'hl 3']
                if message.content.replace('st!game news ', '').lower() in halflife3:
                    await message.channel.send(':x: 이미 뒤진 게임이에요.')
                    return
                id = get_game_id(message.content.replace('st!game news ', ''))
                if id == {}:
                    await message.channel.send(':x: 게임을 찾을 수 없어요.')
                    return
                await message.channel.send(":white_check_mark: 로딩 중 입니다.")
                keys = list(id.keys())
                news_src = requests.get(
                    urls.STEAM_GAME_NEWS.format(
                        keys[0], requested_length))
                news_src = news_src.json()

                news_text = news_src['appnews']['newsitems']
                if requested_length > len(news_text):
                    requested_length = len(news_text)
                em = discord.Embed(title=id[keys[0]], description="{}개의 뉴스를 가져왔어요.".format(requested_length))
                i = 0
                for news in news_text:
                    if i > requested_length:
                        break
                    em.add_field(name='{} - {}'.format(news['feedlabel'], news['title']),
                                 value=md(news['contents']) + ' **[자세히 보기]({})**'.format(news['url']))
                    i += 1
                await message.channel.send(embed=em)
            else:
                await message.channel.send(':x: 게임 이름을 입력해주세요.')
        elif msg[1] == 'realtime':
            if len(msg) > 2:
                if msg[2] == 'stop':
                    if message.channel not in realtimeList:
                        await message.channel.send(':x: 등록되지 않은 채널이에요!')
                        return
                    realtimeList.remove(message.channel)
                    await message.channel.send(':white_check_mark: 스팀 실시간 업데이트 수신을 중지했어요!')
                    return
            if message.channel in realtimeList:
                await message.channel.send(':x: 이미 등록된 채널이에요!')
                return
            realtimeList.append(message.channel)
            await message.channel.send(':white_check_mark: 지금부터 이 채널에서 스팀 실시간 업데이트를 받을 수 있어요!')
    elif msg[0] == "user":
        if len(msg) == 1:
            await message.channel.send(":x: 명령어를 제대로 입력해주세요!.")
            await message.channel.send(embed=help.getSpecificHelp("user"))
        elif msg[1] == 'recent':
            if len(msg) == 2:
                await message.channel.send(":x: 스팀 아이디를 입력해주세요!.")
            elif len(msg) == 3:
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await message.channel.send(":x: 유효한 스팀 아이디를 사용해주세요.")
                    return
                recents = requests.get(
                    urls.STEAM_RECENT_PLAYED.format(steam_api_key, steamid))
                recents = recents.json()
                if recents['response']['total_count'] == 0:
                    await message.channel.send(
                        ':frowning: 어떠한 게임도 불러오지 못했어요. 아무런 게임도 플레이하지 않으셨을수도 있고, 스팀 프로필이 비공개일수도 있어요.')
                    return
                em = discord.Embed(title='{} 님이 최근에 플레이하신 게임 목록이에요.'.format(msg[2]),
                                   description='지난 2주간 {}개의 게임을 플레이하셨어요.'.format(recents['response']['total_count']),
                                   colour=discord.Colour(0x1b2838))
                total_time = 0
                for text in recents['response']['games']:
                    print(text)
                    total_time += text['playtime_2weeks']
                    em.add_field(name='{} ({})'.format(text['name'], text['appid']),
                                 value='지난 2주간 {} 시간동안 플레이 함\n평생 동안 {} 시간동안 플레이 함'.format(
                                     "%.2f" % (text['playtime_2weeks'] / 60), "%.2f" % (text['playtime_forever'] / 60)),
                                 inline=False)
                em.add_field(name='총 플레이 시간',
                             value=msg[2] + '님은 지난 2주간 {} 시간동안 플레이하셨어요!'.format("%.2f" % (total_time / 60)))
                await message.channel.send(embed=em)
            else:
                await message.channel.send(":x: ID를 입력해주세요.")
        elif msg[1] == 'library':
            if len(msg) == 1:
                await message.channel.send(":x: 명령어를 제대로 입력해주세요!.")
            else:
                if len(msg) == 2:
                    await message.channel.send(":x: 스팀 아이디를 입력해주세요!.")
                    return
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await message.channel.send(":x: 유효한 스팀 아이디를 사용해주세요.")
                    return
                userlib = requests.get(
                    urls.STEAM_LIBRARY.format(steam_api_key, steamid))
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
                            em = discord.Embed(title='{} ({})'.format(game['name'], game['appid']),
                                               description='{}\n플레이: steam://run/{}/'.format(playtime, game['appid']))
                            await message.channel.send(embed=em)
                            return
                        await message.channel.send(":x: 게임 갯수는 정수를 사용해주세요.")
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
                await message.channel.send(embed=em)
        elif msg[1] == 'wishlist':
            if len(msg) == 1:
                await message.channel.send(":x: 명령어를 제대로 입력해주세요!.")
            else:
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await message.channel.send(":x: 유효한 스팀 아이디를 사용해주세요.")
                    return
                wishlist = requests.get(urls.STEAM_WISHLIST.format(steamid))
                wishlist = wishlist.json()
                if len(msg) > 3:
                    try:
                        requested_length = int(msg[3])
                    except ValueError:
                        await message.channel.send(":x: 게임 갯수는 정수를 사용해주세요.")
                        return
                else:
                    requested_length = 20
                if len(wishlist) < requested_length:
                    requested_length = len(wishlist)
                if requested_length > 50:
                    requested_length = 50
                sortedNumbers = sorted(wishlist, key=lambda wish: wishlist[wish]['priority'] if wishlist[wish][
                                                                                                    'priority'] != 0 else requested_length + 1)
                sortedNumbers += sorted(wishlist, key=lambda wish: wishlist[wish]['priority'] if wishlist[wish][
                                                                                                     'priority'] == 0 else requested_length + 1)
                i = 0
                output = '찜 목록에 있는 게임 {}개를 불러왔어요.\n'.format(requested_length)
                for num in sortedNumbers:
                    if i == requested_length:
                        break
                    output += '{} ({})'.format(wishlist[num]['name'], num)
                    if wishlist[num].get('subs', False):
                        if wishlist[num]['subs'][0].get('price', False):
                            output += ' - ₩ {:,}'.format(int(wishlist[num]['subs'][0]['price']) // 100)
                    output += '\n'
                    i += 1
                em = discord.Embed(title='{} 님의 찜 목록이에요.'.format(msg[2]),
                                   description=output, inline=False,
                                   colour=discord.Colour(0x1b2838))

                await message.channel.send(embed=em)
        elif msg[1] == "profile":
            if len(msg) < 3:
                await message.channel.send(":x: 스팀 아이디를 입력해주세요!.")
                return
            xmls = get_steam_id(msg[2], True)
            if xmls == 0:
                await message.channel.send(":x: 유효한 스팀 아이디를 사용해주세요.")
                return
            if xmls.find('onlineState').text == 'in-game':
                statusColor = discord.Colour(0x90ba3c)
            elif xmls.find('onlineState').text == 'online':
                statusColor = discord.Colour(0x57cbde)
            else:
                statusColor = discord.Colour(0x898989)
            em = discord.Embed(title=xmls.find('steamID').text,
                               description=xmls.find('stateMessage').text.replace('<br/>', ': '),
                               colour=statusColor).set_thumbnail(url=xmls.find('avatarIcon').text)
            em.add_field(name='요약', value=xmls.find('summary').text.replace('<br>', '\n'), inline=False)
            await message.channel.send(embed=em)


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
            await client.get_channel(channel.id).send(recentRealtime)
        realtimeQueue.clear()


client.run(token)
