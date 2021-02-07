from django.db import models
from django.http import HttpResponse
from spoilr.decorators import *
from spoilr.models import *
from spoilr.puzzle_session import *
import pytz
import datetime
import math
from typing import List, Tuple

# collects statements, returns an array of tuples.
# each tuple is a string (the statement), a bool (Truthiness of statement),
# and another bool (is_code; always False)
def get_statements(team) -> List[Tuple[str,bool,bool]]:
  statement_functions = [
    max_guesses_statement,
    max_hints_statement,
    bingo_unlocked_statement,
    first_puzzle_solve_time_statement,
    first_meta_solve_time_statement
  ]
  statements = []
  fc = 0
  for func in statement_functions:
    fc += 1
    statement = func(team)
    if statement:
      statements.append(statement)
  return statements

def num_max_guesses(team):
  max_guesses = 0 # Unraveling the Mystery begins with 9 "fake" guesses.
  # TODO: optimizeme
  puzzleCounts = {}
  for s in PuzzleSubmission.objects.filter(team=team):
    id = s.puzzle.id
    if id not in puzzleCounts:
      puzzleCounts[id] = 0
    puzzleCounts[id] += 1
    if puzzleCounts[id] > max_guesses:
      max_guesses = puzzleCounts[id]
  return max_guesses

def max_guesses_statement(team):
  return ("Made more than {} guesses on a single puzzle.".format(num_max_guesses(team) - 1), True, False)

def num_max_hints(team):
  max_hints = 0
  puzzleCounts = {}
  for s in HintSubmission.objects.filter(team=team):
    id = s.puzzle.id
    if id not in puzzleCounts:
      puzzleCounts[id] = 0
    puzzleCounts[id] += 1
    if puzzleCounts[id] > max_hints:
      max_hints = puzzleCounts[id]

  for puzzle in Puzzle.objects.exclude(round__url='infinite'):
    count = HintSubmission.objects.filter(team=team, puzzle=puzzle).count()
    if count > max_hints:
      max_hints = count
  return max_hints

def max_hints_statement(team):
  return ("Requested at least three hints on one puzzle.", True, False) if num_max_hints(team) > 3 else None

def bingo_unlocked_time(team):
  return PuzzleAccess.objects.get(team=team, puzzle__name="Bingo").timestamp

def bingo_unlocked_statement(team):
  if bingo_unlocked_time(team) < datetime.datetime(2021, 1, 16, 18, tzinfo=pytz.timezone('US/Eastern')):
    return ("This puzzle unlocked before 6pm EST Saturday.", True, False)
  return None

def first_puzzle_solve_time(team):
  for access in PuzzleAccess.objects.filter(team=team, solved_time__isnull=False).order_by("solved_time"):
    return (access.solved_time - access.found_timestamp)

def first_puzzle_solve_time_statement(team):
  first_time = first_puzzle_solve_time(team)
  value = (first_time and (first_time < datetime.timedelta(minutes=10)))
  return ("Solved our first puzzle within the first 10 minutes of hunt.", value, False)

def first_meta_solve_time(team):
  min_time = None
  min_access = None
  for access in PuzzleAccess.objects.filter(team=team, puzzle__is_meta=True, solved_time__isnull=False):
    if min_time == None or access.solved_time < min_time:
        min_time = access.solved_time
        min_access = access
  if min_time and min_access:
      return (min_time - min_access.found_timestamp)
  else:
      return None

def first_meta_solve_time_statement(team):
  first_time = first_meta_solve_time(team)
  value = first_time and (first_time < datetime.timedelta(hours=1))
  return ("Solved our first meta within an hour of unlocking it.", value, False)
