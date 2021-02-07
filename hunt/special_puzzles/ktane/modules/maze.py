import random
from hunt.special_puzzles.ktane.geom import *
from hunt.special_puzzles.ktane.modules.module_base import *
from hunt.special_puzzles.ktane.validate import Validator as V

class MazeGen:
    @staticmethod
    def num_horizontal(w, h):
        return (w - 1) * h

    @staticmethod
    def num_vertical(w, h):
        return (h - 1) * w

    @staticmethod
    def num_edges(w, h):
        return MazeGen.num_horizontal(w, h) + MazeGen.num_vertical(w, h)

    # horizontal edges come first, then vertical edges
    @staticmethod
    def is_horizontal(w, h, e):
        return e < MazeGen.num_horizontal(w, h)

    def get_edge_endpoints(w, h, e):
        if MazeGen.is_horizontal(w, h, e):
            x1 = e % (w-1)
            x2 = x1 + 1
            y = e // (w-1)
            return [(x1, y), (x2, y)]
        else:
            e -= MazeGen.num_horizontal(w, h)
            y1 = e % (h-1)
            y2 = y1 + 1
            x = e // (h-1)
            return ((x, y1), (x, y2))

    def ufds_get_parent(ufds, n):
        if ufds[n] == n:
            return n
        parent = MazeGen.ufds_get_parent(ufds, ufds[n])
        ufds[n] = parent
        return parent

    @staticmethod
    def make_maze(w, h, seed):
        edge_order = list(range(MazeGen.num_edges(w, h)))
        random.Random(seed).shuffle(edge_order)
        horz_edge_blocked = [0] * h # bitmasks
        vert_edge_blocked = [0] * w # bitmasks
        # kruskal
        ufds = list(range(w * h))
        for e in edge_order:
            (n1x, n1y), (n2x, n2y) = MazeGen.get_edge_endpoints(w, h, e)
            n1 = n1y * w + n1x
            n2 = n2y * w + n2x
            p1 = MazeGen.ufds_get_parent(ufds, n1)
            p2 = MazeGen.ufds_get_parent(ufds, n2)
            if p1 == p2:
                if n1y == n2y:
                    horz_edge_blocked[n1y] |= 1 << n1x
                else:
                    vert_edge_blocked[n1x] |= 1 << n1y
            ufds[p1] = p2
        horz_edges = [((1 << w) - 1) & (~edges) for edges in horz_edge_blocked]
        vert_edges = [((1 << h) - 1) & (~edges) for edges in vert_edge_blocked]
        return horz_edges, vert_edges

MAZE_WIDTH, MAZE_HEIGHT = 10, 10

class MazeModule(ModuleBase):
    name = 'maze'

    def __init__(self, game):
        self.game = game

        self.display_face = None
        self.control_face = None
        self.horz_edges = None
        self.vert_edges = None
        self.x = MAZE_WIDTH - 1
        self.y = MAZE_HEIGHT - 1
        self.goal_x = 0
        self.goal_y = 0
        self.last_strike = EventIndicator()
        # used to help players synchronize between control and display
        self.control_txn = 0
        self.display_txn = 0

        self.strike = False

    def pull_config(self):
        # TODO: get this seed from ManualInfo
        self.horz_edges, self.vert_edges = MazeGen.make_maze(
            MAZE_WIDTH, MAZE_HEIGHT, self.seed
        )

    def init(self, control_face, display_face):
        self.seed = self.game.manual.maze_seed
        self.control_face = control_face
        self.display_face = display_face
        self.pull_config()

    def from_dict(self, d):
        self.control_face = CubeFace(d['control_face'])
        self.display_face = CubeFace(d['display_face'])
        self.last_strike.from_dict(d['last_strike'])
        self.x = d['x']
        self.y = d['y']
        self.control_txn = d['control_txn']
        self.display_txn = d['display_txn']
        self.seed = d['seed']
        self.pull_config()

    def to_dict(self):
        return {
            'control_face': self.control_face.value,
            'display_face': self.display_face.value,
            'last_strike': self.last_strike.to_dict(),
            'x': self.x,
            'y': self.y,
            'control_txn': self.control_txn,
            'display_txn': self.display_txn,
            'seed': self.seed,
        }

    def get_submodule_index(self, is_control):
        return 0 if is_control else 1

    def get_name(self, is_control):
        return self.name + '-' + str(self.get_submodule_index(is_control))

    def handle_rotate(self, view_matrix, rot_face):
        self.control_txn = 0
        self.display_txn = 0
        return {}

    def is_disarmed(self):
        return self.x == self.goal_x and self.y == self.goal_y

    def to_client_control_state(self):
        return {
            'module': self.name,
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
            'disarmed': self.is_disarmed(),
            'txn': self.display_txn,
        }

    def to_client_display_state(self):
        return {
            'module': self.name,
            'timeSinceStrike': self.last_strike.get_milliseconds_since(),
            'disarmed': self.is_disarmed(),
            'txn': self.control_txn,
            'horzEdges': self.horz_edges,
            'vertEdges': self.vert_edges,
            'x': self.x,
            'y': self.y,
        }

    def make_updates(self):
        return {
            self.control_face: self.to_client_control_state(),
            self.display_face: self.to_client_display_state(),
        }

    # unit 0 is control, unit 1 is display
    def is_control(self, submodule):
        return submodule == 0

    def has_horz_edge(self, x, y):
        if x < 0 or x+1 >= MAZE_WIDTH:
            return False
        return ((self.horz_edges[y] >> x) & 1) == 1

    def has_vert_edge(self, x, y):
        if y < 0 or y+1 >= MAZE_HEIGHT:
            return False
        return ((self.vert_edges[x] >> y) & 1) == 1

    # coordinates increase in east and south directions
    def has_wall(self, x, y, direction):
        return not {
            CardinalDirection.n: self.has_vert_edge(x, y-1),
            CardinalDirection.e: self.has_horz_edge(x, y),
            CardinalDirection.s: self.has_vert_edge(x, y),
            CardinalDirection.w: self.has_horz_edge(x-1, y),
        }[direction]

    def handle_input(self, msg, submodule=None):
        if not V.has_key(msg, 'txn') and V.has_key(msg, 'direction'):
            return {}
        client_txn = msg['txn']
        direction = msg['direction']
        if not V.is_nat(client_txn) or not V.is_nat(direction, len(CardinalDirection)):
            return {}

        if self.is_disarmed():
            return {}
        if self.is_control(submodule):
            self.control_txn = client_txn
            direction = CardinalDirection(direction)
            if self.has_wall(self.x, self.y, direction):
                self.strike = True
            else:
                self.x, self.y = direction.move_point(self.x, self.y)
            if len(self.game.players[self.display_face.value]) == 0:
                self.display_txn = self.control_txn
        else:
            self.display_txn = client_txn
        return self.make_updates()

    def is_strike(self):
        return self.strike

    def do_strike(self):
        self.last_strike.trigger()
        return

    def make_full_updates(self):
        return self.make_updates()
