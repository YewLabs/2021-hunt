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

@require_puzzle_access
def puzzle281_solve(request, iid):
    p = get_infinite(iid)

    grid_str = request.GET.get('grid', '')
    words_str = request.GET.get('words', '')

    grid_str = grid_str.upper().strip()
    words_str = words_str.upper().strip()

    grid = [infinite_wordsearch.filter_non_alpha(row) for row in grid_str.split('\n')]
    words = [infinite_wordsearch.filter_non_alpha(word) for word in words_str.split('\n')]

    print(p, grid, words)
    return HttpResponse(infinite_wordsearch.check_puzzle(p, grid, words), content_type="text/plain")

@require_puzzle_access
def puzzle281_lookup(request):
    print(request)
    word = request.GET.get('word', '')
    return HttpResponse(infinite_wordsearch.lookup(word), content_type="text/plain")