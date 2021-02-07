from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction


import csv
import datetime
import glob
import json
import os

from spoilr.models import Puzzle, PuzzleAccess, Team, PseudoAnswer, Round
from hunt.models import *

INFINITE_PATH = '2021-hunt/data/infinite.tsv'

def valid(pi, index):
    return len(pi) > index and len(pi[index]) and pi[index] != 'X'

def import_infinite():
    Puzzle.objects.filter(round__url='infinite', is_meta=False).delete()
    puzzles = {}
    for p in Puzzle.objects.filter(round__url='infinite-template'):
        puzzles[p.y2021puzzledata.tempest_id] = p
    infiniteRound = Round.objects.get(url='infinite')
    with open(INFINITE_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        count = 0
        for puzzleInfo in reader:
            count += 1
            if count % 100 == 0:
                print("Infinite %d/100000" % (count))
            if len(puzzleInfo) == 0:
                continue
            if int(puzzleInfo[1]) not in puzzles:
                err = 'Unknown Puzzle ID: %s' % (puzzleInfo[1])
                if str(puzzleInfo[1]) == '999':
                    err += ' (Ignore this)'
                print(err)
                continue
            parent = puzzles[int(puzzleInfo[1])]
            puzzle = Puzzle()
            puzzle.round = infiniteRound
            puzzle.url = 'infinite-%d' % (int(puzzleInfo[0]))
            puzzle.name = 'Puzzle %d: %s' % (int(puzzleInfo[0]), parent.name)
            puzzle.answer = puzzleInfo[2]
            puzzle.credits = parent.credits
            puzzle.order = int(puzzleInfo[0])
            puzzle.is_meta = False
            puzzle.save()
            puzzle2021 = Y2021PuzzleData()
            puzzle2021.puzzle = puzzle
            puzzle2021.tempest_id = 42000000 + int(puzzleInfo[0])
            puzzle2021.obfuscated_id = obfuscate(puzzle2021.tempest_id)
            puzzle2021.infinite = True
            puzzle2021.parent = parent
            puzzle2021.save()

class Command(BaseCommand):
    help = """Import infinite."""

    def handle(self, *args, **options):
        import_infinite()
