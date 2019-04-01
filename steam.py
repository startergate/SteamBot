import asyncio
import discord
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as et
import threading

from modules.liveupdate import *

app = discord.Client()

token = 'NTU1MzM5MjM2MDM1OTE5ODgy.D2p1kA.hM6p3MhaLbuJnS7H0hUeRrfG2ys'
realtime = SteamLiveUpdate(app)
@app.event
async def on_ready():
    print("로그인 정보>")
    print(app.user.name)
    print(app.user.id)
    print("=============")

    await app.change_presence(game=discord.Game(name="도움말을 받으려면 st!help ", type=1))



@app.event
async def on_message(message):
    if message.author.bot:
        return None
    msg = message.content.split(' ')
    if msg[0] == "st!help":
        em = discord.Embed(title='SteamBot', description='스팀봇을 사용해주셔서 감사합니다!', colour=discord.Colour(0x1b2838))
        em.add_field(name='st!help', value='도움! 무슨 명령어를 써야할지 모를 때 「도움!」을 외쳐주세요!', inline=False)
        em.add_field(name='st!profile [ username ]', value='유저의 프로필을 가져와요.', inline=False)
        em.add_field(name='st!game new', value='스팀 최근 출시 제품들을 가져와요.', inline=False)
        em.add_field(name='st!game specials', value='스팀 인기 할인 제품들을 가져와요.', inline=False)
        em.add_field(name='st!game bestseller', value='스팀 최고 인기 제품 상위 25개를 가져와요.', inline=False)
        em.add_field(name='st!game bestseller [ new, oncoming ]', value='스팀 인기 제품을 가져와요. 각각 신제품, 출시 예정 제품입니다.', inline=False)
        em.add_field(name='st!game recent [ username ]', value='유저가 최근 2주간 플레이한 게임을 가져와요.', inline=False)
        em.add_field(name='st!game library [ username ]', value='유저의 라이브러리를 10개 가져와요.', inline=False)
        em.add_field(name='st!game library [ username ] [ count ]', value='유저의 라이브러리를 입력한 만큼 가져와요. (최대 25개)', inline=False)
        em.add_field(name='st!game wishlist [ username ]', value='유저의 찜 목록를 10개 가져와요.', inline=False)
        em.add_field(name='st!game wishlist [ username ] [ count ]', value='유저의 찜 목록를 입력한 만큼 가져와요. (최대 50개)', inline=False)
        await app.send_message(message.channel, embed=em)
        if len(msg) > 1:
            await app.send_message(message.channel, "help 명령어는 st!help만 쓰셔도 쓸 수 있어요!")
    elif msg[0] == "st!profile":
        if len(msg) == 1:
            await app.send_message(message.channel, "스팀 아이디를 입력해주세요!.")
            return
        xmls = get_steam_id(msg[1], True)
        if xmls == 0:
            await app.send_message(message.channel, "유효한 스팀 아이디를 사용해주세요.")
            return
        if xmls.find('onlineState').text == 'in-game':
            statusColor = discord.Colour(0x90ba3c)
        elif xmls.find('onlineState').text == 'online':
            statusColor = discord.Colour(0x57cbde)
        elif xmls.find('onlineState').text == 'offline':
            statusColor = discord.Colour(0x898989)
        em = discord.Embed(title=xmls.find('steamID').text, description=xmls.find('stateMessage').text.replace('<br/>', ': '), colour=statusColor).set_thumbnail(url=xmls.find('avatarIcon').text)
        em.add_field(name='요약', value=xmls.find('summary').text.replace('<br>', '\n'), inline=False)
        await app.send_message(message.channel, embed=em)
    elif msg[0] == "st!game":
        if len(msg) == 1:
            await app.send_message(message.channel, "명령어를 제대로 입력해주세요!.")
        elif msg[1] == 'recent':
            if len(msg) == 2:
                await app.send_message(message.channel, "스팀 아이디를 입력해주세요!.")
            elif len(msg) == 3:
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await app.send_message(message.channel, "유효한 스팀 아이디를 사용해주세요.")
                    return
                recents = requests.get('http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=B6137C92F67299965B5E6BF287ECA4AE&steamid=' + steamid + '&format=json')
                recents = recents.json()
                if recents['response']['total_count'] == 0:
                    await app.send_message(message.channel, '어떠한 게임도 불러오지 못했어요. 아무런 게임도 플레이하지 않으셨을수도 있고, 스팀 프로필이 비공개일수도 있어요.')
                    return
                em = discord.Embed(title=msg[2] + '님이 최근에 플레이하신 게임 목록이에요.', description='지난 2주간 ' + str(recents['response']['total_count']) + '개의 게임을 플레이하셨어요.', colour=discord.Colour(0x1b2838))
                total_time = 0;
                for text in recents['response']['games']:
                    total_time += text['playtime_2weeks'];
                    em.add_field(name=text['name'] + ' (' + str(text['appid']) + ')', value='지난 2주간 ' + str("%.2f" % (text['playtime_2weeks'] / 60)) + ' 시간동안 플레이 함\n평생 동안 ' + str("%.2f" % (text['playtime_forever'] / 60)) + ' 시간동안 플레이 함', inline=False)
                em.add_field(name='총 플레이 시간', value=msg[2] + '님은 지난 2주간 ' + str("%.2f" % (total_time / 60)) + '시간동안 플레이하셨어요!')
                await app.send_message(message.channel, embed=em)
            else:
                await app.send_message(message.channel, "ID를 입력해주세요.")
        elif msg[1] == 'library':
            if len(msg) == 1:
                await app.send_message(message.channel, "명령어를 제대로 입력해주세요!.")
            else:
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await app.send_message(message.channel, "유효한 스팀 아이디를 사용해주세요.")
                    return
                userlib = requests.get('http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=B6137C92F67299965B5E6BF287ECA4AE&steamid=' + steamid + '&include_appinfo=1&format=json')
                userlib = userlib.json()
                games = userlib['response']['games']
                games = sorted(games, key=lambda game: game['playtime_forever'], reverse=True)
                if len(msg) > 3:
                    try:
                        requested_length = int(msg[3])
                    except ValueError:
                        await app.send_message(message.channel, "게임 갯수는 정수를 사용해주세요.")
                        return
                else:
                    requested_length = 10
                if len(games) < requested_length:
                    requested_length = len(games)
                if requested_length > 25:
                    requested_length = 25
                i = 0
                em = discord.Embed(title='{} 님의 라이브러리에요.'.format(msg[2]),
                                   description='플레이시간 상위 {}개를 불러왔어요.'.format(requested_length), inline=False, colour=discord.Colour(0x1b2838))
                for game in games:
                    if i == requested_length:
                        break
                    playtime = '평생 {} 시간 플레이 함'.format('%.2f' % (game['playtime_forever'] / 60))
                    if 'playtime_2weeks' in game:
                        playtime += '\n지난 2주 간 {} 시간 플레이 함'.format('%.2f' % (game['playtime_2weeks'] / 60))

                    em.add_field(name='{} ({})'.format(game['name'], game['appid']),
                                 value=playtime, inline=False)
                    i += 1
                await app.send_message(message.channel, embed=em)
        elif msg[1] == 'wishlist':
            if len(msg) == 1:
                await app.send_message(message.channel, "명령어를 제대로 입력해주세요!.")
            else:
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await app.send_message(message.channel, "유효한 스팀 아이디를 사용해주세요.")
                    return
                userwish = requests.get('https://store.steampowered.com/wishlist/profiles/{}/wishlistdata/'.format(steamid))
                userwish = userwish.json()
                if len(msg) > 3:
                    try:
                        requested_length = int(msg[3])
                    except ValueError:
                        await app.send_message(message.channel, "게임 갯수는 정수를 사용해주세요.")
                        return
                else:
                    requested_length = 20
                if len(userwish) < requested_length:
                    requested_length = len(userwish)
                if requested_length > 50:
                    requested_length = 50
                sortedNumbers = sorted(userwish, key=lambda wish: userwish[wish]['priority'] if userwish[wish]['priority'] != 0 else requested_length + 1)
                sortedNumbers += sorted(userwish, key=lambda wish: userwish[wish]['priority'] if userwish[wish]['priority'] == 0 else requested_length + 1)
                print(len(userwish))
                i = 0
                output = '찜 목록에 있는 게임 {}개를 불러왔어요.\n'.format(requested_length)
                print(sortedNumbers)
                for num in sortedNumbers:
                    print(userwish[num]);
                    if i == requested_length:
                        break
                    output += '{} ({})'.format(userwish[num]['name'], num)
                    print(userwish[num])
                    if userwish[num].get('subs', False):
                        if userwish[num]['subs'][0].get('price', False):
                            output += ' - ₩ {:,}'.format(int(userwish[num]['subs'][0]['price']) // 100)
                    output += '\n'
                    i += 1
                em = discord.Embed(title='{} 님의 찜 목록이에요.'.format(msg[2]),
                                   description=output, inline=False,
                                   colour=discord.Colour(0x1b2838))

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
                    output_text += '\n' + product.find('span', class_='title').getText() + '  |  ' + price

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
                        price = '₩ ' + temp[2] + ' ~~₩ ' + temp[1] + '~~'
                else:
                    price = "기록 없음"
                output_text += '\n' + product.find('span', class_='title').getText() + '  |  ' + price

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
        elif msg[1] == 'realtime':
            realtime.AddList(message.channel)
            await app.send_message(message.channel, ':white_check_mark: 지금부터 이 채널에서 스팀 실시간 업데이트를 받을 수 있어요!')


def get_steam_id(name, want_all=False):
    xmls = requests.get('https://steamcommunity.com/id/' + name + '/?xml=1').text
    xmls = et.fromstring(xmls)
    try:
        xmls.find('error').text
        return 0
    except AttributeError:
        if want_all:
            return xmls
        return xmls.find('steamID64').text


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False








app.run(token)