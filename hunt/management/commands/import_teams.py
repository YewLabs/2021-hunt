from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import csv
import hashlib
import json
import os
import shutil

from spoilr.models import *
from hunt.models import *

TEAMS_PATH = '2021-hunt/data/teams.tsv'

def import_teams():
    JuiceBox.objects.all().delete()
    Team.objects.all().delete()
    with open(TEAMS_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for teamInfo in reader:
            if len(teamInfo) == 0:
                continue
            team = Team()
            team.url = teamInfo[1]
            team.username = teamInfo[1]
            team.name = teamInfo[2]
            team.password = teamInfo[3]
            team.email = teamInfo[4]
            team.phone = teamInfo[6]
            team.size_desc = teamInfo[7]
            if len(teamInfo) > 8 and teamInfo[8] == '1':
                team.is_admin = True
            if len(teamInfo) > 8 and teamInfo[8] == '2':
                team.is_special = True
            team.save()
            team2021 = Y2021TeamData()
            team2021.team = team
            team2021.tempest_id = teamInfo[0]
            team2021.auth = hashlib.sha256(('token:%s:%s' % (team.username, team.password)).encode('utf-8')).hexdigest()
            if not os.path.exists('2021-hunt/static/team_emoji/%s.png' % (team.url)):
                print("Emoji for %s missing." % (team.url))
            team2021.emoji = 'https://%s/static/team_emoji/%s.png' % (settings.DEFAULT_DOMAIN, team.url)
            team2021.save()

class Command(BaseCommand):
    help = """Import teams."""

    def handle(self, *args, **options):
        import_teams()
