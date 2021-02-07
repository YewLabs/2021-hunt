import random
import datetime
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.modules.module_base import *

ROTATIONS_NEEDED = 5

class ShakeItModule(ModuleBase):
    name = 'shakeit'

    def __init__(self, game):
        self.game = game
        self.face = None
        self.last_reset = EventIndicator()
        self.num_rots = 0
        self.last_strike = EventIndicator()

        self.shake_lb = None
        self.shake_ub = None
        self.reset_lb = None
        self.reset_ub = None

    def pull_config(self):
        manual_data = self.game.manual.shake_it_info.gen_manual_data()['shake']
        self.shake_lb = manual_data['X']
        self.shake_ub = manual_data['Y']
        self.reset_lb = 0
        self.reset_ub = manual_data['Z']
        # self.shake_lb = 30
        # self.shake_ub = 90
        # self.reset_lb = 2
        # self.reset_ub = 3

    def init(self, face):
        self.face = face
        self.last_reset.trigger()
        self.pull_config()

    def from_dict(self, d):
        self.face = CubeFace(d['face'])
        self.last_reset.from_dict(d['last_reset'])
        self.num_rots = d['num_rots']
        self.last_strike.from_dict(d['last_strike'])
        self.pull_config()

    def to_dict(self):
        return {
            'face': self.face.value,
            'last_reset': self.last_reset.to_dict(),
            'num_rots': self.num_rots,
            'last_strike': self.last_strike.to_dict(),
        }

    def to_client_state(self):
        return {
            'module': self.name,
            'timer': self.last_reset.get_milliseconds_since(),
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
        }

    def generate_reset_val(self):
        reset_seconds = random.SystemRandom().randrange(self.reset_lb, self.reset_ub)
        return datetime.timedelta(seconds=reset_seconds)

    def get_lb(self):
        return datetime.timedelta(seconds=self.shake_lb)

    def get_ub(self):
        return datetime.timedelta(seconds=self.shake_ub)

    def get_rotations_needed(self):
        return ROTATIONS_NEEDED

    def reset_timer(self, full=False):
        new_counter_val = datetime.timedelta() if full else self.generate_reset_val()
        self.last_reset.trigger(datetime.datetime.now() - new_counter_val)
        self.num_rots = 0

    def make_updates(self):
        return {
            self.face: self.to_client_state()
        }

    def handle_rotate(self, view_matrix, rot_face):
        time_since = self.last_reset.get_time_since()
        if time_since < self.get_lb():
            return {}
        self.num_rots += 1
        if self.num_rots >= self.get_rotations_needed():
            self.reset_timer()
        return {}

    def is_strike(self):
        return self.last_reset.get_time_since() > self.get_ub()

    def do_strike(self):
        self.reset_timer(True)
        self.last_strike.trigger()
        return

    def make_periodic_updates(self):
        return self.make_updates()

    def make_full_updates(self):
        return self.make_updates()
