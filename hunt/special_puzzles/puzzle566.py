from django.db import models
from django.http import HttpResponse
from spoilr.decorators import *
from spoilr.models import *
from spoilr.puzzle_session import *

import base64
import datetime
import json
import time

from hunt.actions import get_infinite

from channels.generic.websocket import WebsocketConsumer

@require_puzzle_url
def puzzle566_data(request, iid):
    import hunt.special_puzzles.infinite_simulator.simulator as infinite_simulator

    p = get_infinite(int(iid))
    if not p or p.y2021puzzledata.parent != request.puzzle:
        return HttpResponse("[]")
    return HttpResponse(infinite_simulator.generate_data(p, True), content_type="application/json")
