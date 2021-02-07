from hunt.special_puzzles.ktane.geom import *

class KtaneGameGeom:
    @staticmethod
    def get_relative_player_view(face):
        orient = Matrix3x3.make_identity()
        if (face == CubeFace.back):
            orient = orient.left_mult(CubeFace.to_rot(CubeFace.top))
            orient = orient.left_mult(CubeFace.to_rot(CubeFace.top))
        elif (face == CubeFace.left):
            orient = orient.left_mult(CubeFace.to_rot(CubeFace.bottom))
        elif (face == CubeFace.right):
            orient = orient.left_mult(CubeFace.to_rot(CubeFace.top))
        elif (face == CubeFace.top):
            orient = orient.left_mult(CubeFace.to_rot(CubeFace.left))
        elif (face == CubeFace.bottom):
            orient = orient.left_mult(CubeFace.to_rot(CubeFace.right))
        return orient

    @staticmethod
    def get_player_view_matrix(view_mat, player_slot):
        rel_view_mat = KtaneGameGeom.get_relative_player_view(player_slot)
        return rel_view_mat.left_mult(view_mat)

    # gets the face to rotate if rotation is issued from front face
    @staticmethod
    def rot_dir_to_face(d):
        return {
            CardinalDirection.n: CubeFace.left,
            CardinalDirection.e: CubeFace.top,
            CardinalDirection.s: CubeFace.right,
            CardinalDirection.w: CubeFace.bottom
        }[d]

    @staticmethod
    def rot_by_face(view_matrix, rot_face):
        rot_axis = rot_face.get_vec()
        rot_mat = Matrix3x3.make_rotate_90deg_ortho_aa(rot_axis)
        new_view_matrix = view_matrix.left_mult(rot_mat)
        return new_view_matrix

    @staticmethod
    def player_dir_to_rot_face(view_matrix, player_face, rot_dir):
        player_view_matrix = KtaneGameGeom.get_player_view_matrix(
            view_matrix, player_face
        )
        rot_face_rel = KtaneGameGeom.rot_dir_to_face(rot_dir)
        rot_axis_rel = rot_face_rel.get_vec()
        rot_axis = player_view_matrix.mult_vec(rot_axis_rel)
        rot_face = CubeFace.from_vec(rot_axis)
        return rot_face

    @staticmethod
    def player_face_to_face(view_matrix, player_face):
        player_vec = player_face.get_vec()
        vec = view_matrix.mult_vec(player_vec)
        return CubeFace.from_vec(vec)

    @staticmethod
    def char_to_cube_face(c):
        return {
            'C': CubeFace.top,
            'G': CubeFace.bottom,
            'N': CubeFace.back,
            'E': CubeFace.right,
            'S': CubeFace.front,
            'W': CubeFace.left,
        }[c]
