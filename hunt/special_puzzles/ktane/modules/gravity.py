import random
import datetime
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.game_geom import *
from hunt.special_puzzles.ktane.modules.module_base import *

class GravityModule(ModuleBase):
    name = 'gravity'

    # note that this check is done externally
    TIMER_SPEEDUP = 2

    def __init__(self, game):
        self.game = game
        self.face = None
        self.forbidden_dir = None
        self.text = None

    def pull_config(self):
        bomb_data = self.game.manual.gravity_info.gen_bomb_data()
        self.forbidden_dir = KtaneGameGeom.char_to_cube_face(bomb_data['direction'])
        self.text = bomb_data['text']

    def init(self, face):
        self.face = face
        self.pull_config()

    def from_dict(self, d):
        self.face = CubeFace(d['face'])
        self.pull_config()

    def to_dict(self):
        return {
            'face': self.face.value,
        }

    def to_client_state(self):
        return {
            'module': self.name,
            'text': self.text,
        }

    def make_updates(self):
        return {
            self.face: self.to_client_state()
        }

    def is_forbidden(self, view_matrix):
        return CubeFace.from_vec(view_matrix.mult_vec(self.forbidden_dir.get_vec())) == self.face

    def make_full_updates(self):
        return self.make_updates()

