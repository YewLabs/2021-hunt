from django.db import models
from django.http import HttpResponse
from spoilr.models import *
from spoilr.puzzle_session import *

import base64
import datetime
import json
import time

from hunt.actions import get_infinite

import hunt.special_puzzles.make_your_own_wordsearch.generator as infinite_wordsearch


LUGE_TRACKS = [
    ['LRLRLRRLLR'],
    ['LLRLLLRLRL'],
    ['LRRLRLRLRR',
     'LRRLRLRRRR',
     'LRRLRLRRRL'],
]


def puzzle271_check(request):
    index = int(request.GET.get('index', 0))
    check_str = request.GET.get('path', '')
    resp = HttpResponse(
        check_str.upper() in LUGE_TRACKS[index]
    )
    resp['Access-Control-Allow-Headers'] = '*'
    resp['Access-Control-Allow-Origin'] = '*'
    return resp


def puzzle271_final_scene(request):
    resp = HttpResponse(_puzzle271_final_scene(request))
    resp['Access-Control-Allow-Headers'] = '*'
    resp['Access-Control-Allow-Origin'] = '*'
    return resp

def _puzzle271_final_scene(request):
    check_dict = request.GET.get('answers', '')
    check_dict = json.loads(check_dict)
    if 'h' in check_dict:
        # Haxe implementation detail
        check_dict = check_dict['h']

    ERROR_MSG = 'Error loading final scene! Contact Galactic Trendsetters for help!'
    for i in [0, 1, 2]:
        if str(i) not in check_dict:
            return ERROR_MSG
        if check_dict[str(i)] not in LUGE_TRACKS[i]:
            return ERROR_MSG

    return str(open('2021-hunt/hunt/special_puzzles/love_at_150_km_h/finale.txt', 'r').read())
