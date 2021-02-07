import json
import sys

sys.path.insert(0, '../2021-hunt')

from hunt.special_puzzles.ktane.game import *
from hunt.special_puzzles.ktane.geom import *

game = KtaneGame()

def do_join(clid, spectate=False, god=False):
    return game.handle({
        'type': 'join',
        'spectate': spectate,
        'god': '2daefbe73d6f50c28fc7d728ea3b674564330fd22991bcec6f5ca438a0892985' if god else None
    }, clid)
def do_rotate(clid, rotateTxn, rotDir):
    return game.handle({
        'type': 'rotate',
        'rotateTxn': rotateTxn,
        'rotDir': rotDir,
    }, clid)

actions = do_join('x1')
actions = do_join('x2', True)
actions = do_join('x3')
actions = do_join('x4')
actions = do_join('x5', True, True)
actions = do_join('x6')
actions = do_join('x7')
actions = do_join('x8')
actions = do_join('x9', True)
print(game.players)
actions = game.players_manager.handle_disconnect('x1')
print(game.players)
actions = game.players_manager.handle_disconnect('x7')
actions = game.players_manager.handle_disconnect('x8')
actions = game.players_manager.handle_disconnect('x9')
print(game.players)
actions = do_join('x1')
print(game.players)
actions = game.handle({'type': ''}, 'x1')
actions = game.handle_start({}, 'x2')
actions = game.handle({'type': ''}, 'x1')
actions = game.players_manager.handle_disconnect('x1')
do_rotate('x5', 0, 3)
do_rotate('x5', 0, 3)
do_rotate('x5', 0, 3)
game.from_dict(json.loads(json.dumps(game.to_dict())))
game.players = [['x1'], ['x3'], ['x5'], ['x4'], ['x2'], ['x6']]
game.recompute_player_face()
actions = do_join('x7')
actions = do_join('x7')

# game.view_matrix = Matrix3x3.make_identity()
# print(game.cube.face)
# print(game.cube.answer)
# game.handle_module_input({
#     'module': 'cube',
#     'rotateTxn': 0,
# }, 'x4')
# game.handle_rotate({'rotDir': 2, 'rotateTxn': 0}, 'x1')
# print(game.module_slots)

# print(game.players)
# print('vm', game.view_matrix.to_dict())
# game.handle_rotate({'rotDir': 3, 'rotateTxn': 0}, 'x1')
# game.handle_rotate({'rotDir': 2, 'rotateTxn': 0}, 'x1')
# print('vm', game.view_matrix.to_dict())
# actions = game.handle({'type': ''}, 'x1')
# game.from_dict(json.loads(json.dumps(game.to_dict())))
# game.view_matrix = Matrix3x3.make_identity()
# game.handle_module_input({
#     'module': 'manual-1',
#     'rotateTxn': 1,
#     'sectionNum': 1
# }, 'x2')
# game.handle_module_input({
#     'module': 'cube',
#     'rotateTxn': 1,
# }, 'x4')
# print(game.module_slots)
# print(game.manual.section_nums)
