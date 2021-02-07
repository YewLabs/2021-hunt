import random
import datetime
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.modules.module_base import *

TIME_LIMIT = datetime.timedelta(minutes=20)
MAX_STRIKES = 3

class TimerModule(ModuleBase):
    name = 'timer'

    def __init__(self):
        self.face = None
        # time left is as if clock started at this point
        # may be different from real start depending on speed
        self.virtual_start = EventIndicator()
        self.speed = 1
        self.num_strikes = 0
        self.last_strike = EventIndicator()

    def init(self, face):
        self.face = face
        self.virtual_start.trigger()

    def from_dict(self, d):
        self.face = CubeFace(d['face'])
        self.virtual_start.from_dict(d['virtual_start'])
        self.speed = d['speed']
        self.num_strikes = d['num_strikes']
        self.last_strike.from_dict(d['last_strike'])

    def to_dict(self):
        return {
            'face': self.face.value,
            'virtual_start': self.virtual_start.to_dict(),
            'speed': self.speed,
            'num_strikes': self.num_strikes,
            'last_strike': self.last_strike.to_dict(),
        }

    def get_time_left(self):
        return TIME_LIMIT - self.speed * self.virtual_start.get_time_since()

    def change_speed(self, new_speed):
        curr_time = datetime.datetime.now()
        time_since = curr_time - self.virtual_start.last_trigger
        new_virtual_start = curr_time - time_since * self.speed / new_speed
        self.virtual_start.trigger(new_virtual_start)
        self.speed = new_speed

    def to_client_state(self):
        return {
            'module': self.name,
            'timeLeft': self.get_time_left() / datetime.timedelta(milliseconds=1),
            'speed': self.speed,
            'numStrikes': self.num_strikes,
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
        }

    def make_updates(self):
        return {
            self.face: self.to_client_state()
        }

    def make_updates_for_all(self):
        return {
            CubeFace(f): self.to_client_state()
            for f in range(len(CubeFace))
        }

    def register_strike(self):
        self.last_strike.trigger()
        self.num_strikes += 1
        return {}

    def is_explode(self):
        return self.num_strikes >= MAX_STRIKES

    def make_periodic_updates(self):
        return self.make_updates()

    def make_full_updates(self):
        # send updates to everyone for beeping speed
        return self.make_updates_for_all()
