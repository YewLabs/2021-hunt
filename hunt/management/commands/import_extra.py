from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import csv
import glob
import json
import os
import shutil

import spoilr.actions
from spoilr.models import *
from hunt.actions import *
from hunt.models import *

from hunt.special_puzzles.counting import extra as counting_extra

STUDENTS_PATH = '2021-hunt/data/students.tsv'
INTERACTIONS_PATH = '2021-hunt/data/interactions.tsv'

def setup_checkins(interaction):
    pass

def import_extra():
    PuzzleExtraData.objects.all().delete()
    extraPaths = glob.glob(os.path.join(settings.PUZZLE_DATA, '*', 'extra.json'))
    for ePath in extraPaths:
        with open(ePath) as f:
            j = json.load(f)
            mPath = ePath.replace('extra.json', 'metadata.json')
            with open(mPath) as mf:
                mj = json.load(mf)
                try:
                    puzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=mj['puzzle_idea_id'])
                    for k, v in j.items():
                        PuzzleExtraData(puzzle=puzzle, name=k, data=v).save()
                except:
                    print('Unknown puzzle: %d' % (mj['puzzle_idea_id']))

    with open(STUDENTS_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for studentInfo in reader:
            if len(studentInfo) == 0:
                continue
            puzzle = Puzzle.objects.filter(answer=studentInfo[0]).first()
            PuzzleExtraData(puzzle=puzzle, name='npc_name', data=studentInfo[1].strip()).save()
            PuzzleExtraData(puzzle=puzzle, name='dorm', data=studentInfo[2].strip()).save()
            PuzzleExtraData(puzzle=puzzle, name='clubs', data=studentInfo[3].strip()).save()

    counting_extra.load_trivia()

    teams = Team.objects.all()

    Interaction.objects.all().delete()
    with open(INTERACTIONS_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for iInfo in reader:
            if len(iInfo) == 0:
                continue
            interaction = Interaction()
            interaction.url = iInfo[0]
            interaction.name = iInfo[1]
            interaction.order = iInfo[2]
            if iInfo[3] == '1':
                interaction.show_team = True
            if len(iInfo[4]):
                interaction.puzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=iInfo[4])
            interaction.unlock_type = iInfo[5].upper().strip()
            if len(iInfo) > 6 and len(iInfo[6]):
                interaction.email_key = iInfo[6]
            if len(iInfo) > 7 and len(iInfo[7]):
                interaction.message_template = iInfo[7]
            interaction.save()
            utime = datetime.datetime.fromtimestamp(settings.UNLOCK_TIME, tz=datetime.timezone.utc)
            if interaction.unlock_type == 'TIME':
                for t in teams:
                    InteractionAccess.objects.create(team=t, interaction=interaction, timestamp=utime)



class Command(BaseCommand):
    help = """Import Puzzle Extras."""

    def handle(self, *args, **options):
        import_extra()
