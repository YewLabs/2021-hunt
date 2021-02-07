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

ROUNDS_PATH = '2021-hunt/data/rounds.tsv'
PUZZLES_PATH = '2021-hunt/data/puzzles.tsv'
INFINITE_PATH = '2021-hunt/data/infinite.tsv'

def valid(pi, index):
    return len(pi) > index and len(pi[index]) and pi[index] != 'X'

def import_puzzles():
    call_command('check_puzzles')

    from spoilr.signals_register import subscriptions
    subscriptions.clear()

    Y2021Settings.objects.filter(name__in=['reveal_nano', 'prelaunched', 'is_it_hunt_yet', 'mmo_disabled']).delete()

    Round.objects.all().delete()
    Puzzle.objects.all().delete()
    rounds = {}
    with open(ROUNDS_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for roundInfo in reader:
            if len(roundInfo) == 0:
                continue
            round = Round()
            round.url = roundInfo[0]
            round.name = roundInfo[1]
            round.order = roundInfo[3]
            round.save()
            rounds[round.url] = round
            round2021 = Y2021RoundData()
            round2021.round = round
            round2021.tempest_id = roundInfo[2]
            round2021.round_points_granted = float(roundInfo[4])
            round2021.outer_points_granted = float(roundInfo[5])
            round2021.points_required = float(roundInfo[6])
            round2021.save()

    puzzlePaths = glob.glob(os.path.join(settings.PUZZLE_DATA, '*', 'metadata.json'))
    puzzleMetadata = {}
    for pPath in puzzlePaths:
        with open(pPath) as f:
            j = json.load(f)
            puzzleMetadata[str(j['puzzle_idea_id'])] = j

    puzzles = {}

    teams = list(Team.objects.all())

    with open(PUZZLES_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for puzzleInfo in reader:
            if len(puzzleInfo) == 0:
                continue
            if puzzleInfo[1] not in puzzleMetadata:
                print('Unknown Puzzle ID: %s' % (puzzleInfo[1]))
                continue
            metadata = puzzleMetadata[puzzleInfo[1]]
            puzzle = Puzzle()
            puzzle.round = rounds[puzzleInfo[0]]
            puzzle.url = metadata['puzzle_slug']
            puzzle.name = metadata['puzzle_title']
            puzzle.answer = metadata['answer']
            puzzle.credits = metadata['credits']
            puzzle.order = puzzleInfo[2]
            if len(puzzleInfo) > 4 and puzzleInfo[4] == '1':
                puzzle.is_meta = True
            puzzle.save()
            puzzles[metadata['puzzle_idea_id']] = puzzle
            puzzle2021 = Y2021PuzzleData()
            puzzle2021.puzzle = puzzle
            puzzle2021.tempest_id = metadata['puzzle_idea_id']
            puzzle2021.obfuscated_id = obfuscate(puzzle2021.tempest_id)
            if valid(puzzleInfo, 3):
                pr = float(puzzleInfo[3])
                puzzle2021.points_req = pr
            if valid(puzzleInfo, 6):
                fr = float(puzzleInfo[6])
                puzzle2021.feeder_req = fr
            if valid(puzzleInfo, 5):
                puzzle2021.feeder_tag = puzzleInfo[5]
            if valid(puzzleInfo, 7):
                lvl = int(puzzleInfo[7])
                puzzle2021.level = lvl
            if valid(puzzleInfo, 8):
                required_puzzle = int(puzzleInfo[8])
                if required_puzzle not in puzzles:
                    print('Required puzzle %d must appear earlier.' % (required_puzzle))
                puzzle2021.required_available_puzzle = puzzles[required_puzzle]
            if valid(puzzleInfo, 9):
                if puzzleInfo[9].startswith('T+'):
                    puzzle2021.unlock_time = datetime.datetime.fromtimestamp(settings.START_TIME, tz=datetime.timezone.utc) + datetime.timedelta(hours=float(puzzleInfo[9][2:]))
                else:
                    time = int(puzzleInfo[9])
                    puzzle2021.unlock_time = datetime.datetime.fromtimestamp(time, tz=datetime.timezone.utc)
            if valid(puzzleInfo, 11):
                puzzle2021.hint_stuck_duration = datetime.timedelta(hours=float(puzzleInfo[11]))
            if valid(puzzleInfo, 12):
                puzzle2021.unlock_req = puzzleInfo[12]
            puzzle2021.save()
            if 'pseudo' in metadata:
                for k, v in metadata['pseudo'].items():
                    PseudoAnswer(puzzle=puzzle, answer=k, response=v).save()
            if len(puzzleInfo) > 10 and puzzleInfo[10] == '1':
                for team in teams:
                    PuzzleAccess.objects.create(team=team, puzzle=puzzle, found=True, solved=True)
    call_command('import_extra')

class Command(BaseCommand):
    help = """Import puzzles."""

    def handle(self, *args, **options):
        import_puzzles()
