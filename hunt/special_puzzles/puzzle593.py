# See silenda/spoilr/puzzle_session.py
# Error Messages: <div id="puzzle-session-error-message-container"></div>
# <script src="/static/puzzle_session.js"></script>
# var session = new PuzzleSession("URL");
# session.json_request(JSON_PAYLOAD, function(res) {});

from django.db import models
from django.core.validators import int_list_validator
from spoilr.models import *
from spoilr.puzzle_session import *
from typing import Optional
import operator
import codecs
import itertools
import string
import base64
import json
import time

from hunt.teamwork import TeamworkTimeConsumer

class Puzzle593TeamData(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    node_colors = models.CharField(default="red,"*73+"red", max_length=500)

    def __str__(self):
        return '%s' % (self.team)

boxes = [1, 11, 12, 19, 33, 34, 43, 44, 51, 57, 70, 79, 83, 84, 91, 98, 104, 110, 116, 137, 141, 142, 149, 158, 162, 163, 169, 199, 206, 215, 219, 228, 229, 238, 239, 257, 261, 265, 270, 271, 278, 284, 290, 310, 314, 318, 322, 326, 349, 350, 356, 365, 367, 376, 377, 384, 409, 410, 417, 427, 432, 436, 440, 441, 448, 461, 470, 474, 478, 494, 498, 502, 503, 509]
words = [25 ,63 ,97 ,123,148,176,220,246,266,296,327,366,390,428,454,479,516]

depends = {}
depends[25] = [19, 1, 11, 12]
depends[63] = [33, 34, 43, 44, 51, 57]
depends[97] = [70, 79, 83, 84, 91]
depends[123] = [104, 98, 116, 110]
depends[148] = [137, 141, 142]
depends[176] = [162, 163, 169, 141, 149, 158]
depends[220] = [215, 219, 206, 199]
depends[246] = [228, 229, 238, 239]
depends[266] = [257, 261, 265]
depends[296] = [290, 270, 271, 278, 284]
depends[327] = [322, 326, 310, 314, 318]
depends[366] = [365, 356, 349, 350]
depends[390] = [376, 377, 384, 367]
depends[428] = [409, 410, 417, 427]
depends[454] = [448, 432, 436, 440, 441]
depends[479] = [474, 478, 461, 470]
depends[516] = [494, 498, 502, 503, 509]

class Puzzle593Consumer(TeamworkTimeConsumer):
    def setup(self):
        super(Puzzle593Consumer, self).setup(593)

    @transaction.atomic
    def set_node_color(self, box_id, color):
        changed = False
        data = Puzzle593TeamData.objects.get_or_create(team=self.team)[0]
        values = data.node_colors.split(",")
        try:
            val = boxes.index(box_id)
            if values[val] != color:
                values[val] = color
                changed = True
                data.node_colors = ",".join(values)
                data.save()
        except:
            pass
        colors = {}
        for i,boxid in enumerate(boxes):
            colors[boxid] = values[i]
        return colors, changed

    @transaction.atomic
    def get_all_colors(self):
        data = Puzzle593TeamData.objects.get_or_create(team=self.team)[0]
        values = data.node_colors.split(",")
        colors = {}
        for i,boxid in enumerate(boxes):
            colors[boxid] = values[i]
        return colors


    def handle(self, msg):
        if msg['type'] == 'colortoggle':
            box = msg['box']
            new_color = msg['color']
            colors, changed = self.set_node_color(box, new_color)
            if changed:
                response = {
                    "colors": {str(box): new_color},
                    "words": {},
                    'type': 'statusUpdate'
                }
                for wordid,dependencies in depends.items():
                    if box in dependencies:
                        response["words"][str(wordid)] = get_word(wordid, colors)
                self.broadcast(response)
    def authed(self):
        all_colors = self.get_all_colors()
        data = {
            "colors": all_colors,
            "words": dict((str(word),get_word(word, all_colors)) for word in words),
            'type': 'initialState'
        }
        self.respond(data)

    def disconnected(self):
        pass


def compute_gate(color: str, number: int, first_word: str, second_word: Optional[str]=None):
    if color == "red" and number == 1:
      return first_word[-1::-1]
    elif color == "red" and number == 2:
      return codecs.encode(first_word, 'rot_13')
    elif color == "red" and number == 3:
      return "".join(sorted(first_word))
    elif color == "blue" and number == 1:
      if first_word == '':
          return ""
      return first_word[-1]+first_word[:-1]
    elif color == "blue" and number == 2:
      if first_word == '':
          return ""
      last_letter = ord(first_word[-1]) - 64
      last_letter += 3
      last_letter %= 26
      last_letter += 1
      return first_word[:-1]+chr(last_letter+64)
    elif color == "blue" and number == 3:
      if not first_word:
          return "AY"
      return first_word[1:]+first_word[0]+"AY";
    elif color == "green" and number == 1:
      return first_word[1::2]
    elif color == "green" and number == 2:
      return first_word[1:-1]
    elif color == "green" and number == 3:
      return "".join(x for x in first_word if x not in "AIEOU")
    if second_word is None:
        return "Invalid parameters"
    if color == "blue" and number == 4:
      return "".join("".join(x) for x in itertools.zip_longest(first_word, second_word, fillvalue=''))
    elif color == "blue" and number == 5:
      return "".join(a for a,b in zip(first_word, second_word) if a==b)
    elif color == "blue" and number == 6:
      return first_word+second_word
    elif color == "red" and number == 4:
      return redfunc(first_word,second_word,operator.xor)
    elif color == "red" and number == 5:
      return redfunc(first_word,second_word,operator.and_)
    elif color == "red" and number == 6:
      return redfunc(first_word,second_word,operator.or_)
    elif color == "green" and number == 4:
        arr = [(b,a) for a,b in enumerate(second_word)]
        arr.sort()
        res = ""
        for _,i in arr:
            if i < len(first_word):
                res += first_word[i]

        return res + first_word[len(second_word):]
    elif color == "green" and number == 5:
        if second_word == '':
            return ""
        return caesar(first_word,ord(second_word[0])-64)
    elif color == "green" and number == 6:
        res = ""
        for i,ltr in enumerate(first_word):
            v = ord(ltr) - 65
            if(v < len(second_word)):
                res += second_word[v]
            else:
                res += ltr;
        return res
    return "NOT A GATE :("

def caesar(plaintext, shift):
    alphabet = string.ascii_uppercase
    shifted_alphabet = alphabet[shift:] + alphabet[:shift]
    table = str.maketrans(alphabet, shifted_alphabet)
    return plaintext.translate(table)



def letterfn(fn,a,b):
    if not (a and b):
        return a or b
    x = ord(a) - 64
    y = ord(b) - 64
    z = fn(x,y)
    if z > 0 and z < 27:
        return chr(z+64)
    else:
        return "X"
def redfunc(w1,w2,fn):
    return "".join(letterfn(fn,a,b) for a,b in itertools.zip_longest(w1,w2))

answers = ["CREATIONIST", "WATERFALL", "QUINCE", "ANTENNA", "PHASE", "SEAWATER", "NANA", "POEM", "ICE", "THEOLOGIZE", "RIA", "STORAGE", "LOVED", "RIBOSOME", "SUBPRIME", "LOBE", "BOLT", ]
def get_word(v, colors):
    word = get_word_internal(v, colors)
    try:
        if words.index(v) == answers.index(word):
            return word,"yes"
    except:
        pass
    return word,"no"


def get_word_internal(v, colors):
    if v == 25: return compute_gate(colors[19], 6, compute_gate(colors[1], 4, "SWING", "PELOSI"), compute_gate(colors[12], 4, "BOAST", compute_gate(colors[11], 1, "HAM")))
    if v == 63: return compute_gate(colors[57], 6, compute_gate(colors[44], 4, compute_gate(colors[34], 5, compute_gate(colors[33], 2, "PROMO"), "EAVES"), compute_gate(colors[43], 1, "EAVES")), compute_gate(colors[51], 6, "HAJJ", "ATLANTAFALCONS"))
    if v == 97: return compute_gate(colors[91], 6, compute_gate(colors[84], 4, "HAPPEN", "LOCCUM"), compute_gate(colors[83], 1, compute_gate(colors[79], 2, compute_gate(colors[70], 6, "IN", "TRANSALPINE"))))
    if v == 123: return compute_gate(colors[116], 4, compute_gate(colors[104], 5, compute_gate(colors[98], 6, "SAFETY", "NAMES"), "MAINTENANCE"), compute_gate(colors[110], 6, "HEN", "FAD"))
    if v == 148: return compute_gate(colors[142], 5, compute_gate(colors[137], 3, "WAXMUSEUM"), compute_gate(colors[141], 2, "OPOSSUM"))
    if v == 176: return compute_gate(colors[169], 4, compute_gate(colors[162], 1, compute_gate(colors[158], 1, compute_gate(colors[149], 5, compute_gate(colors[141], 2, "OPOSSUM"), "RAVENERS"))), compute_gate(colors[163], 6, "AWED", "EXERTION"))
    if v == 220: return compute_gate(colors[219], 2, compute_gate(colors[215], 3, compute_gate(colors[206], 5, compute_gate(colors[199], 4, "ENSNARE", "WHERE"), "ORNAMENTAL")))
    if v == 246: return compute_gate(colors[239], 4, compute_gate(colors[238], 2, compute_gate(colors[229], 6, "REOPEN", compute_gate(colors[228], 1, "REPAIR"))), "SHAKESPEARE")
    if v == 266: return compute_gate(colors[265], 1, compute_gate(colors[261], 2, compute_gate(colors[257], 3, "ALICE")))
    if v == 296: return compute_gate(colors[290], 6, compute_gate(colors[284], 6, "THE", compute_gate(colors[271], 4, "LOGO", "FARM")), compute_gate(colors[278], 5, compute_gate(colors[270], 3, "CITY"), "FARM"))
    if v == 327: return compute_gate(colors[326], 2, compute_gate(colors[322], 2, compute_gate(colors[318], 2, compute_gate(colors[314], 2, compute_gate(colors[310], 2, "PARATRIATHLON")))))
    if v == 366: return compute_gate(colors[365], 1, compute_gate(colors[356], 6, compute_gate(colors[349], 2, "STOP"), compute_gate(colors[350], 6, "BEACH", "GRENADES")))
    if v == 390: return compute_gate(colors[384], 6, compute_gate(colors[376], 1, compute_gate(colors[367], 6, "OHIO", "SPREAD")), compute_gate(colors[377], 4, "CLUNK", "GECKO"))
    if v == 428: return compute_gate(colors[427], 1, compute_gate(colors[417], 4, compute_gate(colors[409], 1, "SEROTONIN"), compute_gate(colors[410], 4, "IAMB", "DROP")))
    if v == 454: return compute_gate(colors[448], 6, compute_gate(colors[440], 1, "BUS"), compute_gate(colors[441], 4, compute_gate(colors[436], 3, compute_gate(colors[432], 2, "KVETCHY")), "SWAYS"))
    if v == 479: return compute_gate(colors[478], 2, compute_gate(colors[474], 2, compute_gate(colors[470], 3, compute_gate(colors[461], 6, "DICE", "MELBOURNE"))))
    if v == 516: return compute_gate(colors[509], 4, compute_gate(colors[502], 2, compute_gate(colors[494], 2, "MAUL")), compute_gate(colors[503], 6, compute_gate(colors[498], 1, "HOTFIXES"), "CLAY"))
    return "Invalid v."
