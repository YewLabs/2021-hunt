from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import re
import csv
import glob
import json
import os
import shutil

import spoilr.actions
from spoilr.models import *
from hunt.models import *
# slug, title, answer,
DUMMY_PUZZLES = [
["FASTIDIOUS", "Witch One?", "east-campus"],
]

@transaction.atomic
def import_dummy():
    order = 35
    scRound = Round.objects.get(url='students')
    team = Team.objects.get(y2021teamdata__tempest_id=3)
    for p in DUMMY_PUZZLES:
        default_slug = re.sub(
            r'[<>#%\'"|{}\[\])(\\\^?=`;@&,]',
            "",
            re.sub(r"[ \/]+", "-", p[1],
        ).lower())
        try:
            puzzle = Puzzle.objects.get(url=default_slug)
        except:
            puzzle = Puzzle()
        puzzle.round = scRound
        puzzle.url = default_slug
        puzzle.name = p[1]
        puzzle.answer = p[0]
        puzzle.credits = '[Redacted]'
        puzzle.order = order
        puzzle.is_meta = False
        puzzle.save()
        try:
            puzzle2021 = Y2021PuzzleData.objects.get(tempest_id = 4200+order)
        except:
            puzzle2021 = Y2021PuzzleData()
        puzzle2021.puzzle = puzzle
        puzzle2021.tempest_id = 4200 + order
        puzzle2021.point_req = None
        puzzle2021.feeder_req = None
        puzzle2021.feeder_tag = p[2]
        puzzle2021.save()
        spoilr.actions.release_puzzle(team, puzzle)
        spoilr.actions.find_puzzle(team, puzzle)
        order += 1

class Command(BaseCommand):
    help = """Import dummy puzzles."""

    def handle(self, *args, **options):
        import_dummy()
