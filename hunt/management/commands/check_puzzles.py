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

PUZZLES_PATH = '2021-hunt/data/puzzles.tsv'

def check_puzzles():
    puzzles = {}
    duplicates = []
    unused = []
    unknown = []

    puzzlePaths = glob.glob(os.path.join(settings.PUZZLE_DATA, '*', 'metadata.json'))
    puzzleMetadata = {}
    for pPath in puzzlePaths:
        with open(pPath) as f:
            j = json.load(f)
            tid = str(j['puzzle_idea_id'])
            if tid not in puzzles:
                puzzles[tid] = []
            puzzles[tid].append(j['puzzle_slug'])
            if len(puzzles[tid]) > 1 and tid not in duplicates:
                duplicates.append(tid)
    unused = list(puzzles.keys())

    with open(PUZZLES_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for puzzleInfo in reader:
            if len(puzzleInfo) == 0:
                continue
            if puzzleInfo[1] not in puzzles.keys():
                unknown.append(puzzleInfo[1])
            if puzzleInfo[1] in unused:
                unused.remove(puzzleInfo[1])

    if len(duplicates) > 0:
        print('Duplicates:')
        for d in duplicates:
            print('%s: %s' % (d, ','.join(puzzles[d])))

    if len(unknown) > 0:
        print('Unknown:')
        for d in unknown:
            print('%s' % (d))

    if len(unused) > 0:
        print('Unused:\n')
        for d in unused:
            print('%s: %s' % (d, ','.join(puzzles[d])))


class Command(BaseCommand):
    help = """Check puzzles."""

    def handle(self, *args, **options):
        check_puzzles()
