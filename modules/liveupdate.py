import asyncio
import discord
import json
import websocket
import threading

class SteamLiveUpdate(threading.Thread):
    realtimeList = []
    def AddList(self, channel):
        self.realtimeList.append(channel)

    def on_message_live(self, ws, message):
        message = json.loads(message)
        if message["Type"] == 'UsersOnline':
            return
        gameid = list(message['Apps'].keys())[0]
        messageStr = "{} #{} - Apps: {} ({})".format(message['Type'], message['ChangeNumber'], message['Apps'][gameid],
                                                     gameid)
        for channel in self.realtimeList:
            self.app.send_message(channel, messageStr)

    def on_error_live(self, ws, error):
        print(error)

    def on_close_live(self, ws):
        print("### closed ###")

    def on_open_live(self, ws):
        pass

    def __init__(self, app):

        self.app = app

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://steamdb.info/api/realtime/",
                                         on_message=self.on_message_live,
                                         on_error=self.on_error_live,
                                         on_close=self.on_close_live)
        self.ws.on_open = self.on_open_live
        self.ws.run_forever()
