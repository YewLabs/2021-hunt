import random
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.modules.module_base import *
from hunt.special_puzzles.ktane.validate import Validator as V

class SimonModule(ModuleBase):
    name = 'simon'

    def __init__(self, game):
        self.game = game

        self.display_face = None
        self.control_face = None
        self.last_strike = EventIndicator()
        self.answers = []
        self.round_num = 0
        self.input_index = 0
        # fake to make the controls look like the maze
        self.txn = 0

        self.strike = False

    def pull_config(self):
        self.answers = self.game.manual.simon_info.gen_bomb_data()['lights']

    def init(self, control_face, display_face):
        self.control_face = control_face
        self.display_face = display_face
        self.pull_config()

    def from_dict(self, d):
        self.control_face = CubeFace(d['control_face'])
        self.display_face = CubeFace(d['display_face'])
        self.last_strike.from_dict(d['last_strike'])
        self.round_num = d['round_num']
        self.input_index = d['input_index']
        self.pull_config()

    def to_dict(self):
        return {
            'control_face': self.control_face.value,
            'display_face': self.display_face.value,
            'last_strike': self.last_strike.to_dict(),
            'round_num': self.round_num,
            'input_index': self.input_index,
        }

    def get_submodule_index(self, is_control):
        return 0 if is_control else 1

    def get_name(self, is_control):
        return self.name + '-' + str(self.get_submodule_index(is_control))

    def handle_rotate(self, view_matrix, rot_face):
        self.input_index = 0
        return {}

    def is_disarmed(self):
        return self.round_num == len(self.answers)

    def to_client_control_state(self):
        return {
            'module': self.name,
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
            'disarmed': self.is_disarmed(),
            'txn': self.txn,
        }

    def to_client_display_state(self):
        if self.is_disarmed():
            answer_as_ints = None
        else:
            answer_as_ints = [d.value for d in self.answers[self.round_num]]
        return {
            'module': self.name,
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
            'disarmed': self.is_disarmed(),
            'roundNum': self.round_num,
            'seq': answer_as_ints
        }

    def make_updates(self):
        return {
            self.control_face: self.to_client_control_state(),
            self.display_face: self.to_client_display_state(),
        }

    # unit 0 is control, unit 1 is display
    def is_control(self, submodule):
        return submodule == 0

    def handle_input(self, msg, submodule=None):
        if not V.has_key(msg, 'txn') and V.has_key(msg, 'direction'):
            return {}
        client_txn = msg['txn']
        direction = msg['direction']
        if not V.is_nat(client_txn) or not V.is_nat(direction, len(CardinalDirection)):
            return {}

        if self.is_disarmed():
            return {}
        if self.is_control(submodule):
            self.txn = client_txn
            direction = CardinalDirection(direction)
            if direction != self.answers[self.round_num][self.input_index]:
                self.strike = True
            else:
                self.input_index += 1
                if self.input_index == len(self.answers[self.round_num]):
                    self.input_index = 0
                    self.round_num += 1
        return self.make_updates()

    def is_strike(self):
        return self.strike

    def do_strike(self):
        self.last_strike.trigger()
        self.input_index = 0
        return

    def make_full_updates(self):
        return self.make_updates()

