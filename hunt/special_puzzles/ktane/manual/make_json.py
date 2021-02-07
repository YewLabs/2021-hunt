import sys

sys.path.insert(0, "../../../../../2021-hunt")

# TODO: run this to make sure yaml data is synced to json data
import yaml
from gen import *


# this is just for testing and would not be used in the actual game
def gen_manual(data, seed):
    global_state = gen_global_manual_data(data, seed, "")

    modules = {
        "gravity": gen_gravity,
        "six": gen_six,
        "talk": gen_talk,
        "wires": gen_wires,
        "buttons": gen_buttons,
        "passwords": gen_passwords,
        "shake": gen_shake,
    }
    manual_data = {}
    for module_name, module_func in modules.items():
        manual_data[module_name] = module_func(data, seed, global_state)
    return manual_data


if __name__ == "__main__":
    data = yaml.load(open("data.yaml"), Loader=yaml.SafeLoader)
    with open("data.json", "w") as f:
        f.write(json.dumps(data))
    # print(yaml.dump(manual, sort_keys=False))

    manual = gen_manual(data, 11)
    with open("example_manual.json", "w") as f:
        f.write(json.dumps(manual))
    with open("../../../../../ktane-client/js/modules/manual/example_manual.js", "w") as f:
        f.write("export default " + json.dumps(manual))
    with open("example_manual.yaml", "w") as f:
        f.write(yaml.dump(manual, sort_keys=False))
    
    # print(get_page(data, manual, 1))
