import requests
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup

import data.urls as _urls


def get_steam_id(name, want_all=False):
    xmls = requests.get(_urls.STEAM_PROFILE_XML.format(name)).text
    xmls = et.fromstring(xmls)
    try:
        xmls.find('error').text
        return 0
    except AttributeError:
        if want_all:
            return xmls
        return xmls.find('steamID64').text


def get_game_id(name):
    # Do Something
    src = requests.get(_urls.STEAM_SEARCH.format(name.replace(' ', '+'))).text
    src = BeautifulSoup(src, 'html.parser')
    try:
        target = src.find_all('a', class_='search_result_row')[0]
        game_id = target['href'].replace('https://store.steampowered.com/app/', '').split('/')[0]
        title = target.find('span', class_='title').text
        return {game_id: title}
    except IndexError:
        return {}
