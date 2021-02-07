from enum import Enum

class Vector3():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def dot(self, vec):
        return self.x * vec.x + self.y * vec.y + self.z * vec.z

    def from_dict(self, d):
        self.x = d['x']
        self.y = d['y']
        self.z = d['z']

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
        }

    def __eq__(self, vec):
        return self.x == vec.x and self.y == vec.y and self.z == vec.z

class Matrix3x3():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def mult_vec(self, vec):
        return Vector3(
            self.x.dot(vec),
            self.y.dot(vec),
            self.z.dot(vec),
        )

    def get_transpose(self):
        return Matrix3x3(
            Vector3(self.x.x, self.y.x, self.z.x),
            Vector3(self.x.y, self.y.y, self.z.y),
            Vector3(self.x.z, self.y.z, self.z.z)
        )

    def left_mult(self, mat):
        t = self.get_transpose()
        return Matrix3x3(
            t.mult_vec(mat.x),
            t.mult_vec(mat.y),
            t.mult_vec(mat.z),
        )

    @staticmethod
    def make_identity():
        return Matrix3x3(
            Vector3(1, 0, 0),
            Vector3(0, 1, 0),
            Vector3(0, 0, 1)
        )

    # axis must be a unit vector, matrix must be ortho aa
    # rotation follows right-hand rule
    @staticmethod
    def make_rotate_90deg_ortho_aa(axis):
        return Matrix3x3(
            Vector3(abs(axis.x), -axis.z, axis.y),
            Vector3(axis.z, abs(axis.y), -axis.x),
            Vector3(-axis.y, axis.x, abs(axis.z))
        )

    def from_dict(self, d):
        self.x.from_dict(d['x'])
        self.y.from_dict(d['y'])
        self.z.from_dict(d['z'])

    def to_dict(self):
        return {
            'x': self.x.to_dict(),
            'y': self.y.to_dict(),
            'z': self.z.to_dict(),
        }

    def __eq__(self, mat):
        return self.x == mat.x and self.y == mat.y and self.z == mat.z

# specialized for axis-aligned orthogonal matrices
class CardinalDirection(Enum):
    n = 0
    e = 1
    s = 2
    w = 3

    def move_point(self, x, y):
        return {
            CardinalDirection.n: (x, y-1),
            CardinalDirection.e: (x+1, y),
            CardinalDirection.s: (x, y+1),
            CardinalDirection.w: (x-1, y),
        }[self]

class CubeFace(Enum):
    front = 0
    back = 1
    left = 2
    right = 3
    top = 4
    bottom = 5

    def get_opposite(self):
        return {
            CubeFace.front: CubeFace.back,
            CubeFace.back: CubeFace.front,
            CubeFace.left: CubeFace.right,
            CubeFace.right: CubeFace.left,
            CubeFace.top: CubeFace.bottom,
            CubeFace.bottom: CubeFace.top,
        }[self]

    def get_vec(self):
        return {
            CubeFace.front: Vector3(0, 0, 1),
            CubeFace.back: Vector3(0, 0, -1),
            CubeFace.left: Vector3(-1, 0, 0),
            CubeFace.right: Vector3(1, 0, 0),
            CubeFace.top: Vector3(0, 1, 0),
            CubeFace.bottom: Vector3(0, -1, 0)
        }[self]

    @staticmethod
    def from_vec(vec):
        if vec.z == 1:
            return CubeFace.front
        elif vec.z == -1:
            return CubeFace.back
        elif vec.x == -1:
            return CubeFace.left
        elif vec.x == 1:
            return CubeFace.right
        elif vec.y == 1:
            return CubeFace.top
        elif vec.y == -1:
            return CubeFace.bottom
        else:
            raise Exception('vector doesn\'t represent a CubeFace')

    @staticmethod
    def to_rot(face):
        return Matrix3x3.make_rotate_90deg_ortho_aa(face.get_vec())

    @staticmethod
    def is_adjacent(face1, face2):
        return face1 != face2 and face1.get_opposite() != face2
