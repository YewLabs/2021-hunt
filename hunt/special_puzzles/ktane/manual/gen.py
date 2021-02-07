from hunt.special_puzzles.ktane.manual.grandom import *
from hunt.special_puzzles.ktane.manual.gen_manual import *
from hunt.special_puzzles.ktane.geom import *
import json, itertools


def gen_bomb_indicators(rand):
    # gen global state
    serial = "".join(
        rand.choice("AAAACEEEEFHJKLMNPRTUUUVWX3333333444447777779999") for _ in range(5)
    ) + str(rand.randint(0, 9))
    year = rand.randint(2000, 2020)
    month = rand.randint(1, 12)
    day = rand.randint(1, 28)
    date = f"{year}-{month:02}-{day:02}"
    n_batteries = rand.randint(3, 12)
    n_ports = rand.randint(3, 8)
    return {
        "serial": serial,
        "serial digit": int(serial[-1]),
        "serial letters": len([x for x in serial if x.isalpha()]),
        "year": year,
        "month": month,
        "day": day,
        "date": date,
        "batteries": n_batteries,
        "ports": n_ports,
    }


def gen_global_bomb_data(data, manual, seed, global_state):
    rand = GRandom(seed)
    global_state = gen_bomb_indicators(rand)
    slots = [0] * 7
    slots[0] = rand.shuffled(["timer", "shakeit", "gravity", "six"])
    slots[1] = [f"buttons-{i}" for i in range(4)]
    slots[2] = [0] * 4
    for i, v in enumerate(rand.shuffled(["maze", "simon"])):
        slots[2][i::2] = rand.shuffled([f"{v}-0", f"{v}-1"])
    slots[3] = rand.shuffled(["whosonfirst0", "whosonfirst1", "wires", "cube"])
    slots[4] = [f"passwords-{i}" for i in range(4)]
    slot56 = rand.shuffled(
        [
            "serial",
            "date",
            *[f"batteries-{i}" for i in range(3)],
            *[f"ports-{i}" for i in range(3)],
        ]
    )
    slots[5] = slot56[::2]
    slots[6] = slot56[1::2]
    global_state["modules"] = dict(
        zip([CubeFace.front, CubeFace.left, CubeFace.back, CubeFace.right], zip(*slots))
    )
    for side, mods in global_state["modules"].items():
        global_state["modules"][side] = rand.shuffled(mods[:4]) + list(mods[4:])
    global_state["modules"][CubeFace.top] = ["manual-1"]
    global_state["modules"][CubeFace.bottom] = ["manual-0"]
    global_state["batteries_modules"] = rand.distrib(
        global_state["batteries"], 3, min_=1, max_=4
    )
    global_state["ports_modules"] = rand.distrib(
        global_state["ports"], 3, min_=1, max_=4
    )
    return global_state


def gen_bomb_batteries(data, manual, seed, global_state):
    rand = GRandom(seed)
    return {"batteries": rand.distrib(global_state["batteries"], 3, max_=4)}


def gen_bomb_ports(data, manual, seed, global_state):
    rand = GRandom(seed)
    return {"ports": rand.distrib(global_state["ports"], 3, max_=4)}


def is_satisfied(cond, global_state):
    if cond == "":
        return True
    if "and" in cond:
        return all(is_satisfied(cd, global_state) for cd in cond["and"])
    if "or" in cond:
        return any(is_satisfied(cd, global_state) for cd in cond["or"])
    if "not" in cond:
        return not is_satisfied(cond["not"], global_state)
    if "even" in cond or "odd" in cond:
        par = "even" if "even" in cond else "odd"
        return global_state[cond[par]] % 2 == (0 if par == "even" else 1)
    if "range" in cond:
        cd = cond["range"]
        obj = global_state[cd["obj"]]
        if "min" in cd and obj < cd["min"]:
            return False
        if "max" in cd and obj > cd["max"]:
            return False
        return True
    if "serial has" in cond:
        return (
            any(c in global_state["serial"] for c in "AEIOU")
            if cond["serial has"] == "vowel"
            else any(c in global_state["serial"] for c in "BCDFGHJKLMNPQRSTVWXYZ")
        )
    if "gravity" in cond:
        return cond["gravity"] == global_state["gravity"]
    raise Exception("unknown condition")


