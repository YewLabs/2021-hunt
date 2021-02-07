import datetime

class EventIndicator:
    def __init__(self):
        self.last_trigger = None

    def reset(self):
        self.last_trigger = None

    def from_dict(self, d):
        self.last_trigger = None if d is None else (
            datetime.datetime.fromtimestamp(d)
        )

    def to_dict(self):
        return None if self.last_trigger is None else (
            datetime.datetime.timestamp(self.last_trigger)
        )

    def get_time_since(self):
        if self.last_trigger is None:
            return None
        return datetime.datetime.now() - self.last_trigger

    def get_milliseconds_since(self):
        td = self.get_time_since()
        if td is None:
            return None
        return td / datetime.timedelta(milliseconds=1)

    def trigger(self, new_val=None):
        if new_val is None:
            self.last_trigger = datetime.datetime.now()
        else:
            self.last_trigger = new_val

class ModuleBase:
    def handle_rotate(self, view_matrix, rot_face):
        return {}

    def handle_input(self, msg, submodule=None):
        return {}

    def is_strike(self):
        return False

    def do_strike(self):
        return

    # use this to do periodic updates like timer checks
    def make_periodic_updates(self):
        return {}

    def make_full_updates(self):
        return {}

    def is_disarmed(self):
        return True
