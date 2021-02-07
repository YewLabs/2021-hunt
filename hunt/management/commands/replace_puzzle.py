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

@transaction.atomic
def replace_puzzle(original, replacement, replace_title=False):
    try:
        opuzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=original)
        rpuzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=replacement)
    except Puzzle.DoesNotExist:
        print("Unknown puzzles.")
        return
    print("Replacing '%s' with '%s'" % (opuzzle.name, rpuzzle.name))
    print("Enter 'REPLACE' to replace.")
    confirm = input('>')
    if confirm != 'REPLACE':
        print("Cancelling replacement")
        return

    round = opuzzle.round
    order = opuzzle.order
    name = opuzzle.name

    tmpPuzzle = Puzzle.objects.create(round=rpuzzle.round, order=12345, url='tmp-puzzle', name='Tmp Puzzle')
    o21 = opuzzle.y2021puzzledata
    r21 = rpuzzle.y2021puzzledata
    o21.puzzle = tmpPuzzle
    r21.puzzle = opuzzle
    o21.save()
    r21.save()

    o21.puzzle = rpuzzle
    o21.save()
    tmpPuzzle.delete()

    opuzzle.round = rpuzzle.round
    opuzzle.name += ' - REPLACED'
    opuzzle.order = rpuzzle.order + 100
    opuzzle.save()

    rpuzzle.round = round
    rpuzzle.answer = opuzzle.answer
    rpuzzle.order = order
    if replace_title:
        rpuzzle.name = name
    rpuzzle.save()

    for pa in PuzzleAccess.objects.filter(puzzle=rpuzzle):
        pa.delete()

    for pa in PuzzleAccess.objects.filter(puzzle=opuzzle):
        pa.puzzle = rpuzzle
        pa.save()

    print('Replaced.')

class Command(BaseCommand):
    help = """Replace Puzzle."""

    def add_arguments(self, parser):
        parser.add_argument('old', type=int, help='The old puzzle to replace')
        parser.add_argument('new', type=int, help='The new puzzle to replace')
        parser.add_argument('--keep-title', dest='keepTitle', action='store_true')
        parser.set_defaults(keepTitle=False)

    def handle(self, *args, **options):
        original = options['old']
        replacement = options['new']
        keepTitle = options['keepTitle']
        replace_puzzle(original, replacement, keepTitle)
