import enum
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.modules.module_base import *
from hunt.special_puzzles.ktane.validate import Validator as V

class ButtonsTask(enum.Enum):
    sequential = 0
    simultaneous = 1

class ButtonsModule(ModuleBase):
    name = 'buttons'

    def __init__(self, game):
        self.game = game

        self.last_strike = EventIndicator()
        self.faces = []
        self.task_type = None
        self.button_texts = []
        self.answer = []
        self.depressed = [] # list of depressed buttons

        self.strike = False

    def pull_config(self):
        bomb_data = self.game.manual.buttons_info.gen_bomb_data()
        self.task_type = {
            'sequential': ButtonsTask.sequential,
            'simultaneous': ButtonsTask.simultaneous,
        }[bomb_data['type_']]
        self.button_texts = [
            bomb_data['labels'][f]
            for f in self.faces
        ]
        self.answer = bomb_data['answer']

    def init(self, faces):
        self.faces = faces
        self.depressed = []
        self.pull_config()

    def from_dict(self, d):
        self.faces = [CubeFace(f) for f in d['faces']]
        self.last_strike.from_dict(d['last_strike'])
        self.depressed = d['depressed']
        self.pull_config()

    def to_dict(self):
        return {
            'faces': [f.value for f in self.faces],
            'last_strike': self.last_strike.to_dict(),
            'depressed': self.depressed,
        }

    def to_client_state(self, submodule):
        buttons = self.button_texts[submodule]
        return {
            'module': self.name,
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
            'disarmed': self.is_disarmed(),
            'buttonTexts': buttons,
            'depressed': [b for b in self.depressed if b in buttons],
        }

    def is_disarmed(self):
        return len(self.depressed) == len(self.answer)

    def handle_rotate(self, view_matrix, rot_face):
        if self.is_disarmed():
            return {}
        if self.task_type == ButtonsTask.simultaneous:
            self.depressed = []
        return {}

    def handle_input(self, msg, submodule=None):
        if not V.is_nat(submodule, len(self.faces)):
            return {}
        if not V.has_key(msg, 'button') or not V.has_key(msg, 'isDown'):
            return {}
        button = msg['button']
        is_down = msg['isDown']
        if not V.is_str(button) or not V.is_bool(is_down):
            return {}

        if self.is_disarmed():
            return {}

        if not is_down:
            if self.task_type == ButtonsTask.simultaneous:
                self.depressed = [b for b in self.depressed if b != button]
                return self.make_updates()
            else:
                return {}

        if button in self.depressed:
            return {}

        if self.task_type == ButtonsTask.sequential:
            if button != self.answer[len(self.depressed)]:
                self.strike = True
                return {}
        else:
            if button not in self.answer:
                self.strike = True
                return {}
        self.depressed += [button]
        return self.make_updates()

    def make_updates(self):
        return {
            f: self.to_client_state(i) for i, f in enumerate(self.faces)
        };

    def is_strike(self):
        return self.strike

    def do_strike(self):
        self.last_strike.trigger()
        self.input_index = 0

    def make_full_updates(self):
        return self.make_updates()

