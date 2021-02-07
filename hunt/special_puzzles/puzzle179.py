from django.db import models
from django.http import JsonResponse
from spoilr.models import *
from spoilr.puzzle_session import *
from spoilr.actions import solve_puzzle
from spoilr.log import discord_log

import base64
import datetime
import json
import time

from hunt.special_puzzles.cafe_luge import team_data
from hunt.special_puzzles.cafe_luge.question_parser import Question
from hunt.teamwork import TeamworkTimeConsumer
from hunt.actions import get_infinite

class Puzzle179TeamData(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    completions = models.IntegerField(default=0)
    redemptions = models.IntegerField(default=0)

    active_questions = models.TextField(default='')
    questions_answered = models.IntegerField(default=0)
    questions_posed = models.IntegerField(default=0)
    total_penalty_time_applied = models.FloatField(default=0)
    comps = models.IntegerField(default=0)
    comp_progress = models.IntegerField(default=0)
    finish_time = models.FloatField(default=0)
    next_spawn_times = models.TextField(default='')
    status = models.IntegerField(default=0)
    got_boss = models.BooleanField(default=False)
    bucket_positions = models.TextField(default='')
    next_qid = models.IntegerField(default=0)
    do_nothing_streak = models.IntegerField(default=0)

    def __str__(self):
        return '%s' % (self.team)

    @transaction.atomic
    def redeem(self, tempest_id):
        if self.redemptions < self.completions:
            p = get_infinite(tempest_id)
            if p.y2021puzzledata.parent.y2021puzzledata.tempest_id == 179:
                if PuzzleAccess.objects.filter(team=self.team, puzzle=p, solved=False).exists():
                    solve_puzzle(self.team, p, 'Redeemed Cafe Luge token.')
                    self.redemptions += 1
                    self.save()
                    return True
        return False

    @transaction.atomic
    def load_game_state(self, cls):
        self.active_questions = json.dumps(cls.active_questions)
        self.questions_answered = cls.questions_answered
        self.questions_posed = cls.questions_posed
        self.total_penalty_time_applied = cls.total_penalty_time_applied
        self.comps = cls.comps
        self.comp_progress = cls.comp_progress
        self.finish_time = cls.finish_time
        self.next_spawn_times = json.dumps(cls.next_spawn_times)
        self.do_nothing_streak = cls.do_nothing_streak
        self.status = (
            0 if cls.status == 'not_started' else
            1 if cls.status == 'in_game' else
            2
        )
        self.got_boss = cls.got_boss
        self.bucket_positions = json.dumps(cls.bucket_positions)
        self.next_qid = cls.next_qid

    @transaction.atomic
    def dump_game_state(self):
        cls = team_data.CafeTeamData()
        cls.active_questions = json.loads(self.active_questions or "{}")

        active_questions = {}
        for k, v in cls.active_questions.items():
            active_questions[int(k)] = v
            active_questions[int(k)]['question'] = Question(*active_questions[int(k)]['question'])
        cls.active_questions = active_questions

        cls.questions_answered = self.questions_answered
        cls.questions_posed = self.questions_posed
        cls.total_penalty_time_applied = self.total_penalty_time_applied
        cls.comps = self.comps
        cls.comp_progress = self.comp_progress
        cls.finish_time = self.finish_time
        cls.next_spawn_times = json.loads(self.next_spawn_times or "{}")
        cls.do_nothing_streak = self.do_nothing_streak
        cls.status = (
            'not_started' if self.status == 0 else
            'in_game' if self.status == 1 else
            'finished'
        )
        cls.got_boss = self.got_boss
        if self.bucket_positions:
            cls.bucket_positions = json.loads(self.bucket_positions)
        cls.next_qid = self.next_qid

        return cls


@require_puzzle_access
def puzzle179_handle_cafe_msg(request):
    data = Puzzle179TeamData.objects.get_or_create(team=request.team)[0]
    try:
        message = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({})

    game_state = data.dump_game_state()

    is_finished = (game_state.status == 'finished')
    msg = None
    if message['type'] == 'init':
        if game_state.status in ['not_started', 'finished']:
            discord_log('cafe-luge', request.team, 'Started a new Café Lüge instance.')
            game_state.new_game()
    elif message['type'] == 'answer':
        msg = game_state.handle_answer(message['id'], message['value'])
    elif message['type'] == 'compRequest':
        msg = game_state.comp(message['id'])
    elif message['type'] == 'refresh':
        msg = game_state.refresh()
    elif message['type'] == 'spendToken':
        status = data.redeem(int(message['id']))

    data.load_game_state(game_state)
    newly_finished = (game_state.status == 'finished' and not is_finished)
    if newly_finished:
        data.completions += 1

    data.save()

    to_return = (msg if msg else game_state.state())

    return JsonResponse({**to_return, 'tokens': data.completions - data.redemptions})
