import json
import random
import datetime
import os.path
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.modules.module_base import *
from hunt.special_puzzles.ktane.manual.gen import *
from hunt.special_puzzles.ktane.validate import Validator as V

MANUAL_GEN_DATA_PATH = '../manual/data.json'

# singleton
class ManualGenData:
    data = None

    @staticmethod
    def get_data():
        if ManualGenData.data is None:
            full_path = os.path.join(os.path.dirname(__file__), MANUAL_GEN_DATA_PATH)
            with open(full_path, 'r') as f:
                ManualGenData.data = json.loads(f.read())
        return ManualGenData.data

MANUAL_GEN_FUNCTIONS = {
    'global': gen_global_manual_data,
    'intro': gen_empty,
    'timer': gen_empty,
    'gravity': gen_gravity,
    'six': gen_six,
    'talk': gen_talk,
    'wires': gen_wires,
    'buttons': gen_buttons,
    'passwords': gen_passwords,
    'simon': gen_empty,
    'maze': gen_empty,
    'cube': gen_empty,
    'shake': gen_shake,
    'directions': gen_empty,
}

BOMB_GEN_FUNCTIONS = {
    'global': gen_global_bomb_data,
    'intro': None,
    'timer': None,
    'gravity': gen_bomb_gravity,
    'six': gen_bomb_six,
    'talk': gen_bomb_talk,
    'wires': gen_bomb_wires,
    'buttons': gen_bomb_buttons,
    'passwords': gen_bomb_passwords,
    'simon': gen_bomb_simon,
    'maze': None,
    'cube': gen_bomb_cube,
    'shake': None,
    'directions': None,
}

# TODO: make these false
NONRANDOM_SEED = False

class ManualInfo:
    def __init__(self, name):
        self.manual_seed = None
        self.bomb_seed = None
        self.name = name
        self.generate_manual_data = MANUAL_GEN_FUNCTIONS[name]
        self.generate_bomb_data = BOMB_GEN_FUNCTIONS[name]
        self.manual_data = None
        self.bomb_data = None

        # set these before calling gen data if necessary
        self.global_manual_data = None
        self.global_bomb_data = None

    def init(self, manual_seed, bomb_seed):
        self.manual_seed = manual_seed
        self.bomb_seed = bomb_seed

    def to_client_state(self):
        return self.gen_manual_data()

    def gen_manual_data(self):
        if self.manual_data is None:
            gen_data = ManualGenData.get_data()
            self.manual_data = {
                'module': self.name,
                self.name: self.generate_manual_data(gen_data, self.manual_seed, self.global_manual_data)
            }
        return self.manual_data

    def gen_bomb_data(self):
        if self.bomb_data is None:
            gen_data = ManualGenData.get_data()
            manual_data = self.gen_manual_data()
            self.bomb_data = self.generate_bomb_data(gen_data, manual_data, self.bomb_seed, self.global_bomb_data)
        return self.bomb_data

