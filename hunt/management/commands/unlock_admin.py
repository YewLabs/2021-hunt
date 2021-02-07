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
import hunt.mmo_unlock as mu
import hunt.constants

def unlock_admin():
    from spoilr.signals_register import subscriptions
    subscriptions.clear()

    hunt.constants.SKIP_UNLOCK_SAVE = True
    hunt.constants.SKIP_UNLOCK_LOG = True

    team1 = Team.objects.get(y2021teamdata__tempest_id=0)
    team2 = Team.objects.get(y2021teamdata__tempest_id=1)
    team3 = Team.objects.get(y2021teamdata__tempest_id=6)
    #teamA = Team.objects.get(y2021teamdata__tempest_id=231)
    #teamB = Team.objects.get(y2021teamdata__tempest_id=232)
    #teamC = Team.objects.get(y2021teamdata__tempest_id=233)
    #teamD = Team.objects.get(y2021teamdata__tempest_id=234)
    #teamE = Team.objects.get(y2021teamdata__tempest_id=235)

    teams = [team1, team2, team3]
    for t in teams:
        start_team(t)
    for round in Round.objects.all():
        for team in teams:
            spoilr.actions.release_round(team, round)
    for puzzle in Puzzle.objects.exclude(round__url='infinite'):
        if puzzle.y2021puzzledata.infinite:
            continue
        for team in teams:
            spoilr.actions.release_puzzle(team, puzzle)
            spoilr.actions.find_puzzle(team, puzzle)
    try:
        puzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=INFINITE_META)
        for team in teams:
            spoilr.actions.release_puzzle(team, puzzle)
            spoilr.actions.find_puzzle(team, puzzle)
    except:
        pass
    for t in teams:
        mu.get_global_team_state(t)

class Command(BaseCommand):
    help = """Unlock Admin."""

    def handle(self, *args, **options):
        unlock_admin()
