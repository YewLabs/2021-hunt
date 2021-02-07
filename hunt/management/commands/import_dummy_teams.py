from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import csv
import hashlib
import json
import os
import shutil

from spoilr.models import *
from hunt.models import *
import spoilr.signals as signals
from spoilr.actions import release_puzzle, find_puzzle, solve_puzzle, clear_cache
from hunt.actions import unlock_puzzles

@transaction.atomic
def import_dummy_teams():
    from spoilr.signals_register import subscriptions
    subscriptions.clear()

    intro_meta = Puzzle.objects.get(y2021puzzledata__tempest_id=288)
    for i in range(20):
        print(i)
        Team.objects.filter(url='test%d' % (i + 1)).delete()
        team = Team()
        team.url = 'test%d' % (i + 1)
        team.username = team.url
        team.name = 'Test %d' % (i + 1)
        team.password = 'password'
        team.email = 'IGNORE'
        team.size_desc = 10
        team.save()
        team2021 = Y2021TeamData()
        team2021.team = team
        team2021.tempest_id = 100 + i + 1
        team2021.auth = hashlib.sha256(('token:%s:%s' % (team.username, team.password)).encode('utf-8')).hexdigest()
        try:
            team2021.emoji = 'https://perpendicular.institute/static/team_emoji/test.png'
        except:
            pass
        team2021.save()
        release_puzzle(team, intro_meta)
        find_puzzle(team, intro_meta)
        solve_puzzle(team, intro_meta)
        #unlock_puzzles(team)
        #clear_cache(team)

class Command(BaseCommand):
    help = """Import dummy teams."""

    def handle(self, *args, **options):
        import_dummy_teams()
