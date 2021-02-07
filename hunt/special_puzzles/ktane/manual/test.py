import os, sys
import os.path

SERVER_ROOT = "../../../.."
CLIENT_REPO = "../../../../../ktane-client"

curr_dir = os.path.dirname(__file__)
if curr_dir != '':
    os.chdir(curr_dir)
sys.path.insert(0, SERVER_ROOT)

from gen import *
from make_json import gen_manual
import json, pprint, yaml

with open("data.json", "r") as f:
    data = json.loads(f.read())


def gen_bomb(data, manual, seed):
    global_state = gen_global_bomb_data(data, manual, seed, "")
    modules = {
        "global": gen_global_bomb_data,
        "gravity": gen_bomb_gravity,
        "six": gen_bomb_six,
        "talk": gen_bomb_talk,
        "wires": gen_bomb_wires,
        "buttons": gen_bomb_buttons,
        "passwords": gen_bomb_passwords,
        "simon": gen_bomb_simon,
        "cube": gen_bomb_cube,
    }
    bomb_data = {}
    for module_name, module_func in modules.items():
        bomb_data[module_name] = module_func(data, manual, seed, global_state)
    return bomb_data


def test(seed=None):
    def subtest(seed):
        pprint.pprint(seed)
        manual = gen_manual(data, seed)
        pprint.pprint(manual)
        bomb = gen_bomb(data, manual, seed)
        pprint.pprint(bomb)

    if seed:
        return subtest(seed)
    while True:
        subtest(GRandom().randint(0, 1 << 32))


if __name__ == "__main__":
    # with open("example_manual.json", "r") as f:
    #     manual = json.loads(f.read())
    if len(sys.argv) == 1:
        test()
    elif len(sys.argv) == 2:
        seed = sys.argv[1]
        file = os.path.join(CLIENT_REPO, "js/modules/manual/example_manual.js")
    elif len(sys.argv) == 3:
        seed, file = sys.argv[1:]
    manual = gen_manual(data, seed)
    bomb = gen_bomb(data, manual, seed)
    pprint.pprint(seed)
    pprint.pprint(manual)
    pprint.pprint(bomb)
    with open(file, "w") as f:
        f.write("export default " + json.dumps(manual))
    with open("example_manual.yaml", "w") as f:
        f.write(yaml.dump(manual, sort_keys=False))
