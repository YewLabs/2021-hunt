import datetime
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.game_geom import *
from hunt.special_puzzles.ktane.modules.module_base import *
from hunt.special_puzzles.ktane.validate import Validator as V

NUM_WIRES = 5

class WiresModule(ModuleBase):
    name = 'wires'

    def __init__(self, game):
        self.game = game
        self.face = None
        self.last_strike = EventIndicator()
        self.colors = [0] * NUM_WIRES
        self.cuts = 0 # bitmask
        self.striped = 0 # bitmask
        self.allowed_sides = []

        self.strike = False

    def pull_config(self):
        bomb_data = self.game.manual.wires_info.gen_bomb_data()
        self.colors = bomb_data['colors']
        self.striped = bomb_data['striped']
        self.allowed_sides = [
            [KtaneGameGeom.char_to_cube_face(c) for c in wire_allowed_sides]
            for wire_allowed_sides in bomb_data['allowed_sides']
        ]

    def init(self, face):
        self.face = face
        self.pull_config()

    def from_dict(self, d):
        self.face = CubeFace(d['face'])
        self.last_strike.from_dict(d['last_strike'])
        self.cuts = d['cuts']
        self.pull_config()

    def to_dict(self):
        return {
            'face': self.face.value,
            'last_strike': self.last_strike.to_dict(),
            'cuts': self.cuts,
        }

    def to_client_state(self):
        return {
            'module': self.name,
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
            'colors': self.colors,
            'striped': self.striped,
            'cuts': self.cuts,
        }

    def is_disarmed(self):
        return self.cuts == ((1 << NUM_WIRES) - 1);

    def set_cut(self, cut):
        self.cuts |= 1 << cut

    def handle_input(self, msg, submodule=None):
        if not V.has_key(msg, 'cut'):
            return {}
        cut = msg['cut']
        if not V.is_nat(cut, NUM_WIRES):
            return {}

        if self.is_disarmed():
            return {}
        direction = CubeFace.from_vec(self.game.view_matrix.get_transpose().mult_vec(self.face.get_vec()))
        self.set_cut(cut)
        if direction not in self.allowed_sides[cut]:
            # allow the cut but strike
            self.strike = True
            return {}
        return self.make_updates()

    def is_strike(self):
        return self.strike

    def do_strike(self):
        self.last_strike.trigger()
        return

    def make_updates(self):
        return {
            self.face: self.to_client_state()
        }

    def make_full_updates(self):
        return self.make_updates()
