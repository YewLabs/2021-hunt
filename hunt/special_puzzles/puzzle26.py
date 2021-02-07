import asyncio
import base64
import json
import time

from hunt.teamwork import AsyncTeamworkTimeConsumer

IDLE_TIMEOUT_S = 5
DEAD_TIMEOUT_S = 60

IMAGE_PATH = '2021-hunt/puzzle/cooperation/solution/image.png'
ANSWER_IMAGE = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('utf-8')

class Puzzle26Consumer(AsyncTeamworkTimeConsumer):
    '''
    Teamwork Time implementation for Cooperation. The state is just a collection
    of each client's state, so it is ephemeral on the server and does not hit
    the database. When a consumer is created, it broadcasts request_init to
    existing consumers, which unicast back the current state. When the consumer
    gets updates from its client, it makes changes to the state and broadcasts
    update_state to the other consumers, which forward to their clients.
    '''

    def setup(self):
        super(Puzzle26Consumer, self).setup(26)
        self.world = {}

    async def handle(self, msg):
        if msg['type'] != 'updatePosition':
            return
        now = time.time()
        if self.world.get(self.channel_name) is not None:
            old = self.world[self.channel_name]
            if all(msg['data'][key] == old[key] for key in msg['data']) and now < old['t'] + 1:
                return
        update = {}
        for k, v in self.world.items():
            if v is not None:
                if now - v['t'] > DEAD_TIMEOUT_S:
                    update[k] = None
                elif now - v['t'] > IDLE_TIMEOUT_S and v['active']:
                    update[k] = dict(v, active=False)
        update[self.channel_name] = {
            'x': msg['data']['x'],
            'y': msg['data']['y'],
            'active': msg['data']['active'],
            'r': 0.1,
            't': now,
        }
        await self.channel_layer.group_send(self.group, {
            'type': 'puzzle26.update_state', 'world': update})

    async def disconnected(self):
        if self.world.get(self.channel_name) is not None:
            update = {self.channel_name: None}
            self.channel_layer.group_send(self.group, {
                'type': 'puzzle26.update_state', 'world': update})

    async def authed(self):
        await asyncio.gather(
            self.respond({'type': 'answerImage', 'data': f'data:image/png;base64,{ANSWER_IMAGE}'}),
            self.channel_layer.group_send(
                self.group, {'type': 'puzzle26.request_init', 'self': self.channel_name})
        )

    def export_state(self):
        ret = {}
        for k, v in self.world.items():
            if v is not None:
                ret[k] = dict(v)
                del ret[k]['t']
        return ret

    async def puzzle26_update_state(self, event):
        before = self.export_state()
        self.world.update(event['world'])
        after = self.export_state()
        if before != after and self.world.get(self.channel_name) is not None:
            await self.respond({'type': 'updatePositions', 'data': after})

    async def puzzle26_request_init(self, event):
        if event['self'] != self.channel_name:
            await self.channel_layer.send(event['self'], {
                'type': 'puzzle26.update_state', 'world': self.world})
