import discord


class Help:
    def getHelp(self):
        em = discord.Embed(title='SteamBot', description='스팀봇을 사용해주셔서 감사합니다!', colour=discord.Colour(0x1b2838))
        em.add_field(name='st!help', value='도움! 무슨 명령어를 써야할지 모를 때 「도움!」을 외쳐주세요!\n각 명령어에 대한 자세한 도움말을 보려면 st!help 뒤에 명령어 이름을 붙여주세요.\n예) st!game에 대한 도움말 => st!help game', inline=False)
        em.add_field(name='st!add', value='스팀 봇 추가 링크를 가져와요.', inline=False)
        em.add_field(name='st!game', value='[ new, specials, bestseller, hot, search, realtime ]', inline=False)
        em.add_field(name='st!user', value='[ profile, recent, library, wishlist ]', inline=False)
        return em

    def getSpecificHelp(self, select):
        if select == 'game':
            em = discord.Embed(title='SteamBot - st!game',
                               description='st!game에 대한 도움말이에요!\n[] => 비 필수 사항이고, 안에 있는 단어 중 하나를 선택해서 입력해주세요.\n() => 필수 사항이고, 위치에 맞는 형태로 입력해주세요.',
                               colour=discord.Colour(0x1b2838))
            em.add_field(name='st!game new', value='스팀 최근 출시 제품들을 가져와요.', inline=False)
            em.add_field(name='st!game specials', value='스팀 인기 할인 제품들을 가져와요.', inline=False)
            em.add_field(name='st!game bestseller [ new, oncoming ]', value='스팀 인기 제품을 가져와요. `new`를 입력하면 신제품만 불러오고, `oncoming`을 입력하면 출시 예정 제품만 불러와요.', inline=False)
            em.add_field(name='st!game hot', value='스팀 최다 플레이 중인 게임을 가져와요. 명령어 뒤에 숫자를 붙이면 입력한 만큼 가져와요.', inline=False)
            em.add_field(name='st!game search ( query )', value='`query` 자리에 입력한 문장으로 스팀을 검색해요.', inline=False)
            em.add_field(name='st!game realtime', value='해당 채널로 스팀 실시간 업데이트를 가져와요. 뒤에 `stop`을 붙이면 업데이트 수신을 중지해요.', inline=False)
            return em
        elif select == 'user':
            em = discord.Embed(title='SteamBot - st!user',
                               description='st!user에 대한 도움말이에요!\n[] => 필수 사항이 아니고, 안에 있는 단어 중 하나를 선택해서 입력해주세요.\n() => 필수 사항이고, 위치에 맞는 형태로 입력해주세요.',
                               colour=discord.Colour(0x1b2838))
            em.add_field(name='st!user profile ( username )', value='`username` 자리에 입력한 유저의 프로필을 가져와요.', inline=False)
            em.add_field(name='st!user recent ( username )', value='`username` 자리에 입력한 유저가 최근 2주간 플레이한 게임을 가져와요.', inline=False)
            em.add_field(name='st!user library ( username ) ', value='`username` 자리에 입력한 유저의 라이브러리를 10개 가져와요. 명령어 뒤에 숫자를 붙이면 입력한 만큼 가져와요. (최대 25개)', inline=False)
            em.add_field(name='st!user wishlist ( username )', value='`username` 자리에 입력한 유저의 찜 목록를 10개 가져와요. 명령어 뒤에 숫자를 붙이면 입력한 만큼 가져와요. (최대 50개)', inline=False)
            return em
        else:
            em = discord.Embed(title='SteamBot - 없는 명령어', description='그런 명령어는 없어요.', colour=discord.Colour(0x1b2838))
            return em
