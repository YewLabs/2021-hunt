from enum import Enum
import random
import datetime

from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.game_geom import *
from hunt.special_puzzles.ktane.players import *
from hunt.special_puzzles.ktane.ws_action import *
from hunt.special_puzzles.ktane.validate import Validator as V
from hunt.special_puzzles.ktane.modules.manual import *
from hunt.special_puzzles.ktane.modules.timer import *
from hunt.special_puzzles.ktane.modules.shake_it import *
from hunt.special_puzzles.ktane.modules.whos_on_first import *
from hunt.special_puzzles.ktane.modules.six import *
from hunt.special_puzzles.ktane.modules.wires import *
from hunt.special_puzzles.ktane.modules.maze import *
from hunt.special_puzzles.ktane.modules.simon import *
from hunt.special_puzzles.ktane.modules.gravity import *
from hunt.special_puzzles.ktane.modules.cube import *
from hunt.special_puzzles.ktane.modules.buttons import *
from hunt.special_puzzles.ktane.modules.passwords import *
from hunt.special_puzzles.ktane.modules.indicators import *

MAX_NUM_STRIKES = 3

def version_str_to_list(s):
    return [int(x) for x in s.split('.')]

class KtaneGamePhase(Enum):
    lobby = 0
    running = 1

class KtaneGame():
    def __init__(self):
        self.reset()
        # use this to communicate high scores to the upper layer
        self.win_time_left = None

    def reset(self):
        self.version = '0.0.24'
        self.phase = KtaneGamePhase.lobby
        # first player in self.players[f] is defuser,
        # the rest are spectators
        # self.spectators contains perma-spectators, i.e.
        # spectators in self.players may substitute disconnected defusers
        # but self.spectators will always be spectators
        # WARNING: player_face must be kept in sync with players/spectators
        self.players = [[] for i in range(len(CubeFace))]
        self.spectators = [[] for i in range(len(CubeFace))]
        self.player_face = {}

        # these overlap with spectators
        self.gods = {}

        self.module_slots = None
        self.last_strike = EventIndicator()

        # modules
        self.manual = ManualModule()
        self.timer = TimerModule()
        self.shake_it = ShakeItModule(self)
        self.whos_on_first_0 = WhosOnFirstModule(self, 0)
        self.whos_on_first_1 = WhosOnFirstModule(self, 1)
        self.six = SixModule(self)
        self.wires = WiresModule(self)
        self.maze = MazeModule(self)
        self.simon = SimonModule(self)
        self.gravity = GravityModule(self)
        self.cube = CubeModule(self)
        self.buttons = ButtonsModule(self)
        self.passwords = PasswordsModule(self)
        self.batteries = BatteriesModule(self)
        self.ports = PortsModule(self)
        self.serial = SerialNumberModule(self)
        self.date = DateOfManufactureModule(self)
        # WARNING: modules_by_name must be kept in sync with modules
        self.modules = [
            self.manual,
            self.timer,
            self.shake_it,
            self.whos_on_first_0,
            self.whos_on_first_1,
            self.six,
            self.wires,
            self.maze,
            self.simon,
            self.gravity,
            self.cube,
            self.buttons,
            self.passwords,
            self.batteries,
            self.ports,
            self.serial,
            self.date,
        ]
        self.modules_by_name = {
            module.name: module for module in self.modules
        }

        self.players_manager = KtanePlayersManager(self)
        # Warning: this transforms the players, not the cube
        self.view_matrix = Matrix3x3.make_identity()
        self.old_view_matrix = None
        self.rotate_txn = 0
        self.strike_reasons = []
        self.last_passive_update = EventIndicator()

        self.reset_temp_state()

    def reset_temp_state(self):
        self.need_update_rot = False
        self.need_update_module_slots = False
        self.face_updates = [[] for i in range(len(CubeFace))]
        self.need_stop = False
        self.out_of_time = False
        self.win = False
        self.god_reassign = None

    def invert_face_arr(self, arr):
        d = {}
        for face, face_el in enumerate(arr):
            for el in face_el:
                d[el] = CubeFace(face)
        return d

    def recompute_player_face(self):
        self.player_face = self.invert_face_arr(self.players)
        self.player_face.update(self.invert_face_arr(self.spectators))

    def from_dict(self, d):
        if version_str_to_list(d['version']) < version_str_to_list(self.version):
            return
        self.version = d['version']
        self.phase = KtaneGamePhase(d['phase'])
        self.players = d['players']
        self.spectators = d['spectators']
        self.gods = d['gods']
        self.recompute_player_face()
        self.module_slots = d['module_slots']
        if d['modules'] is not None:
            for module in self.modules:
                module.from_dict(d['modules'][module.name])
        self.players_manager.from_dict(d['players_manager'])
        self.view_matrix.from_dict(d['view_matrix'])
        self.last_strike.from_dict(d['last_strike'])
        self.rotate_txn = d['rotate_txn']
        self.strike_reasons = d['strike_reasons']
        self.last_passive_update.from_dict(d['last_passive_update'])

    def to_dict(self):
        return {
            'version': self.version,
            'phase': self.phase.value,
            'players': self.players,
            'spectators': self.spectators,
            'gods': self.gods,
            'module_slots': self.module_slots,
            'modules': {
                module.name: module.to_dict()
                for module in self.modules
            } if self.is_running() else None,
            'players_manager': self.players_manager.to_dict(),
            'view_matrix': self.view_matrix.to_dict(),
            'last_strike': self.last_strike.to_dict(),
            'rotate_txn': self.rotate_txn,
            'strike_reasons': self.strike_reasons,
            'last_passive_update': self.last_passive_update.to_dict(),
        }

    def is_running(self):
        return self.phase == KtaneGamePhase.running

    def check_gravity(self):
        if self.gravity.is_forbidden(self.view_matrix):
            self.timer.change_speed(self.gravity.TIMER_SPEEDUP)
        else:
            self.timer.change_speed(1)

    def make_update_state_actions_helper(self, clid, update_rot, update_module_slots, module_updates):
        actions = []
        msg = {
            'type': 'updateState',
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
        }
        need_update = False
        if update_rot:
            msg['viewMatrix'] = self.view_matrix.to_dict()
            msg['rotateTxn'] = self.rotate_txn
            need_update = True
        if update_module_slots:
            msg['moduleSlots'] = self.module_slots
            msg['debugSeed'] = self.manual.seed
            need_update = True
        if len(module_updates) > 0:
            msg['moduleUpdates'] = module_updates
            need_update = True
        if need_update:
            actions += [KtaneAction.make_send(msg, clid)]
        return actions

    def get_player_old_active_face(self, clid):
        player_slot = self.player_face[clid]
        face = KtaneGameGeom.player_face_to_face(
            self.old_view_matrix, CubeFace(player_slot)
        )
        return face

    def get_player_active_face(self, clid):
        player_slot = self.player_face[clid]
        face = KtaneGameGeom.player_face_to_face(
            self.view_matrix, CubeFace(player_slot)
        )
        return face

    def make_update_state_actions(self, clid):
        module_updates = []
        if self.old_view_matrix is not None:
            old_face = self.get_player_old_active_face(clid)
            module_updates += self.face_updates[old_face.value]
        face = self.get_player_active_face(clid)
        module_updates += self.face_updates[face.value]
        return self.make_update_state_actions_helper(
            clid, self.need_update_rot, self.need_update_module_slots,
            module_updates
        )

    def make_join_update_state_actions(self, clid):
        face = self.get_player_active_face(clid)
        module_updates = self.make_module_init_updates_for_face(face)
        return self.make_update_state_actions_helper(
            clid, True, True, module_updates
        )

    def make_all_update_state_actions(self, face_updates=None):
        actions = []
        for cl in self.players_manager.get_players():
            actions += self.make_update_state_actions(cl)
        return actions

    def make_all_stop_action(self):
        win_message = []
        time_left = self.timer.get_time_left() / datetime.timedelta(milliseconds=1)
        if self.win:
            win_message = [
                'You hear what one might describe as the sound',
                'of a xylophone as the screen flickers on. You',
                'did it! Your team fixed the console and can now',
                'play games together. You pick up a controller',
                'and invite your teammates to play a game with',
                'the newly-restored PANASONIC Q.',
            ]
            self.win_time_left = time_left
        return KtaneAction.make_send_many({
            'type': 'stop',
            'strikeReasons': self.strike_reasons,
            'timeLeft': time_left,
            'winMessage': win_message,
        }, self.players_manager.get_players())

    def add_face_updates(self, updates):
        for face, face_updates in updates.items():
            self.face_updates[face.value] += [face_updates]

    def make_module_init_updates_for_face(self, face):
        init_updates = []
        for module in self.modules:
            face_updates = module.make_full_updates()
            if face in face_updates:
                init_updates += [face_updates[face]]
        return init_updates

    def add_module_full_updates(self):
        for module in self.modules:
            self.add_face_updates(module.make_full_updates())

    def make_modules(self):
        self.manual.init()
        global_bomb_data = self.manual.global_info.gen_bomb_data()
        module_slots_data = global_bomb_data['modules']

        # slot 0: timer | shake | gravity | six
        # slot 1: buttons
        # slot 2: maze | simon
        # slot 3: talk | wires | cube | talk
        # slot 4: password
        # slot 5: serial number | date of manufacture | 2x batteries
        # slot 6: batteries/ports
        self.module_slots = [module_slots_data[CubeFace(i)] for i in range(len(CubeFace))]
        module_faces = {}
        for face, face_modules in enumerate(self.module_slots):
            for module in face_modules:
                module_faces[module] = CubeFace(face)

        self.timer.init(module_faces['timer'])
        self.shake_it.init(module_faces['shakeit'])
        self.whos_on_first_0.init(module_faces['whosonfirst0'])
        self.whos_on_first_1.init(module_faces['whosonfirst1'])
        self.six.init(module_faces['six'])
        self.wires.init(module_faces['wires'])
        self.maze.init(module_faces['maze-0'], module_faces['maze-1'])
        self.simon.init(module_faces['simon-0'], module_faces['simon-1'])
        self.gravity.init(module_faces['gravity'])
        self.cube.init(module_faces['cube'])
        self.buttons.init([module_faces['buttons-0'], module_faces['buttons-1'], module_faces['buttons-2'], module_faces['buttons-3']])
        self.passwords.init([module_faces['passwords-0'], module_faces['passwords-1'], module_faces['passwords-2'], module_faces['passwords-3']])
        self.serial.init(module_faces['serial'])
        self.date.init(module_faces['date'])
        self.batteries.init([module_faces['batteries-0'], module_faces['batteries-1'], module_faces['batteries-2']])
        self.ports.init([module_faces['ports-0'], module_faces['ports-1'], module_faces['ports-2']])
        self.check_gravity()
        self.add_module_full_updates()

    def start_game(self):
        self.phase = KtaneGamePhase.running
        self.make_modules()

    def stop_game(self):
        actions = []
        actions += [self.make_all_stop_action()]
        self.reset()
        return actions

    # modules should set an internal flag when a user make a strike
    # and override is_strike and do_strike to get detected here
    def update_passive_state(self):
        time_left = self.timer.get_time_left()
        if time_left < datetime.timedelta():
            self.out_of_time = True
            self.need_stop = True
            return

        strike_happened = False
        for module in self.modules:
            if module.is_strike():
                self.strike_reasons += [module.name]
                # no need to do individual state updates since we
                # get all updates form the rotate
                module.do_strike()
                self.timer.register_strike()
                strike_happened = True
                self.last_strike.trigger()

        # randomly rotate on strike, but don't queue another
        # rotation if a rotation is already happening
        if strike_happened and not self.need_update_rot:
            self.do_rotate(CubeFace(random.SystemRandom().randrange(len(CubeFace))))

        # put this after the rotation so that all clients
        # are notified of the strike
        if self.timer.is_explode():
            self.need_stop = True
            return

        if all([module.is_disarmed() for module in self.modules]):
            self.win = True
            self.need_stop = True
            return

        time_since = self.last_passive_update.get_time_since()
        # only send passive updates every 1s
        if time_since is None or time_since >= datetime.timedelta(seconds=1):
            for module in self.modules:
                self.add_face_updates(module.make_periodic_updates())
            self.last_passive_update.trigger()

    def handle_start(self, msg, clid):
        if self.phase != KtaneGamePhase.lobby:
            return
        self.start_game()
        self.need_update_rot = True
        self.need_update_module_slots = True

    def handle_stop(self, msg, clid):
        self.need_stop = True

    def do_rotate(self, rot_face):
        self.old_view_matrix = self.view_matrix
        self.view_matrix = KtaneGameGeom.rot_by_face(self.view_matrix, rot_face)
        self.need_update_rot = True
        for module in self.modules:
            module.handle_rotate(self.view_matrix, rot_face)
        self.check_gravity()
        self.add_module_full_updates()
        self.rotate_txn += 1

    def handle_rotate(self, msg, clid):
        if not V.has_key(msg, 'rotateTxn') or not V.has_key(msg, 'rotDir'):
            return
        client_rotate_txn = msg['rotateTxn']
        rot_dir = msg['rotDir']
        if not V.is_nat(rot_dir, len(CardinalDirection)):
            return

        if not self.is_running():
            return

        if client_rotate_txn < self.rotate_txn:
            return

        rot_dir = CardinalDirection(rot_dir)
        rot_face = KtaneGameGeom.player_dir_to_rot_face(self.view_matrix, self.player_face[clid], rot_dir)

        if clid in self.gods:
            new_view_matrix = KtaneGameGeom.rot_by_face(self.view_matrix, rot_face)
            new_rel_vec = new_view_matrix.mult_vec(self.player_face[clid].get_vec())
            new_vec = self.view_matrix.get_transpose().mult_vec(new_rel_vec)
            new_face = CubeFace.from_vec(new_vec)
            self.god_reassign = new_face
            return

        self.do_rotate(rot_face)

    def handle_module_input(self, msg, clid):
        if not V.has_key(msg, 'rotateTxn') or not V.has_key(msg, 'module'):
            return
        client_rotate_txn = msg['rotateTxn']
        full_name = msg['module']

        if not self.is_running():
            return

        if client_rotate_txn < self.rotate_txn:
            return

        if not self.players_manager.is_defuser(clid):
            return
        active_face = self.get_player_active_face(clid)
        if full_name not in self.module_slots[active_face.value]:
            return

        name_parts = full_name.split('-')
        submodule = None
        if len(name_parts) > 1:
            if not V.is_nat_str(name_parts[1]):
                return
            submodule = int(name_parts[1])
        if not V.has_key(self.modules_by_name, name_parts[0]):
            return
        module = self.modules_by_name[name_parts[0]]

        face_updates = module.handle_input(msg, submodule)
        if face_updates is None:
            print('BUG: handle_input returns None')
            return
        self.add_face_updates(face_updates)

    def handle_disconnect(self, clid):
        return self.players_manager.handle_disconnect(clid)

    def handle(self, msg, clid):
        if not V.is_dict(msg) or not V.has_key(msg, 'type'):
            return []
        msg_type = msg['type']
        # for debug server
        if msg_type == 'AUTH':
            return []

        actions = []

        if clid in self.player_face:
            handlers = {
                'start': self.handle_start,
                'stop': self.handle_stop,
                'clearState': self.handle_stop,
                'rotate': self.handle_rotate,
                'moduleInput': self.handle_module_input,
            }
            if msg_type in handlers:
                handlers[msg_type](msg, clid)
        if self.is_running():
            self.update_passive_state()

        actions += self.make_all_update_state_actions()
        actions += self.players_manager.handle(msg, clid)

        if self.god_reassign is not None:
            old_face = self.player_face[clid]
            self.spectators[old_face.value] = [
                cl for cl in self.spectators[old_face.value]
                if cl != clid
            ]
            self.player_face[clid] = self.god_reassign
            # use the join algorithm to force
            # god spectator into new face
            actions += self.players_manager.do_join(clid, True, True)

        if self.need_stop:
            actions += self.stop_game()
        elif clid in self.player_face:
            if all([clid not in action.targets for action in actions]):
                actions += [KtaneAction.make_send({
                    'type': 'pong',
                }, clid)]
        else:
            actions += [KtaneAction.make_send({
                'type': 'stop',
            }, clid)]

        return actions
