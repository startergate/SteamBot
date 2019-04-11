import asyncio
import json
import websocket


def on_message_live(ws, message):
    print(message)
    message = json.loads(message)
    if message["Type"] == 'UsersOnline':
        return
    if message["Type"] == 'LogOff':
        return
    if message["Type"] == 'LogOn':
        return
    gameid = list(message['Apps'].keys())[0]
    messageStr = "{} #{} - Apps: {} ({})".format(message['Type'], message['ChangeNumber'], message['Apps'][gameid],
                                                     gameid)
    f = open('../buffer.txt', mode='wt', encoding='utf-8')
    f.write(messageStr)


def on_error_live(ws, error):
    print(error)


def on_close_live(ws):
    print("### closed ###")


def on_open_live(ws):
    pass


websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://steamdb.info/api/realtime/",
                            on_message=on_message_live,
                            on_error=on_error_live,
                            on_close=on_close_live)
ws.on_open = on_open_live
ws.run_forever()