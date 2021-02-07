import random
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.modules.module_base import *


class SerialNumberModule(ModuleBase):
    name = 'serial'

    def __init__(self, game):
        self.game = game
        self.face = None
        self.text = None

    def pull_config(self):
        bomb_data = self.game.manual.global_info.gen_bomb_data()
        self.text = bomb_data['serial']

    def init(self, face):
        self.face = face
        self.pull_config()

    def from_dict(self, d):
        self.face = CubeFace(d['face'])
        self.pull_config()

    def to_dict(self):
        return {
            'face': self.face.value
        }

    def to_client_state(self):
        return {
            'module': self.name,
            'text': self.text
        }

    def make_updates(self):
        return {
            self.face: self.to_client_state()
        }

    def make_full_updates(self):
        return self.make_updates()


class DateOfManufactureModule(ModuleBase):
    name = 'date'

    def __init__(self, game):
        self.game = game
        self.face = None
        self.text = None

    def pull_config(self):
        bomb_data = self.game.manual.global_info.gen_bomb_data()
        self.text = bomb_data['date']

    def init(self, face):
        self.face = face
        self.pull_config()

    def from_dict(self, d):
        self.face = CubeFace(d['face'])
        self.pull_config()

    def to_dict(self):
        return {
            'face': self.face.value
        }

    def to_client_state(self):
        return {
            'module': self.name,
            'text': self.text
        }

    def make_updates(self):
        return {
            self.face: self.to_client_state()
        }

    def make_full_updates(self):
        return self.make_updates()


class BatteriesModule(ModuleBase):
    name = 'batteries'

    def __init__(self, game):
        self.game = game
        self.faces = None

    def pull_config(self):
        bomb_data = self.game.manual.global_info.gen_bomb_data()
        self.num_per_face = bomb_data['batteries_modules']

    def init(self, faces):
        self.faces = faces
        self.pull_config()

    def from_dict(self, d):
        self.faces = [CubeFace(f) for f in d['faces']]
        self.pull_config()

    def to_dict(self):
        return {
            'faces': [f.value for f in self.faces],
        }

    def get_name(self, index):
        return self.name + '-' + str(index)

    def to_client_state(self):
        return {
            'module': self.name,
            'numPerFace': self.num_per_face
        }

    def make_updates(self):
        return {
            f: self.to_client_state()
            for f in self.faces
        }

    def make_full_updates(self):
        return self.make_updates()


class PortsModule(ModuleBase):
    name = 'ports'

    def __init__(self, game):
        self.game = game
        self.faces = None

    def pull_config(self):
        bomb_data = self.game.manual.global_info.gen_bomb_data()
        self.num_per_face = bomb_data['ports_modules']

    def init(self, faces):
        self.faces = faces
        self.pull_config()

    def from_dict(self, d):
        self.faces = [CubeFace(f) for f in d['faces']]
        self.pull_config()

    def to_dict(self):
        return {
            'faces': [f.value for f in self.faces],
        }

    def get_name(self, index):
        return self.name + '-' + str(index)

    def to_client_state(self):
        return {
            'module': self.name,
            'numPerFace': self.num_per_face
        }

    def make_updates(self):
        return {
            f: self.to_client_state()
            for f in self.faces
        }

    def make_full_updates(self):
        return self.make_updates()
