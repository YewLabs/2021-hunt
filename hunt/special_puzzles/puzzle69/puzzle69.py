import random
import os
import sys
import copy
import json
from typing import List
from pathlib import Path
from django.http import JsonResponse
from google.cloud import storage
from spoilr.decorators import *

from .team_specific import get_statements

VERSION = 2

def generate_boards(team):
  f = open(Path(__file__).parent / "statements.tsv", 'r')
  statements = f.read()
  statements = statements.split("\n")
  falsecode = []
  truecode = []
  falsedata = []
  truedata = []
  oldSeed = random.random()
  random.seed(5)
  for i in statements:
    x = i.split("\t")
    if len(x) == 2:
      statement, bools = x
      code = False
    elif len(x) == 3:
      statement, bools, codest = x
      code = codest != ''
    else:
      continue
    if code or random.randint(0,6) <= 1:
      if "T" in bools:
        truecode.append(statement)
      else:
        falsecode.append(statement)
    else:
      if "T" in bools:
        truedata.append(statement)
      else:
        falsedata.append(statement)
  for statement,val,code in get_statements(team):
    if code:
      if val:
        truecode.append(statement)
      else:
        falsecode.append(statement)
    else:
      if val:
        truedata.append(statement)
      else:
        falsedata.append(statement)

  # print([len(x) for x in [truecode, falsecode, truedata, falsedata]])
  board = 'x.,x.,x.,x.,x.,x.,x.,x,.,.,,.,,.,,.,.,x,x.,x.,x.,x.,x.,x.,x.,x.,x,x,x,x,x,x.,x,.,.,,.,,.,,.,,x,x.,x,x,x,x,x,x.,x.,x,x.,x.,x.,x,x.,x,,.,.,,,,,.,.,x,x.,x,x.,x.,x.,x,x.,x.,x,x.,x.,x.,x,x.,x,.,.,,.,.,.,,.,,x,x.,x,x.,x.,x.,x,x.,x.,x,x.,x.,x.,x,x.,x,.,,.,.,.,,.,,.,x,x.,x,x.,x.,x.,x,x.,x.,x,x,x,x,x,x.,x,.,.,.,,,,.,.,.,x,x.,x,x,x,x,x,x.,x.,x.,x.,x.,x.,x.,x.,x,x.,x,x.,x,x.,x,x.,x,x.,x,x.,x.,x.,x.,x.,x.,x.,x,x,x,x,x,x,x,x,,.,.,.,,.,,.,.,x,x,x,x,x,x,x,x,,,,.,,,x.,,,.,,,,.,,.,.,,,.,.,.,,.,.,,,,.,.,,x,.,.,.,.,,.,,.,,.,.,,,.,.,.,,,.,,,,.,.,x.,,,,.,,.,.,.,.,,,.,.,,.,.,.,,,.,,,,.,x,,,,.,.,.,.,.,,,.,,,,.,,,,.,.,.,.,,,x.,.,,,,.,.,,.,.,,,.,,.,.,,.,,,,.,,.,.,x,,.,,,.,,.,.,.,.,,,,,,.,,,.,,.,,,.,x.,,.,.,.,,,.,,,,,,,,.,.,.,.,,.,.,,.,,x,.,.,.,,,,,.,.,,.,.,.,,,.,.,,.,.,.,.,,.,x.,,.,.,.,.,.,,.,,x.,x.,x.,x.,x.,.,,.,.,x,x,x,x,x,x,x,x,.,,,.,.,.,,.,x.,x,x,x,x.,,,.,.,x.,x.,x.,x.,x.,x.,x.,x,,.,,.,.,.,.,,x.,x,x.,x,x.,.,,,,x.,x,x,x,x,x,x.,x,,,.,.,.,,,,x.,x,x,x,x.,,.,,,x.,x,x.,x.,x.,x,x.,x,,.,.,,.,,.,.,x.,x.,x.,x.,x.,.,.,,.,x.,x,x.,x.,x.,x,x.,x,.,.,,.,,.,,.,.,,.,,.,.,.,.,,x.,x,x.,x.,x.,x,x.,x,,.,,.,,,.,.,.,,.,,.,,.,,.,x.,x,x,x,x,x,x.,x,,.,.,,.,.,.,,,,,.,,.,.,,.,x.,x.,x.,x.,x.,x.,x.,x,,.,,,.,.,.,,.,.,.,,.,.,.,,.'
  boardsplit = board.split(",")
  newboards = []
  for i in range(5):
    for j in range(5):
      newboards.append([])
      copy_falsecode = copy.deepcopy(falsecode)
      copy_truecode = copy.deepcopy(truecode)
      copy_falsedata = copy.deepcopy(falsedata)
      copy_truedata = copy.deepcopy(truedata)
      for k in range(5):
        start = 125*i+ 5*j + 25*k
        newboards[5*i+j].append([])
        for l in range(5):
          term = boardsplit[start+l]
          if term == 'x':
            value = random.choice(copy_falsecode)
            copy_falsecode.remove(value)
          elif term == 'x.':
            value = random.choice(copy_truecode)
            copy_truecode.remove(value)
          elif term == '':
            value = random.choice(copy_falsedata)
            copy_falsedata.remove(value)
          else:
            value = random.choice(copy_truedata)
            copy_truedata.remove(value)
          newboards[5*i+j][k].append(value)
  random.seed(oldSeed)
  return newboards



def get_boards(team) -> List[List[List[str]]]:
  store = storage.Client()
  bucket = store.get_bucket('mh2021-puzzle-data-dev')
  blob_name = f'bingo/boardV{VERSION}-team-{team.y2021teamdata.tempest_id}'
  try:
    dataFile = bucket.get_blob(blob_name)
    if dataFile:
      return json.loads(dataFile.download_as_string())
  except:
    pass

  boards = generate_boards(team)

  data = json.dumps(boards)
  try:
    b = bucket.blob(blob_name)
    b.upload_from_string(data)
  except:
    pass
  return boards

@require_puzzle_access
def puzzle69_view(request):
    rand = random.randint(0,99)
    boardnum = rand%25

    boards = get_boards(request.team)
    res = {
        "num": boardnum+1,
        "board": boards[boardnum]
    }
    return JsonResponse(res, safe=False)