class ManualModule(ModuleBase):
    name = 'manual'

    def __init__(self):
        self.section_nums = [0, 0]
        self.page_nums = [0, 0]

        self.global_info = ManualInfo('global')
        self.intro_info = ManualInfo('intro')
        self.timer_info = ManualInfo('timer')
        self.gravity_info = ManualInfo('gravity')
        self.six_info = ManualInfo('six')
        self.whos_on_first_info = ManualInfo('talk')
        self.wires_info = ManualInfo('wires')
        self.buttons_info = ManualInfo('buttons')
        self.passwords_info = ManualInfo('passwords')
        self.simon_info = ManualInfo('simon')
        self.maze_info = ManualInfo('maze')
        self.cube_info = ManualInfo('cube')
        self.shake_it_info = ManualInfo('shake')
        self.directions_info = ManualInfo('directions')

        # grouped by sections
        self.manual_infos = [
            [
                self.intro_info,
                self.timer_info,
            ],
            [
                self.gravity_info
            ],
            [
                self.shake_it_info
            ],
            [
                self.six_info
            ],
            [
                self.whos_on_first_info
            ],
            [
                self.wires_info
            ],
            [
                self.buttons_info
            ],
            [
                self.passwords_info
            ],
            [
                self.cube_info
            ],
            [
                self.directions_info,
                self.simon_info,
                self.maze_info,
            ],
        ]

        self.global_manual_data = None
        self.global_bomb_data = None
        self.seed = None
        self.maze_seed = None

    def gen_global_data(self):
        self.global_manual_data = self.global_info.gen_manual_data()['global']
        self.global_bomb_data = self.global_info.gen_bomb_data()

        for section_infos in self.manual_infos:
            for manual_info in section_infos:
                manual_info.global_manual_data = self.global_manual_data
                manual_info.global_bomb_data = self.global_bomb_data

    def init(self):
        seed = 556493047 if NONRANDOM_SEED else random.SystemRandom().randrange(1<<30)
        # print('seed: ' + str(seed))
        self.seed = seed
        self.init_manual_infos()

    def init_manual_infos(self):
        r = Random(self.seed)
        self.global_info.init(r.randrange(1<<30), r.randrange(1<<30))
        for section_infos in self.manual_infos:
            for info in section_infos:
                info.init(r.randrange(1<<30), r.randrange(1<<30))
        self.maze_seed = r.randrange(1<<30)
        self.gen_global_data()

    def from_dict(self, d):
        self.seed = d['seed']
        self.init_manual_infos()

        self.section_nums = d['section_nums']
        self.page_nums = d['page_nums']

    def to_dict(self):
        return {
            'seed': self.seed,
            'section_nums': self.section_nums,
            'page_nums': self.page_nums,
        }

    def get_submodule_index(self, is_top):
        return 1 if is_top else 0

    def submodule_to_cube_face(self, submodule):
        return CubeFace.top if (submodule == 1) else CubeFace.bottom

    def get_name(self, is_top):
        return self.name + '-' + str(self.get_submodule_index(is_top))

    def to_client_state(self, is_top, send_page_num=True):
        submodule_index = self.get_submodule_index(is_top)
        opposite = 1 - submodule_index
        section_num = self.section_nums[submodule_index]
        infos = self.manual_infos[section_num]

        client_state = {
            'module': self.name,
            'selectedSectionNum': self.section_nums[opposite],
            'sectionNum': section_num,
            'infos': [info.to_client_state() for info in infos],
        }
        if send_page_num:
            page_num = self.page_nums[submodule_index]
            client_state['pageNum'] = page_num
        return client_state

    def make_updates(self):
        return {
            CubeFace.top: self.to_client_state(True),
            CubeFace.bottom: self.to_client_state(False),
        }

    def make_full_updates(self):
        return self.make_updates()

    def handle_input(self, msg, submodule):
        if 'sectionNum' in msg:
            new_section_num = msg['sectionNum']
            if not V.is_nat(new_section_num, len(self.manual_infos)):
                return {}

            opposite = 1 - submodule
            if self.section_nums[opposite] == new_section_num:
                return {}

            self.section_nums[opposite] = new_section_num
            self.page_nums[opposite] = 0

            face = self.submodule_to_cube_face(submodule)
            opposite_face = self.submodule_to_cube_face(opposite)
            opposite_is_top = opposite_face == CubeFace.top
            return {
                face: self.to_client_state(face == CubeFace.top, False),
                opposite_face: self.to_client_state(opposite_is_top, False),
            }

        if 'pageNum' in msg:
            new_page_num = msg['pageNum']
            if not V.is_nat(new_page_num):
                return {}
            self.page_nums[submodule] = new_page_num
            face = self.submodule_to_cube_face(submodule)
            return {
                face: self.to_client_state(face == CubeFace.top, True),
            }
        return {}
