from random import Random


class GRandom(Random):
    def shuffled(self, x):
        x = list(x)
        self.shuffle(x)
        return x

    def distrib(self, total, count, *, min_=0, max_=None, skew=1):
        if min_ * count > total:
            raise ValueError(
                f"The total must be at least {min_}*{count}={min_*count} "
                f"when count={count} and min_={min_}"
            )
        if max_ is not None and max_ * count < total:
            raise ValueError(
                f"The total must be at most {max_}*{count}={max_*count} "
                f"when count={count} and max_={max_}"
            )
        if skew <= 0:
            raise ValueError("The skew has to be at least 1.")
        if max_ is None:
            max_ = total
        dist = [min_] * count
        inds = self.shuffled(range(count))
        for it in range(total - min_ * count):
            while True:
                assert inds
                idx = min(self.randrange(len(inds)) for it in range(skew))
                if dist[inds[idx]] < max_:
                    dist[inds[idx]] += 1
                    break
                else:
                    inds[idx], inds[-1] = inds[-1], inds[idx]
                    inds.pop()
        assert sum(dist) == total
        assert min_ <= min(dist) <= max(dist) <= max_
        return dist

    def data(self, arg, n=1):
        length = len(self.data_[arg])
        k = length + n + 1 if n < 0 else n
        return self.sample(self.data_[arg], k)

    def directions(self):
        return "".join(self.shuffled("CGNESW"))

    def side(self):
        return self.choice("UDFLBR")

    def talk_press(self):
        return "".join(self.choice("MmNn") for _ in range(4))

    def range_(self, min_, avg, max_):
        min_avg, max_avg = int((min_ + avg) / 2), int((max_ + avg) / 2)
        ch = self.randint(0, 6)
        if ch <= 1:
            return {"min": self.randint(avg, max_avg)}
        elif ch <= 3:
            return {"max": self.randint(min_avg, avg)}
        elif ch <= 5:
            z = self.randint(min_avg, max_avg)
            return {"min": z, "max": z}
        else:
            return {
                "min": self.randint(min_avg, avg),
                "max": self.randint(avg, max_avg),
            }

    def date_range_(self):
        ch = self.randint(0, 6)
        if ch <= 2:
            res = {"obj": "day", "min": 1, "max": 31}
            res.update(self.range_(1, 14, 31))
            return res
        elif ch <= 4:
            res = {"obj": "month", "min": 1, "max": 12}
            res.update(self.range_(1, 4, 12))
            return res
        else:
            res = {"obj": "year", "min": 2000, "max": 2020}
            res.update(self.range_(2000, 2010, 2020))
            return res

    def range(self, obj):
        if obj == "date":
            res = self.date_range_()
        else:
            res = {"obj": obj}
            res.update(self.range_(*self.data_["bounds"][obj]))
        return {"range": res}

    def simple_(self, objs, extra=None):
        new_objs = objs[:]
        if extra:
            new_objs.extend(extra)
        obj = self.choice(new_objs)
        if extra and obj in extra:
            return {obj: self.data(obj)[0]}
        ch = self.randint(0, 5)
        if ch == 0 and obj != "date":
            return {"odd": obj}
        elif ch == 1 and obj != "date":
            return {"even": obj}
        return self.range(obj)

    def condition_(self, objs, complexity=0, extra=None):
        # objs: ["batteries", "ports", "date", "serial digit"]
        # extra: ["gravity", "serial has"]
        if complexity == 3:
            res = self.condition_(objs, 2, extra)
            return res if self.randint(0, 4) else {"not": res}
        elif complexity == 2:
            ch = self.randint(0, 3)
            if ch <= 1 and len(objs) > 1:
                head, *tail = objs
                return {
                    "and"
                    if ch
                    else "or": [
                        self.condition_([head], 1),
                        self.condition_(tail, 1, extra),
                    ]
                }
            return self.condition_(objs, 1, extra)
        elif complexity == 1:
            res = self.simple_(objs, extra)
            has = lambda x: x in res["range"]
            one_sided = "range" in res and (has("min") != has("max"))
            return {"not": res} if not (self.randint(0, 3) or one_sided) else res
        return self.simple_(objs, extra)

    def simplify(self, res):
        # de morgan (and not not -> not or)
        if "and" in res and all("not" in x for x in res["and"]):
            return self.simplify({"not": {"or": [x["not"] for x in res["and"]]}})
        # de morgan (not and -> or not not)
        if "not" in res and "and" in res["not"]:
            return self.simplify({"or": [self.simplify({"not": x}) for x in res["not"]["and"]]})
        # double negation
        if "not" in res and "not" in res["not"]:
            return self.simplify(res["not"]["not"])
        return res

    def condition(self, *args):
        return self.simplify(self.condition_(*args))
