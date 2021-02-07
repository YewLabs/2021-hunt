import json
import sys
import random
import threading
import os
import os.path
import asyncio
import websockets
import http.server
import socketserver
import importlib
import types
import datetime

# import logging
# logger = logging.getLogger('websockets')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

os.chdir(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, '.')

import hunt.special_puzzles.ktane.game
from hunt.special_puzzles.ktane.game import KtaneGame, KtaneActionType

STATIC_PORT = 8000
WEBSOCKETS_PORT = 8001

class ReusableServer(socketserver.TCPServer):
    allow_reuse_address = True

def make_static():
    Handler = http.server.SimpleHTTPRequestHandler
    with ReusableServer(('localhost', STATIC_PORT), Handler) as httpd:
        httpd.serve_forever()

data = {'world':''}
ws_map = {}

def reload_module():
    sys.modules.clear()

FAKE_LATENCY = 0 # ms
send_queue = []

class KtaneConsumer():
    def __init__(self, channel_name):
        self.channel_name = channel_name

    def handle_txn(self, msg, clid=None):
        global data

        if clid is None:
            clid = self.channel_name

        game = KtaneGame()

        game_data_valid = False
        try:
            game_data = json.loads(data['world'])
            game_data_valid = True
        except:
            game_data = {}

        if game_data_valid:
            game.from_dict(game_data)

        actions = game.handle(msg, clid)

        data['world'] = json.dumps(game.to_dict())
        return actions

    def handle_disconnect(self, clid=None):
        global data

        if clid is None:
            clid = self.channel_name

        game = KtaneGame()

        game_data_valid = False
        try:
            game_data = json.loads(data['world'])
            game_data_valid = True
        except:
            game_data = {}

        if not game_data_valid:
            print('disconnect: no game data found')
            return []

        game.from_dict(game_data)
        actions = game.handle_disconnect(clid)

        data['world'] = json.dumps(game.to_dict())
        return actions

    async def perform_send(self, action, clid):
        if action.targets is None:
            action.targets = [clid]
        for cl in action.targets:
            # this is a hack to make in-order sends
            # work with TeamworkTimeConsumer
            try:
                await ws_map[cl].send(json.dumps(action.msg))
            except:
                pass

    async def perform_actions(self, actions, clid):
        for action in actions:
            await {
                KtaneActionType.send: self.perform_send,
            }[action.action_type](action, clid)

    async def process_send_queue(self):
        global send_queue
        progress_point = datetime.datetime.now() - datetime.timedelta(milliseconds=FAKE_LATENCY)
        while len(send_queue) > 0:
            msg_data = send_queue[0]
            if msg_data[0] > progress_point:
                break
            if msg_data[2] == 'disconnect':
                print(msg_data[1] + ' disconnected')
                actions = self.handle_disconnect(msg_data[1])
            else:
                # print('received ' + str(msg_data[2]) + ' from ' + msg_data[1])
                actions = self.handle_txn(msg_data[2], msg_data[1])
            await self.perform_actions(actions, msg_data[1])
            send_queue = send_queue[1:]

    async def disconnected(self):
        global send_queue
        send_queue += [(
            datetime.datetime.now(),
            self.channel_name,
            'disconnect'
        )]
        await self.process_send_queue()

    async def handle(self, msg):
        global send_queue
        send_queue += [(
            datetime.datetime.now(),
            self.channel_name,
            json.loads(msg)
        )]
        await self.process_send_queue()

def make_websockets():
    async def on_connect(ws, path):
        name = str(random.randrange(1 << 30))
        ws_map[name] = ws
        async for m in ws:
            await KtaneConsumer(name).handle(m)
        await KtaneConsumer(name).disconnected()

    start_server = websockets.serve(on_connect, 'localhost', WEBSOCKETS_PORT)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

threading.Thread(target=make_static, args=()).start()
make_websockets()
