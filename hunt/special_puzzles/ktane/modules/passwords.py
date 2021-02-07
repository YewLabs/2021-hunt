import random
import enum
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.modules.module_base import *
from hunt.special_puzzles.ktane.validate import Validator as V

class PasswordsModule(ModuleBase):
    name = 'passwords'

    def __init__(self, game):
        self.game = game

        self.faces = []
        self.selected = []
        self.letters = []
        self.answer = None

    def pull_config(self):
        bomb_data = self.game.manual.passwords_info.gen_bomb_data()
        self.letters = [
            bomb_data['letters'][f]
            for f in self.faces
        ]
        self.answer = ''.join([
            bomb_data['answer'][f]
            for f in self.faces
        ])

    def init(self, faces):
        self.faces = faces
        self.pull_config()
        self.selected = [0]*len(self.letters)

    def from_dict(self, d):
        self.faces = [CubeFace(f) for f in d['faces']]
        self.selected = d['selected']
        self.pull_config()

    def to_dict(self):
        return {
            'faces': [f.value for f in self.faces],
            'selected': self.selected,
        }

    def to_client_state(self, submodule):
        return {
            'module': self.name,
            'disarmed': self.is_disarmed(),
            'letters': self.letters[submodule],
            'selected': self.selected[submodule],
        }

    def is_disarmed(self):
        selected_word = ''.join([
            sub_letters[index]
            for sub_letters, index in
            zip(self.letters, self.selected)
        ])
        return selected_word == self.answer

    def handle_input(self, msg, submodule=None):
        if not V.is_nat(submodule, len(self.faces)):
            return {}
        if not V.has_key(msg, 'selection'):
            return {}
        selection = msg['selection']
        if not V.is_nat(selection, len(self.letters[submodule])):
            return {}

        if self.is_disarmed():
            return {}
        self.selected[submodule] = selection
        return self.make_updates()

    def make_updates(self):
        return {
            f: self.to_client_state(i) for i, f in enumerate(self.faces)
        };

    def make_full_updates(self):
        return self.make_updates()
