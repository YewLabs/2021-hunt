from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import csv
import json
import os
import shutil

from spoilr.models import *
from hunt.models import *

@transaction.atomic
def reset_log():
    SystemLog.objects.all().delete()
    TeamLog.objects.all().delete()
    for y in Y2021Settings.objects.all():
        if y.name != 'mmo_version':
            y.delete()

class Command(BaseCommand):
    help = """Clear logs."""

    def handle(self, *args, **options):
        reset_log()
