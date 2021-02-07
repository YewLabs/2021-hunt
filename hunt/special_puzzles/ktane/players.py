import random
import datetime

from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.ws_action import *
from hunt.special_puzzles.ktane.validate import Validator as V

class KtanePlayersManager:
    def __init__(self, game):
        self.game = game
        self.last_ping_times = {}

    def from_dict(self, d):
        self.last_ping_times = {
            cl: datetime.datetime.fromtimestamp(ts)
            for cl, ts in d['last_ping_times'].items()
        }

    def to_dict(self):
        return {
            'last_ping_times': {
                cl: datetime.datetime.timestamp(dt)
                for cl, dt in self.last_ping_times.items()
            },
        }

    def get_empty_slots(self):
        return [
            i for i, face_players in enumerate(self.game.players)
            if len(face_players) == 0
        ]

    def get_player_counts(self):
        return [len(l) for l in self.game.players]

    def get_spectator_counts(self):
        return [len(l) for l in self.game.spectators]

    def get_players(self):
        return list(self.game.player_face.keys())

    def is_defuser(self, clid):
        if clid not in self.game.player_face:
            return False
        face = self.game.player_face[clid]
        if len(self.game.players[face.value]) == 0:
            return False
        return self.game.players[face.value][0] == clid

    def make_update_players_action(self):
        player_counts = self.get_player_counts()
        spectator_counts = self.get_spectator_counts()
        player_slot_filled = 0
        num_spectators = sum(player_counts) + sum(spectator_counts)
        for i in range(len(CubeFace)):
            if player_counts[i] != 0:
                num_spectators -= 1
                player_slot_filled |= 1 << i
        return KtaneAction.make_send_many({
            'type': 'players',
            'players': player_slot_filled,
            'spectators': num_spectators,
        }, self.get_players())

    def make_update_player_pos_action(self, clid):
        is_defuser = self.is_defuser(clid)
        return KtaneAction.make_send({
            'type': 'playerPos',
            'face': self.game.player_face[clid].value,
            'isDefuser': is_defuser,
            # piggyback high scores with playerPos messages
            # this will be set by the upper layer
            'hiscores': None,
        }, clid)

    def handle_disconnect_many(self, clids):
        actions = []

        for clid in clids:
            self.game.gods.pop(clid, None)

        # get initial defusers
        old_defusers = [
            (face_players[0] if len(face_players) > 0 else None)
            for face_players in self.game.players
        ]

        # remove disconnected clients
        self.game.players = [
            [cl for cl in face_players if cl not in clids]
            for face_players in self.game.players
        ]
        self.game.spectators = [
            [cl for cl in face_spectators if cl not in clids]
            for face_spectators in self.game.spectators
        ]

        # if there are empty slots, try to fill them with spectators
        empty_slots = self.get_empty_slots()
        spectators = [
            cl
            for face_players in self.game.players if len(face_players) > 1
            for cl in face_players[1:]
        ]
        if len(empty_slots) > len(spectators):
            empty_slots = empty_slots[:len(spectators)]
        subst_defusers = random.SystemRandom().sample(spectators, len(empty_slots))
        # remove substitute defusers
        self.game.players = [
            [cl for cl in face_players if cl not in subst_defusers]
            for face_players in self.game.players
        ]
        # put substitute defusers in empty slots
        for face, (empty_slot, defuser) in enumerate(zip(empty_slots, subst_defusers)):
            self.game.players[empty_slot] = [defuser]
        self.game.recompute_player_face()

        actions += [self.make_update_players_action()]

        # update players that have newly become defusers
        for face, (defuser, face_players) in enumerate(zip(old_defusers, self.game.players)):
            if len(face_players) == 0:
                continue
            if defuser is not None and face_players[0] == defuser:
                continue
            actions += [self.make_update_player_pos_action(
                face_players[0]
            )]

        for clid in clids:
            self.last_ping_times.pop(clid, None)

        if self.game.is_running():
            for clid in subst_defusers:
                # update substitute defusers
                actions += self.game.make_join_update_state_actions(clid)
        return actions

    def handle_disconnect(self, clid):
        return self.handle_disconnect_many({clid})

    def handle_ping(self, msg, clid):
        actions = []
        return actions

    def add_player(self, clid, cl_face=None):
        if cl_face is None:
            num_players = self.get_player_counts()
            min_num_players = min(num_players)
            best_slots = [i for i, num_face_players in enumerate(num_players) if num_face_players == min_num_players]
            # TODO: make sure this is random
            cl_face = CubeFace(random.SystemRandom().choice(best_slots))
            # cl_face = CubeFace(best_slots[0])
        self.game.players[cl_face.value] += [clid]
        self.game.player_face[clid] = cl_face
        return cl_face

    def add_spectator(self, clid, cl_face = None):
        if cl_face is None:
            cl_face = CubeFace(random.SystemRandom().randrange(len(CubeFace)))
        self.game.spectators[cl_face.value] += [clid]
        self.game.player_face[clid] = cl_face
        return cl_face

    def do_join(self, clid, spectate, is_god):
        actions = []

        cl_face = self.game.player_face.get(clid, None)
        if cl_face is None:
            if spectate:
                cl_face = self.add_spectator(clid)
            else:
                cl_face = self.add_player(clid)
        else:
            # keep player in the same face if spectator mode changes
            if spectate:
                self.game.players[cl_face.value] = [
                    cl for cl in self.game.players[cl_face.value]
                    if cl != clid
                ]
                if clid not in self.game.spectators[cl_face.value]:
                    cl_face = self.add_spectator(clid, cl_face)
            else:
                self.game.spectators[cl_face.value] = [
                    cl for cl in self.game.spectators[cl_face.value]
                    if cl != clid
                ]
                if clid not in self.game.players[cl_face.value]:
                    cl_face = self.add_player(clid, cl_face)

        if is_god:
            self.game.gods[clid] = 0

        # use disconnect algorithm to rebalance
        # this also sends a players message
        actions += self.handle_disconnect_many([])
        # we may still need to send a playerPos message
        actions += [self.make_update_player_pos_action(clid)]

        if self.game.is_running():
            # if game is already running, start game on client
            actions += self.game.make_join_update_state_actions(clid)

        return actions

    def handle_join(self, msg, clid):
        if not V.has_key(msg, 'spectate'):
            return
        spectate = msg['spectate']

        is_god = False
        if 'god' in msg and type(msg['god']) == str and msg['god'] == 'mmoderator' and spectate:
            is_god = True

        return self.do_join(clid, spectate, is_god)

    def update_pings(self, clid):
        # Warning: this should be kept in sync with
        # CLIENT_PING_TIMEOUT in puzzle.py
        PING_TIMEOUT = datetime.timedelta(seconds=15)
        curr_time = datetime.datetime.now()
        self.last_ping_times[clid] = curr_time
        dead_clients = {cl for cl, last_ping_time in self.last_ping_times.items() if curr_time > last_ping_time + PING_TIMEOUT}
        actions = []
        if len(dead_clients) > 0:
            actions += self.handle_disconnect_many(dead_clients)
        return actions

    def handle(self, msg, clid):
        actions = []

        msg_type = msg['type']
        handlers = {
            'join': self.handle_join,
            'ping': self.handle_ping,
        }
        if msg_type in handlers:
            actions += handlers[msg_type](msg, clid)
        actions += self.update_pings(clid)
        return actions