def gen_bomb_gravity(data, manual, seed, global_state):
    rand = GRandom(seed)
    text = rand.choice(data["gravity"])
    global_state["gravity"] = text
    for row in manual["gravity"]:
        if is_satisfied(row["condition"], global_state):
            direction = row["direction"]
            break
    return {"text": text, "direction": direction}


def gen_bomb_six(data, manual, seed, global_state):
    rand = GRandom(seed)
    for row in manual["six"]:
        if is_satisfied(row["condition"], global_state):
            direction = row["direction"]
            break
    init = sum(rand.sample([1, 2, 4, 8, 16, 32], 2))
    return {"direction": direction, "init": init}


def gen_bomb_talk_with_rand(data, manual, rand, global_state):
    # this one is independent of which module it is, so just call it twice?
    data = rand.choice(manual["talk"])
    # warning: these must be synced with the client
    button_texts = ["N", "n", "M", "m"]
    button_order = list(range(4))
    rand.shuffle(button_order)
    return {
        "prompt": data["text"],
        "answer": [button_texts.index(c) for c in data["press"]],
        "button_order": button_order,
    }


def gen_bomb_talk(data, manual, seed, global_state):
    rand = GRandom(seed)
    return [
        gen_bomb_talk_with_rand(data, manual, rand, global_state),
        gen_bomb_talk_with_rand(data, manual, rand, global_state),
    ]


def gen_bomb_wires(data, manual, seed, global_state):
    rand = GRandom(seed)
    n_wires = 5
    colors = rand.choices(range(4), k=n_wires)
    striped = rand.randint(0, (1 << n_wires) - 1)
    console_side = manual["wires"]["side"]
    get_man = lambda s: [
        dir_
        for obj in manual["wires"]["table"]
        if obj["wire"] == s
        for dir_ in obj["direction"]
    ]
    to_color = ["white", "blue", "black", "yellow"]
    to_dict = ["first", "second", "third", "fourth", "fifth"]
    allowed_sides = []
    for i, col in enumerate(colors):
        bad = set(get_man(to_dict[i])) | set(get_man(to_color[col]))
        if striped & (1 << i):
            bad |= set(get_man("striped"))
        good = set("CGNESW") - bad
        allowed_sides.append(sorted(good))
    return {
        "colors": colors,
        "striped": striped,
        "console_side": console_side,
        "allowed_sides": allowed_sides,
    }


