import base64
import json
import time

from django.db import models, DatabaseError
from spoilr.models import *
from asgiref.sync import async_to_sync
from channels.exceptions import ChannelFull

from hunt.teamwork import TeamworkTimeConsumer
from hunt.special_puzzles.ktane.game import *
from hunt.special_puzzles.ktane.ws_action import *
from hunt.special_puzzles.ktane.validate import Validator as V

class KtaneTeamData(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    world = models.TextField()

    def __str__(self):
        return '%s' % (self.team)

class KtaneHighScoreData(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '%s (%d)' % (self.team, self.score)

    class Meta:
        indexes = [
            models.Index(
                fields=['score'],
                name='score_idx'
            ),
        ]

FAST_PATH_TIMEOUT = datetime.timedelta(milliseconds=1000)
# Warning: this should be kept less than PING_TIMEOUT in players.py
CLIENT_PING_TIMEOUT = datetime.timedelta(seconds=10)
# TODO: set these to large numbers (e.g. 100/1000) once we're done testing
MAX_TEAM_CACHE_SIZE = 100
MAX_CLIENT_CACHE_SIZE = 1000

# This tracks the last ping of each team so that if we've
# checked the database less than FAST_PATH_TIMEOUT ago,
# we don't need to go through the database again
class FastPathHelper():
    def __init__(self):
        # stores tuples of last ping time and rotate_txn lower bound
        self.team_cache = {}
        # stores the last ping time
        self.client_cache = {}

    def update_rotate_txn(self, team_id, rotate_txn):
        if team_id in self.team_cache:
            self.team_cache[team_id] = (self.team_cache[team_id][0], rotate_txn)

    def remove_client(self, clid):
        self.client_cache.pop(clid, None)

    def remove_team(self, team_id):
        self.team_cache.pop(team_id, None)

    def purge_old(self):
        if len(self.team_cache) > MAX_TEAM_CACHE_SIZE:
            teams_by_time = [(v[0], team_id) for team_id, v in self.team_cache.items()]
            teams_by_time.sort()
            for last_ping, team_id in teams_by_time[:MAX_TEAM_CACHE_SIZE//2]:
                del self.team_cache[team_id]
        if len(self.client_cache) > MAX_TEAM_CACHE_SIZE:
            clients_by_time = [(v, clid) for clid, v in self.client_cache.items()]
            clients_by_time.sort()
            for last_ping, clid in clients_by_time[:MAX_TEAM_CACHE_SIZE//2]:
                del self.client_cache[clid]

    # returns whether an update is needed, and only does
    # the update if so
    def update(self, team_id, clid, is_ping, rotate_txn):
        if rotate_txn is None:
            rotate_txn = 0
        curr_time = datetime.datetime.now()
        self.purge_old()
        need_update = False
        if team_id not in self.team_cache:
            self.team_cache[team_id] = (curr_time, rotate_txn)
            need_update = True
        if clid not in self.client_cache:
            self.client_cache[clid] = curr_time
            need_update = True
        if need_update:
            return True
        last_team_ping, old_rotate_txn = self.team_cache[team_id]
        last_cl_ping = self.client_cache[clid]

        need_update_txn = (not is_ping) and rotate_txn >= old_rotate_txn
        need_update_team_ping = curr_time >= last_team_ping + FAST_PATH_TIMEOUT
        need_update_cl_ping = curr_time >= last_cl_ping + CLIENT_PING_TIMEOUT
        if (not need_update_txn) and (not need_update_team_ping) and (not need_update_cl_ping):
            return False
        new_txn = rotate_txn if need_update_txn else old_rotate_txn
        new_team_ping = curr_time if need_update_team_ping else last_team_ping
        new_cl_ping = curr_time if need_update_cl_ping else last_cl_ping
        self.team_cache[team_id] = (new_team_ping, new_txn)
        self.client_cache[clid] = new_cl_ping
        return True

fast_path_helper = FastPathHelper()

class KtaneConsumer(TeamworkTimeConsumer):
    def setup(self):
        super(KtaneConsumer, self).setup(610)

    def update_fast_path_helper(self, game):
        team_id = self.team.y2021teamdata.tempest_id
        clid = self.channel_name
        fast_path_helper.update_rotate_txn(team_id, game.rotate_txn)
        if clid not in game.player_face:
            fast_path_helper.remove_client(clid)
        if len(game.player_face) == 0:
            fast_path_helper.remove_team(team_id)

    def safe_run_database_op(self, operation):
        success = False
        actions = None
        try:
            actions = operation()
            success = True
        except DatabaseError:
            pass
        if not success:
            self.close()
        return actions, success

    @transaction.atomic
    def handle_txn(self, msg):
        data = KtaneTeamData.objects.select_for_update().get_or_create(team=self.team)[0]
        game = KtaneGame()

        game_data_valid = False
        try:
            game_data = json.loads(data.world)
            game_data_valid = True
        except:
            game_data = {}

        if game_data_valid:
            game.from_dict(game_data)

        actions = game.handle(msg, self.channel_name)
        score = game.win_time_left

        self.update_fast_path_helper(game)

        data.world = json.dumps(game.to_dict())
        data.save()

        if score is not None:
            self.set_high_score(score)

        return actions

    @transaction.atomic
    def handle_disconnect(self):
        data = KtaneTeamData.objects.select_for_update().get_or_create(team=self.team)[0]
        game = KtaneGame()

        game_data_valid = False
        try:
            game_data = json.loads(data.world)
            game_data_valid = True
        except:
            game_data = {}

        if not game_data_valid:
            return []

        game.from_dict(game_data)
        actions = game.handle_disconnect(self.channel_name)

        self.update_fast_path_helper(game)

        data.world = json.dumps(game.to_dict())
        data.save()
        return actions

    def perform_send(self, action):
        dead_clients = set()
        if action.targets is None:
            action.targets = [self.channel_name]
        for cl in action.targets:
            # this is a hack to make in-order sends
            # work with TeamworkTimeConsumer
            try:
                async_to_sync(self.channel_layer.send)(cl, {
                    'type': 'channel.receive_broadcast',
                    'data': action.msg
                })
            except ChannelFull:
                dead_clients.add(cl)
        return dead_clients

    def perform_actions(self, actions):
        while True:
            dead_clients = set()
            for action in actions:
                new_dead_clients = {
                    KtaneActionType.send: self.perform_send,
                }[action.action_type](action)
                dead_clients.update(new_dead_clients)
            if len(dead_clients) == 0:
                break

            actions, success = self.safe_run_database_op(lambda: self.handle_dead_clients(dead_clients))
            if not success:
                break

    @transaction.atomic
    def handle_dead_clients(self, dead_clients):
        data = KtaneTeamData.objects.select_for_update().get_or_create(team=self.team)[0]
        game = KtaneGame()

        game_data_valid = False
        try:
            game_data = json.loads(data.world)
            game_data_valid = True
        except:
            game_data = {}

        if not game_data_valid:
            return []

        game.from_dict(game_data)
        actions = game.players_manager.handle_disconnect_many(dead_clients)

        self.update_fast_path_helper(game)

        data.world = json.dumps(game.to_dict())
        data.save()
        return actions

    def disconnected(self):
        if not hasattr(self, 'team'):
            return
        # print(self.channel_name + ' disconnected')

        actions, success = self.safe_run_database_op(lambda: self.handle_disconnect())
        if not success:
            return

        self.perform_actions(actions)

    def get_high_scores(self):
        if not KtaneHighScoreData.objects.filter(team=self.team).exists():
            return None
        SCORES_TABLE_SIZE = 10
        scores = list(KtaneHighScoreData.objects.order_by('-score').values_list('team__name', 'score')[:SCORES_TABLE_SIZE])
        # real high score by creators
        scores += [('✈️✈️✈️ Galactic Trendsetters ✈️✈️✈️', 861009)]
        scores.sort(key=lambda t: t[1], reverse=True)
        return scores[:SCORES_TABLE_SIZE]

    def set_high_score(self, score):
        data = KtaneHighScoreData.objects.select_for_update().get_or_create(team=self.team)[0]
        if score > data.score:
            data.score = score
            data.save()

    def handle(self, msg):
        # print('received ' + str(msg) + ' from ' + self.channel_name)
        if not hasattr(self, 'team'):
            # this should have been dealt with by the upper layer
            # so it isn't actually necessary
            self.perform_actions([KtaneAction.make_send({
                'type': 'badauth',
            })])
            return

        # this should be all the validation that is performed
        # before update_pings is called
        if not V.is_dict(msg) or not V.has_key(msg, 'type'):
            return
        msg_type = msg['type']
        # for debug server
        if msg_type == 'AUTH':
            return

        # fast path
        is_ping = msg_type == 'ping'
        rotate_txn = msg['rotateTxn'] if 'rotateTxn' in msg else None
        if is_ping or rotate_txn is not None:
            team_id = self.team.y2021teamdata.tempest_id
            clid = self.channel_name
            need_update = fast_path_helper.update(team_id, clid, is_ping, rotate_txn)
            if not need_update:
                self.perform_actions([KtaneAction.make_send({
                    'type': 'pong'
                })])
                return

        actions, success = self.safe_run_database_op(lambda: self.handle_txn(msg))
        if not success:
            return

        for action in actions:
            if action.is_send() and 'hiscores' in action.msg:
                try:
                    action.msg['hiscores'] = self.get_high_scores()
                except DatabaseError:
                    pass
        self.perform_actions(actions)
