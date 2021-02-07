from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import csv
import glob
import json
import os
import shutil

from spoilr.models import *
from hunt.models import *

UNLOCKS_PATH = '2021-hunt/data/unlocks.tsv'

@transaction.atomic
def import_unlocks():
    from spoilr.signals_register import subscriptions
    subscriptions.clear()

    hunt.models.SKIP_UNLOCK_SAVE = True

    MMOUnlock.objects.all().delete()
    with open(UNLOCKS_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for unlockInfo in reader:
            if len(unlockInfo) == 0:
                continue
            unlock = MMOUnlock()
            unlock.unlock_id = unlockInfo[0]
            if len(unlockInfo) > 1 and unlockInfo[1]:
                unlock.description = unlockInfo[1]
            if len(unlockInfo) > 2 and unlockInfo[2]:
                try:
                    unlock.puzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=int(unlockInfo[2]))
                except:
                    print('Unknown puzzle: %d' % (int(unlockInfo[2])))
            if len(unlockInfo) > 3 and unlockInfo[3]:
                unlock.round = Round.objects.get(y2021rounddata__tempest_id=int(unlockInfo[3]))
            if len(unlockInfo) > 4 and unlockInfo[4]:
                unlock.juice = int(unlockInfo[4])
            if len(unlockInfo) > 5 and unlockInfo[5]:
                unlock.interaction = Interaction.objects.get(url=unlockInfo[5])
            if len(unlockInfo) > 6 and unlockInfo[6]:
                unlock.force = unlockInfo[6]
            unlock.save()

class Command(BaseCommand):
    help = """Import unlocks."""

    def handle(self, *args, **options):
        import_unlocks()
