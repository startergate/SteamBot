import asyncio
import discord
import requests
from bs4 import BeautifulSoup;

app = discord.Client()

token = 'NTU1MzM5MjM2MDM1OTE5ODgy.D2p1kA.hM6p3MhaLbuJnS7H0hUeRrfG2ys'


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
        em = discord.Embed(title='SteamBot', description='스팀봇을 사용해주셔서 감사합니다!')
        em.add_field(name='st!help', value='도움! 무슨 명령어를 써야할지 모를 때 도움!을 외쳐주세요!', inline=False)
        em.add_field(name='st!game bestseller', value='스팀 최고 인기 제품 상위 25개를 가져옵니다.', inline=False)
        em.add_field(name='st!game bestseller [ new, oncoming ]', value='스팀 인기 제품을 가져옵니다. 각각 신제품, 출시 예정 제품입니다.', inline=False)
        em.add_field(name='st!game recent (Player)', value='유저가 최근 2주간 플레이한 게임을 가져옵니다.', inline=False)
        await app.send_message(message.channel, embed=em)
        if len(msg) > 1:
            await app.send_message(message.channel, "help 명령어는 st!help만 쓰셔도 작동합니다.")
    elif msg[0] == "st!game":
        if len(msg) == 1:
            await app.send_message(message.channel, "명령어를 제대로 입력해주세요!.")
        elif msg[1] == 'recent':
            if len(msg) == 3:
                steamid = get_steam_id(msg[2])
                if steamid == 0:
                    await app.send_message(message.channel, "유효한 스팀 아이디를 사용해주세요.")
                    return
                recents = requests.get('http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=B6137C92F67299965B5E6BF287ECA4AE&steamid=' + steamid + '&format=json')
                recents = recents.json()
                if recents['response']['total_count'] == 0:
                    await app.send_message(message.channel, '어떠한 게임도 불러오지 못했어요. 아무런 게임도 플레이하지 않으셨을수도 있고, 스팀 프로필이 비공개일수도 있어요.')
                    return
                em = discord.Embed(title='최근에 플레이하신 게임 목록입니다,, ' + message.author.name + ' 님!', description='그리고, 사용해주셔서 감사합니다!\n지난 2주간 ' + str(recents['response']['total_count']) + '개의 게임을 플레이하셨습니다..')
                total_time = 0;
                for text in recents['response']['games']:
                    total_time += text['playtime_2weeks'];
                    em.add_field(name=text['name'] + ' (' + str(text['appid']) + ')', value='지난 2주간 ' + str("%.2f" % (text['playtime_2weeks'] / 60)) + ' 시간동안 플레이함\n평생 동안 ' + str("%.2f" % (text['playtime_forever'] / 60)) + ' 시간동안 플레이함', inline=False)
                em.add_field(name='총 플레이 시간', value=msg[2] + '님은 지난 2주간 ' + str("%.2f" % (total_time / 60)) + '시간동안 플레이하셨습니다!')
                await app.send_message(message.channel, embed=em)
            else:
                await app.send_message(message.channel, "ID를 입력해주세요.")
        elif msg[1] == 'bestseller':
            if len(msg) == 2:
                bestseller_src = requests.get('https://store.steampowered.com/search/?filter=topsellers')
                bestseller_src = BeautifulSoup(bestseller_src.text, 'html.parser')
                bst_seller = bestseller_src.find_all('a', class_='search_result_row')

                output_text = '스팀의 최고 판매 제품 목록입니다!'
                for product in bst_seller:
                    price = product.find('div', class_='search_price').getText().strip();
                    temp = price.split('₩')
                    if len(temp) >= 3:
                        price = '₩ ' + temp[2] + ' ~~₩ ' + temp[1] + '~~'
                    output_text += '\n' + product.find('span', class_='title').getText() + '  |  ' + price

                em = discord.Embed(title='스팀 최고 판매 제품', description=output_text)
                await app.send_message(message.channel, embed=em)
            elif msg[2] == 'new':
                bestseller_src = requests.get('https://store.steampowered.com/explore/new/')
                bestseller_src = BeautifulSoup(bestseller_src.text, 'html.parser')
                bst_seller = bestseller_src.find('div', id='tab_newreleases_content')
                bst_seller = bst_seller.find_all('a', class_='tab_item')

                output_text = '스팀의 신제품 최고 판매 제품 목록입니다!'
                previous_title = ''
                for product in bst_seller:
                    if previous_title == product.find('div', class_='tab_item_name').getText():
                        continue
                    previous_title = product.find('div', class_='tab_item_name').getText()
                    price = product.find('div', class_='discount_final_price').getText().strip()
                    if product.find('div', class_='discount_original_price'):
                        price += ' ~~' + product.find('div', class_='discount_original_price').getText().strip() + '~~'
                    output_text += '\n' + product.find('div', class_='tab_item_name').getText() + ' | ' + price

                em = discord.Embed(title='스팀 최고 판매 제품', description=output_text)
                await app.send_message(message.channel, embed=em)
            elif msg[2] == 'oncoming':
                bestseller_src = requests.get('https://store.steampowered.com/explore/upcoming/')
                bestseller_src = BeautifulSoup(bestseller_src.text, 'html.parser')
                bst_seller = bestseller_src.find('div', id='tab_popular_comingsoon_content')
                bst_seller = bst_seller.find_all('a', class_='tab_item')

                output_text = '스팀의 인기순 출시 예정 목록입니다!'
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

                em = discord.Embed(title='스팀 최고 인기 출시 예정 제품', description=output_text)
                await app.send_message(message.channel, embed=em)


def get_steam_id(name):
    if isNumber(name) and len(name) > 17:
        return name
    jsons = requests.get('https://api.steamid.uk/request.php?api=9295K4J61YKD3357E6WA&player=' + name +'&request_type=5&format=json')
    jsons = jsons.json()
    if hasattr(jsons, 'error'):
        return 0

    return jsons['linked_users']['steamid64']


def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

app.run(token)
