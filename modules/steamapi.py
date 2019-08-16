import requests
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup


def get_steam_id(name, want_all=False):
    xmls = requests.get('https://steamcommunity.com/id/{}/?xml=1'.format(name)).text
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
    src = requests.get('https://store.steampowered.com/search/?term={}'.format(name.replace(' ', '+'))).text
    src = BeautifulSoup(src, 'html.parser')
    try:
        target = src.find_all('a', class_='search_result_row')[0]
    except IndexError:
        return {}
    return {target['href'].replace('https://store.steampowered.com/app/', '').split('/')[0]: target.find('span', class_='title').text}
