from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.modules.module_base import *
from hunt.special_puzzles.ktane.validate import Validator as V

NUM_ROUNDS = 1

class WhosOnFirstModule(ModuleBase):
    name_prefix = 'whosonfirst'

    def __init__(self, game, index):
        self.game = game
        self.index = index
        self.name = self.name_prefix + str(index)

        self.face = None
        self.round_num = 0
        self.last_strike = EventIndicator()
        self.button_order = []
        self.answer = []
        self.text = ''
        self.input_index = 0

        self.strike = False

    def pull_config(self):
        bomb_data = self.game.manual.whos_on_first_info.gen_bomb_data()[self.index]
        self.text = bomb_data['prompt']
        self.answer = bomb_data['answer']
        self.button_order = bomb_data['button_order']

    def init(self, face):
        self.face = face
        self.pull_config()

    def from_dict(self, d):
        self.face = CubeFace(d['face'])
        self.round_num = d['round_num']
        self.last_strike.from_dict(d['last_strike'])
        self.input_index = d['input_index']
        self.pull_config()

    def to_dict(self):
        return {
            'face': self.face.value,
            'round_num': self.round_num,
            'last_strike': self.last_strike.to_dict(),
            'input_index': self.input_index,
        }

    def to_client_state(self):
        return {
            'module': self.name,
            'text': self.text,
            'roundNum': self.round_num,
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
            'buttonOrder': self.button_order,
            'disarmed': self.is_disarmed(),
            'prevInputs': self.answer[:self.input_index],
        }

    def is_disarmed(self):
        return self.round_num >= NUM_ROUNDS

    def handle_input(self, msg, submodule=None):
        if not V.has_key(msg, 'press'):
            return {}
        press = msg['press']
        if not V.is_nat(press):
            return {}

        if self.is_disarmed():
            return {}
        if press != self.answer[self.input_index]:
            self.strike = True
            return {}
        self.input_index += 1
        if self.input_index >= len(self.answer):
            self.round_num += 1
            self.input_index = 0
        return self.make_updates()

    def make_updates(self):
        return {
            self.face: self.to_client_state()
        }

    def is_strike(self):
        return self.strike

    def do_strike(self):
        self.last_strike.trigger()
        self.input_index = 0
        return

    def make_full_updates(self):
        return self.make_updates()
