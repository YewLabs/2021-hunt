from django import template
import spoilr.models as smodels
import hunt.models as hmodels
from django.db.models import Q

import datetime

register = template.Library()

@register.filter
def interactionCheck(interactions, islug):
    if not interactions:
        return False
    return interactions.filter(interaction__url=islug).exists()

@register.filter
def metaSolveCheck(solvedMetas, pslug):
    try:
        return solvedMetas.filter(url=pslug).exists()
    except solvedMetas.DoesNotExist:
        print('ERROR: no meta %s' % pslug)
        raise

@register.filter
def safeAnswer(team, pslug):
    try:
        return team.solved_puzzles.get(url=pslug).answer
    except smodels.Puzzle.DoesNotExist:
        return "ERROR (you should not see this, contact HQ if you do)"

@register.filter
def minutesAvailable(puzzle, duration):
    dt = smodels.now() - puzzle['found_time']
    return dt > datetime.timedelta(minutes=duration)

@register.filter
def minutesRemaining(puzzle, duration):
    dt = datetime.timedelta(minutes=duration) + puzzle['found_time'] - smodels.now()
    return int(dt.total_seconds() / 60)
