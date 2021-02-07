import random
import datetime
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.game_geom import *
from hunt.special_puzzles.ktane.modules.module_base import *

class SixModule(ModuleBase):
    name = 'six'

    def __init__(self, game):
        self.game = game
        self.face = None
        self.lit = 0 # bitmask

        self.perm = []

    def pull_config(self):
        bomb_data = self.game.manual.six_info.gen_bomb_data()
        directions_map = {
            'C': CubeFace.top,
            'G': CubeFace.bottom,
            'N': CubeFace.back,
            'E': CubeFace.right,
            'S': CubeFace.front,
            'W': CubeFace.left,
        }
        self.perm = [KtaneGameGeom.char_to_cube_face(c).value for c in bomb_data['direction']]
        self.lit = bomb_data['init']

    def init(self, face):
        self.face = face
        self.lit = 0
        self.pull_config()

    def from_dict(self, d):
        self.face = CubeFace(d['face'])
        self.pull_config()
        self.lit = d['lit']

    def to_dict(self):
        return {
            'face': self.face.value,
            'lit': self.lit,
        }

    def is_disarmed(self):
        return self.lit == ((1 << len(CubeFace)) - 1)

    def get_lit(self, index):
        return ((self.lit >> index) & 1) == 1

    def toggle_lit(self, index):
        self.lit ^= 1 << index

    def to_client_state(self):
        lit_perm = 0
        for i in range(len(CubeFace)):
            if self.get_lit(self.perm[i]):
                lit_perm |= 1 << i
        return {
            'module': self.name,
            'lit': lit_perm,
        }

    def make_updates(self):
        return {
            self.face: self.to_client_state()
        }

    def handle_rotate(self, view_matrix, rot_face):
        if self.is_disarmed():
            return {}
        if rot_face == self.face or rot_face == self.face.get_opposite():
            # don't toggle if still facing the same side
            return {}
        orient_vec = view_matrix.get_transpose().mult_vec(self.face.get_vec())
        orient = CubeFace.from_vec(orient_vec)
        self.toggle_lit(orient.value)
        return {}

    def make_full_updates(self):
        return self.make_updates()
