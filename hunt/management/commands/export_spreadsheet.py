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
UNLOCKS_PATH = '2021-hunt/data/unlocks.tsv'

def export_spreadsheet():
    puzzles = {}
    round_lookup = {}
    gate_lookup = {}

    ids_in_hunt = set()
    with open(PUZZLES_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for puzzleInfo in reader:
            if len(puzzleInfo) == 0:
                continue
            pid = puzzleInfo[1]
            ids_in_hunt.add(pid)
            if len(puzzleInfo) > 5:
                round_lookup[pid] = puzzleInfo[5]
                if puzzleInfo[3].isdigit():
                    gate_lookup[pid] = puzzleInfo[3] + " JUICE"
                elif len(puzzleInfo) > 6 and puzzleInfo[6].isdigit():
                    gate_lookup[pid] = puzzleInfo[6] + " puzzles"
                elif len(puzzleInfo) > 9 and puzzleInfo[9]:
                    gate_lookup[pid] = puzzleInfo[9]
                else:
                    gate_lookup[pid] = ''
            else:
                round_lookup[pid] = puzzleInfo[0]
                gate_lookup[pid] = ''

    puzzlePaths = glob.glob(os.path.join(settings.PUZZLE_DATA, '*', 'metadata.json'))
    puzzleMetadata = {}
    for pPath in puzzlePaths:
        with open(pPath) as f:
            j = json.load(f)
            pid = str(j['puzzle_idea_id'])
            if pid in ids_in_hunt:
                puzzles[pid] = [gate_lookup[pid], j['puzzle_title'], round_lookup[pid], j['credits'], j['answer']]

    with open(UNLOCKS_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for unlockInfo in reader:
            if len(unlockInfo) < 2:
                continue
            pid = unlockInfo[2] if len(unlockInfo) > 2 else ''
            name = unlockInfo[0]
            location = unlockInfo[1]
            puzzleRow = puzzles.get(pid, [''] * 6)
            if puzzleRow[0] == '':
                if len(unlockInfo) > 4 and unlockInfo[4]:
                    puzzleRow[0] = unlockInfo[4] + " JUICE"
                elif len(unlockInfo) > 5 and unlockInfo[5]:
                    puzzleRow[0] = unlockInfo[5]
            print('\t'.join([pid, name, location] + puzzleRow))
            if pid in ids_in_hunt:
                ids_in_hunt.remove(pid)

    ids_in_hunt = sorted(list(ids_in_hunt), key = lambda pid : (puzzles[pid][2], puzzles[pid][0]))
    for pid in ids_in_hunt:
        print('\t'.join([pid, '----', '----'] + puzzles[pid]))


class Command(BaseCommand):
    help = """Export a spreadsheet of unlock and puzzle data."""

    def handle(self, *args, **options):
        export_spreadsheet()
