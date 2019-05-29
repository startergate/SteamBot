import json
import websocket
import threading

realtimeList = []
realtimeQueue = []
isRealtimeAlive = False;

def on_message_live(ws, message):
    print(message)
    message = json.loads(message)
    if message["Type"] == 'UsersOnline':
        return
    if message["Type"] == 'LogOff':
        return
    if message["Type"] == 'LogOn':
        return
    if len(list(message['Apps'].keys())) < 1:
        return
    gameid = list(message['Apps'].keys())[0]
    messageStr = "{} #{} - Apps: {} ({})".format(message['Type'], message['ChangeNumber'], message['Apps'][gameid],
                                                     gameid)
    if message['Packages'] != {}:
        packageid = list(message['Packages'].keys())[0]
        messageStr += ' - Packages: {} ({})'.format(message['Packages'][packageid], packageid);
    print(messageStr)
    realtimeQueue.append(messageStr)
    print(realtimeQueue)

def on_error_live(ws, error):
    print(error)

def on_close_live(ws):
    print("### closed ###")
    global isRealtimeAlive
    isRealtimeAlive = False

def on_open_live(ws):
    global isRealtimeAlive
    isRealtimeAlive = True

websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://steamdb.info/api/realtime/",
                                 on_message=on_message_live,
                                 on_error=on_error_live,
                                 on_close=on_close_live)
ws.on_open = on_open_live
wst = threading.Thread(target=ws.run_forever)
wst.daemon = True