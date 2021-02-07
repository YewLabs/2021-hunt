import sys
import asyncio
import websockets
import json
import datetime

if len(sys.argv) != 2:
    print('needs one argument')

async def run():
    url = 'ws://' + sys.argv[1] + '/ws/puzzle/yweiyst'
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({
            'type': 'AUTH',
            'data': '5e1dc0f1f4244cbe5fa07f79fc94b0b50cff238723ef01e211144d33c5af1054',
        }))
        await ws.send(json.dumps({
            'type': 'join',
            'spectate': 'false',
        }))
        while True:
            msg = json.loads(await ws.recv())
            if msg['type'] == 'playerPos' or msg['type'] == 'updateState':
                break
        await ws.send(json.dumps({
            'type': 'start',
        }))
        rotate_txn = 0
        while True:
            msg = json.loads(await ws.recv())
            if msg['type'] == 'updateState':
                rotate_txn = msg['rotateTxn']
                break
        round_cnt = 0
        round_tot_latency = datetime.timedelta()
        while True:
            start_time = datetime.datetime.now()
            await ws.send(json.dumps({
                'type': 'rotate',
                'rotateTxn': rotate_txn,
                'rotDir': 0
            }))
            while True:
                msg = json.loads(await ws.recv())
                if msg['type'] == 'updateState' and 'rotateTxn' in msg:
                    rotate_txn = msg['rotateTxn']
                    round_cnt += 1
                    round_tot_latency += datetime.datetime.now() - start_time
                    if round_cnt == 10:
                        avg_latency = round_tot_latency / round_cnt
                        print('average latency for %d rotates = %.1f ms' % (round_cnt, avg_latency / datetime.timedelta(milliseconds=1)))
                        round_cnt = 0
                        round_tot_latency = datetime.timedelta()
                    break

asyncio.get_event_loop().run_until_complete(run())
