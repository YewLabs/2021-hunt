from django.urls import re_path

import hunt.sample_puzzle
from hunt.special_puzzles import puzzle26, puzzle179, puzzle277, puzzle538, puzzle593, puzzle617
from hunt.special_puzzles.ktane.puzzle import KtaneConsumer
from hunt.special_puzzles.boggle.puzzle import BoggleConsumer
from .notifications import TeamNotificationsConsumer

websocket_urlpatterns = [
    re_path('^ws/puzzle/(?P<puzzle>cool_dynamic_puzzle)$', hunt.sample_puzzle.SamplePuzzleConsumer),

    re_path('^ws/puzzle/(?P<puzzle>cooperation)$', puzzle26.Puzzle26Consumer),
    re_path('^ws/puzzle/(?P<puzzle>counting)$', puzzle277.CountingConsumer),
    re_path('^ws/puzzle/(?P<puzzle>analog-circuitry)$', puzzle593.Puzzle593Consumer),
    re_path('^ws/puzzle/(?P<puzzle>divided-is-us)$', puzzle617.Puzzle617Consumer),
    re_path('^ws/puzzle/(?P<puzzle>yweiyst)$', KtaneConsumer),
    re_path('^ws/puzzle/(?P<puzzle>squee-squee)$', puzzle538.SqueeSqueeConsumer),
    re_path('^ws/puzzle/(?P<puzzle>boggle)$', BoggleConsumer),

    re_path('^ws/team$', TeamNotificationsConsumer),
]
