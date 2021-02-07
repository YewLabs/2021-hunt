# See silenda/spoilr/puzzle_session.py
# Error Messages: <div id="puzzle-session-error-message-container"></div>
# <script src="/static/puzzle_session.js"></script>
# var session = new PuzzleSession("URL");
# session.json_request(JSON_PAYLOAD, function(res) {});

from django.db import models
from spoilr.models import *
from spoilr.puzzle_session import *

import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class PuzzleSampleSession(PuzzleSessionModelBase):
    stuff = models.IntegerField(null=True)

    def __str__(self):
        if self.stuff:
            return '[%s]' % (self.stuff)
        else:
            return '[no stuff]'

    class Meta:
        verbose_name = 'Sample Session'
        verbose_name_plural = 'Sample Sessions'

@puzzle_session(PuzzleSampleSession)
def cool_dynamic_view(request, state):
    # request.puzzle.answer has the answer, request.puzzle.y2021puzzledata.infinite_id has the infinite ID.
    new_stuff = int(request.POST['stuff'])
    if state.stuff != new_stuff:
        state.stuff = new_stuff
        return {'result': 'Failure'}
    else:
        return {'result': 'Match'}

class SamplePuzzleTeamData(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    cool_value = models.FloatField(default=0)

class SamplePuzzleConsumer(WebsocketConsumer):
    team = None

    def connect(self):
        async_to_sync(self.channel_layer.group_add)("chat", self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("chat", self.channel_name)

    @transaction.atomic
    def doDBStuff(self):
        data = SamplePuzzleTeamData.objects.get_or_create(team=self.team)[0]
        oldValue = data.cool_value
        data.cool_value = oldValue + 1
        data.save()
        return oldValue

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        if action == 'AUTH':
            try:
                self.team = Team.objects.get(y2021teamdata__auth=text_data_json['data'])
            except Exception as e:
                self.send(text_data=json.dumps({'error': text_data + ': ' + str(e)}))
            self.send(text_data=json.dumps({'msg': 'Hello ' + self.team.name + ': ' + str(self.doDBStuff())}))
            async_to_sync(self.channel_layer.group_send)("chat", {'type': 'chat.message', 'text': 'Joined Channel.'})

    def chat_message(self, event):
        self.send(text_data=event["text"])