def gen_bomb_buttons(data, manual, seed, global_state):
    rand = GRandom(seed)
    n_modules = 4
    n_buttons = 4
    labels = rand.sample(data["buttons"], n_modules * n_buttons)
    type_ = (
        "sequential"
        if is_satisfied(manual["buttons"]["condition"], global_state)
        else "simultaneous"
    )
    subman = manual["buttons"][type_]
    if type_ == "sequential":
        for row in subman:
            if is_satisfied(row["condition"], global_state):
                buttons = row["buttons"]
                break
        btnset = set(buttons)
        fake_buttons = [s for s in data["buttons"] if s not in btnset]
        n_fake = rand.randint(4, 6)
        labels = rand.sample(buttons, n_modules * n_buttons - n_fake)
        labels.extend(rand.sample(fake_buttons, n_fake))
        rand.shuffle(labels)
        return {
            "type_": type_,
            "labels": dict(
                zip(
                    [CubeFace.front, CubeFace.left, CubeFace.back, CubeFace.right],
                    [
                        labels[n_buttons * i : n_buttons * (i + 1)]
                        for i in range(n_modules)
                    ],
                )
            ),
            "answer": [b for b in buttons if b in labels],
        }

    for row in subman["table"]:
        if is_satisfied(row["condition"], global_state):
            modules = row["instruction"]["modules"]
            category = row["instruction"]["category"]
            break
    good_category = [
        x["buttons"] for x in subman["categories"] if x["category"] == category
    ][0]
    true_buttons = rand.sample(good_category, 3 if modules == "opposite" else 2)
    btnset = set(true_buttons)
    fake_buttons = [b for b in data["buttons"] if b not in good_category]
    labels = rand.sample(fake_buttons, n_modules * n_buttons)
    labels = dict(
        zip(
            [CubeFace.front, CubeFace.left, CubeFace.back, CubeFace.right],
            [labels[n_buttons * i : n_buttons * (i + 1)] for i in range(n_modules)],
        )
    )
    if modules == "opposite":
        true_sides = rand.sample(
            [CubeFace.front, CubeFace.back, CubeFace.left, CubeFace.right], 3
        )
    elif modules == "adjacent":
        true_sides = rand.choice(
            [
                [CubeFace.front, CubeFace.left],
                [CubeFace.front, CubeFace.right],
                [CubeFace.back, CubeFace.left],
                [CubeFace.back, CubeFace.right],
            ]
        )
    for i, side in enumerate(true_sides):
        labels[side][rand.randint(0, n_buttons - 1)] = true_buttons[i]
    for i, s1 in enumerate(true_sides):
        for j, s2 in enumerate(true_sides):
            if (modules == "opposite" and s1.get_opposite() == s2) or (
                modules == "adjacent" and CubeFace.is_adjacent(s1, s2)
            ):
                ans1, ans2 = true_buttons[i], true_buttons[j]
    return {
        "type_": type_,
        "labels": labels,
        "answer": [ans1, ans2],
    }


def gen_bomb_passwords(data, manual, seed, global_state):
    rand = GRandom(seed)
    true_words = manual["passwords"]["words"]
    twset = set(true_words)
    fake_words = [p for p in data["passwords"] if p not in twset]
    n_true = lambda: sum("".join(w) in true_words for w in itertools.product(*letters))
    n_fake = lambda: sum("".join(w) in fake_words for w in itertools.product(*letters))
    attempts = 0
    letters = ["AAA"] * 4
    while n_true() != 1 or n_fake() < 3 or any(len(set(s)) < 3 for s in letters):
        answer = rand.sample(true_words, 1)[0]
        letters = list(zip(answer, *rand.sample(fake_words, 2)))
        attempts += 1
    while "".join(lts[0] for lts in letters) == answer:
        letters = [rand.shuffled(lts) for lts in letters]
    tenum = {
        "B": CubeFace.back,
        "L": CubeFace.left,
        "F": CubeFace.front,
        "R": CubeFace.right,
    }
    faces = list(map(tenum.__getitem__, manual["passwords"]["directions"]))
    return {
        "letters": dict(zip(faces, letters)),
        "answer": dict(zip(faces, answer)),
    }


def gen_bomb_simon(data, manual, seed, global_state):
    rand = GRandom(seed)
    return {
        "lights": [
            rand.choices(
                [
                    CardinalDirection.n,
                    CardinalDirection.e,
                    CardinalDirection.s,
                    CardinalDirection.w,
                ],
                k=10,
            )
            for _ in range(3)
        ]
    }


def gen_bomb_maze(data, manual, seed, global_state):
    pass  # mark handles this xp


def gen_bomb_cube(data, manual, seed, global_state):
    rand = GRandom(seed)
    n_turns = rand.randint(4, 5)
    trans = {
        "D": CubeFace.top,
        "U": CubeFace.bottom,
        "R": CubeFace.left,
        "L": CubeFace.right,
        "F": CubeFace.back,
        "B": CubeFace.front,
    }
    seq = "".join(rand.side() for _ in range(n_turns))
    return {"text": seq, "turns": list(map(trans.__getitem__, seq))}
