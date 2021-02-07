import random
import datetime
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.game_geom import *
from hunt.special_puzzles.ktane.modules.module_base import *

class CubeModule(ModuleBase):
    name = 'cube'

    def __init__(self, game):
        self.game = game
        self.face = None
        self.last_strike = EventIndicator()
        self.text = None
        self.input_index = 0
        self.start_face = None
        self.answer = []

        self.strike = False

    def pull_config(self):
        bomb_data = self.game.manual.cube_info.gen_bomb_data()
        self.text = bomb_data['text']
        self.answer = bomb_data['turns']

    def init(self, face):
        self.face = face
        self.pull_config()

    def from_dict(self, d):
        self.face = CubeFace(d['face'])
        self.last_strike.from_dict(d['last_strike'])
        self.input_index = d['input_index']
        if d['start_face'] is not None:
            self.start_face = CubeFace(d['start_face'])
        self.pull_config()

    def to_dict(self):
        return {
            'face': self.face.value,
            'last_strike': self.last_strike.to_dict(),
            'input_index': self.input_index,
            'start_face': None if self.start_face is None else self.start_face.value,
        }

    def is_disarmed(self):
        return self.input_index >= len(self.answer)

    def to_client_state(self):
        return {
            'module': self.name,
            'disarmed': self.is_disarmed(),
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
            'started': self.start_face is not None,
            'text': self.text,
        }

    def make_updates(self):
        return {
            self.face: self.to_client_state()
        }

    def handle_rotate(self, view_matrix, rot_face):
        if self.is_disarmed():
            return {}
        if self.start_face is None:
            return {}
        rel_view_matrix = KtaneGameGeom.get_player_view_matrix(self.game.view_matrix, self.start_face)
        rel_rot_face = CubeFace.from_vec(rel_view_matrix.get_transpose().mult_vec(rot_face.get_vec()))
        if rel_rot_face.get_opposite() == self.answer[self.input_index]:
            self.input_index += 1
        else:
            self.strike = True
        return {}

    def handle_input(self, msg, submodule=None):
        if self.is_disarmed():
            return {}
        cube_vec = self.face.get_vec()
        player_vec = self.game.view_matrix.get_transpose().mult_vec(cube_vec)
        self.start_face = CubeFace.from_vec(player_vec)
        self.input_index = 0
        return self.make_updates()

    def is_strike(self):
        return self.strike

    def do_strike(self):
        self.last_strike.trigger()
        self.input_index = 0
        self.start_face = None
        return

    def make_full_updates(self):
        return self.make_updates()


