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


SCHEDULE_PATH = '2021-hunt/data/schedule.tsv'
BOXES_PATH = '2021-hunt/data/juiceboxes.tsv'

def valid(pi, index):
    return len(pi) > index and len(pi[index]) and pi[index] != 'X'

def import_infusions():
    JuiceSchedule.objects.all().delete()
    JuiceBox.objects.all().delete()

    with open(SCHEDULE_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for scheduleInfo in reader:
            if len(scheduleInfo) == 0:
                continue

            schedule = JuiceSchedule()
            if scheduleInfo[0].startswith('T+'):
                schedule.timestamp = datetime.datetime.fromtimestamp(settings.START_TIME, tz=datetime.timezone.utc) + datetime.timedelta(hours=float(scheduleInfo[0][2:]))
            else:
                time = int(scheduleInfo[0])
                schedule.timestamp = datetime.datetime.fromtimestamp(time, tz=datetime.timezone.utc)
            if valid(scheduleInfo, 1):
                schedule.active = True
            if valid(scheduleInfo, 2):
                schedule.students_juice = float(scheduleInfo[2])
            if valid(scheduleInfo, 3):
                schedule.green_juice = float(scheduleInfo[3])
            if valid(scheduleInfo, 4):
                schedule.infinite_juice = float(scheduleInfo[4])
            if valid(scheduleInfo, 5):
                schedule.nano_juice = float(scheduleInfo[5])
            if valid(scheduleInfo, 6):
                schedule.stata_juice = float(scheduleInfo[6])
            if valid(scheduleInfo, 7):
                schedule.clusters_juice = float(scheduleInfo[7])
            if valid(scheduleInfo, 8):
                schedule.tunnels_juice = float(scheduleInfo[8])
            schedule.save()

    with open(BOXES_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for boxInfo in reader:
            if len(boxInfo) == 0:
                continue

            box = JuiceBox()
            if valid(boxInfo, 0):
                if boxInfo[0].startswith('T+'):
                    box.unlock_time = datetime.datetime.fromtimestamp(settings.START_TIME, tz=datetime.timezone.utc) + datetime.timedelta(hours=float(boxInfo[0][2:]))
                else:
                    time = int(boxInfo[0])
                    box.unlock_time = datetime.datetime.fromtimestamp(time, tz=datetime.timezone.utc)
            if valid(boxInfo, 1):
                box.active = True
            if valid(boxInfo, 2):
                box.round = Round.objects.get(y2021rounddata__tempest_id=int(boxInfo[2]))
            if valid(boxInfo, 3):
                box.juice = float(boxInfo[3])
            if valid(boxInfo, 4):
                box.team = Team.objects.get(y2021teamdata__tempest_id=int(boxInfo[4]))
            box.save()

class Command(BaseCommand):
    help = """Import infusions."""

    def handle(self, *args, **options):
        import_infusions()
