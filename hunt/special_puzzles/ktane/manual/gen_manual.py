from hunt.special_puzzles.ktane.manual.grandom import *
from hunt.special_puzzles.ktane.geom import *
import json, itertools


def gen_empty(*args):
    pass


def gen_gravity(data, seed, global_state):
    rand = GRandom(seed)
    rand.data_ = data
    objs = global_state[0]
    res = []
    n_conds = rand.randint(2, 3)
    dirs = rand.directions()
    for dir_ in dirs[:n_conds]:
        res.append(
            {"condition": rand.condition(objs, 2, ["gravity"]), "direction": dir_}
        )
    res.append({"condition": "", "direction": dirs[-1]})
    return res


def gen_six(data, seed, global_state):
    rand = GRandom(seed)
    rand.data_ = data
    objs = global_state[1]
    res = []
    n_conds = rand.randint(2, 3)
    for _ in range(n_conds):
        res.append(
            {"condition": rand.condition(objs, 3), "direction": rand.directions()}
        )
    res.append({"condition": "", "direction": rand.directions()})
    return res


def get_normalized_str(s):
    return [c for c in s.lower() if c.isalpha()]


def gen_talk(data, seed, global_state):
    rand = GRandom(seed)
    rand.data_ = data
    res = []
    for texts in rand.data("talk", -1):
        for text in texts:
            res.append({"text": text, "press": rand.talk_press()})
    return sorted(res, key=lambda x: get_normalized_str(x["text"]))


def gen_wires(data, seed, global_state):
    rand = GRandom(seed)
    rand.data_ = data
    table = []
    dirs = [d for _ in range(3) for d in rand.directions()]
    for wire in rand.data("wires", -3):
        if wire == "striped" or rand.randint(0, 3):
            table.append({"wire": wire, "direction": [dirs.pop()]})
        else:
            table.append({"wire": wire, "direction": [dirs.pop(), dirs.pop()]})
    return {"side": rand.side(), "table": sorted(table, key=lambda v: v["wire"])}


def gen_sequential(rand, objs):
    res = []
    n_conds = 2
    for _ in range(n_conds):
        res.append(
            {
                "condition": rand.condition(objs, 2),
                "buttons": rand.data("buttons", 12),
            }
        )
    res.append({"condition": "", "buttons": rand.data("buttons", 12)})
    return res


def gen_simultaneous(rand, objs):
    table = []
    n_conds = 2
    cats = rand.data("buttons button", -1)
    for cat in cats[:n_conds]:
        inst = {"modules": rand.data("buttons modules")[0], "category": cat}
        table.append({"condition": rand.condition(objs, 2), "instruction": inst})
    inst = {"modules": rand.data("buttons modules")[0], "category": cats[n_conds]}
    table.append({"condition": "", "instruction": inst})

    n_per_category = 4
    cats = rand.data_["buttons button"]
    categories = []
    but = rand.data("buttons", n_per_category * len(cats))
    for i in range(len(cats)):
        categories.append(
            {
                "category": cats[i],
                "buttons": but[i * n_per_category : (i + 1) * n_per_category],
            }
        )

    return {"table": table, "categories": categories}


def gen_buttons(data, seed, global_state):
    rand = GRandom(seed)
    rand.data_ = data
    objs = global_state[2]
    return {
        "condition": rand.condition(objs, 3, ["serial has"]),
        "sequential": gen_sequential(rand, objs),
        "simultaneous": gen_simultaneous(rand, objs),
    }


def gen_passwords(data, seed, global_state):
    rand = GRandom(seed)
    rand.data_ = data
    return {
        "directions": "".join(rand.shuffled("FBLR")),
        "words": sorted(rand.data("passwords", 20)),
    }


def gen_shake(data, seed, global_state):
    rand = GRandom(seed)
    rand.data_ = data
    rate = 3
    X = rand.randint(rate * 25, rate * 35)
    Y = X + 10 * rate
    Z = rand.randint(10, rate * 10 + 5)
    return {"X": X, "Y": Y, "Z": Z}


def gen_global_manual_data(data, seed, global_state):
    rand = GRandom(seed)
    rand.data_ = data
    obj1, obj2, obj3 = rand.shuffled(
        [["batteries", "date"], ["ports", "date"], ["serial digit", "serial letters"]]
    )
    return [obj1, obj2, obj3]
