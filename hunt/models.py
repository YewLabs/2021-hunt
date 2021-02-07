from django.db import models
from spoilr.models import Puzzle, Round, Team, Interaction
from spoilr.puzzle_session import PuzzleSessionModelBase
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
import hashlib
import math
import json

from hunt.constants import *

class Y2021TeamData(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    auth = models.CharField(max_length=128)
    tempest_id = models.IntegerField(null=True, unique=True)
    emoji = models.CharField(max_length=128, blank=True)
    juice = models.TextField(default=json.dumps((0,{})))

    def get_juice(self, qrnd=None):
        global_juice, round_juice = json.loads(self.juice)
        if qrnd:
            qrnd = str(qrnd)
            if qrnd not in round_juice:
                return None
            return global_juice + round_juice[qrnd]
        return (global_juice, round_juice)

    def set_juice(self, global_juice, round_juice):
        self.juice = json.dumps((global_juice, round_juice))
        self.save()

    @property
    def base_juice(self):
        return json.loads(self.juice)[0]


    def __str__(self):
        return u'%s' % (self.team.name)

    class Meta:
        verbose_name = '2021 team data'
        verbose_name_plural = '2021 team data'

def obfuscate(tid):
    return hashlib.sha256(('%s:%d' % ("SPY21", tid)).encode('utf-8')).hexdigest()

class Y2021PuzzleData(models.Model):
    puzzle = models.OneToOneField(Puzzle, on_delete=models.CASCADE)
    tempest_id = models.IntegerField(null=True, unique=True)
    obfuscated_id = models.CharField(unique=True, max_length=128)
    points_req = models.IntegerField(verbose_name='JUICE required', blank=True, null=True)
    feeder_req = models.IntegerField(verbose_name='Feeders required', blank=True, null=True)
    feeder_tag = models.CharField(max_length=200, blank=True, null=True)
    required_available_puzzle = models.ForeignKey(Puzzle, related_name='dependent_available_puzzles', on_delete=models.SET_NULL, null=True, blank=True)
    unlock_time = models.DateTimeField(null=True, blank=True)
    level = models.IntegerField(blank=True, null=True)
    unlock_req = models.CharField(max_length=200, blank=True, null=True)
    instructions = models.TextField(default="", blank=True)
    infinite = models.BooleanField(default=False, db_index=True)
    parent = models.ForeignKey(Puzzle, related_name='child_puzzles', on_delete=models.SET_NULL, null=True, blank=True)
    hint_solve_threshold = models.IntegerField(default=30)
    hint_stuck_duration = models.DurationField(null=True, blank=True)

    @property
    def infinite_id(self):
        if self.infinite:
            return self.tempest_id - INFINITE_BASE_ID
        return None

    def __str__(self):
        if self.points_req is not None:
            return u'%s (JUICE req %d)' % (self.puzzle.name, self.points_req)
        elif self.feeder_req is not None:
            return u'%s (Feeders req %d)' % (self.puzzle.name, self.feeder_req)
        else:
            return u'%s (Special)' % (self.puzzle.name)

    class Meta:
        verbose_name = '2021 puzzle data'
        verbose_name_plural = '2021 puzzle data'

class Y2021RoundData(models.Model):
    round = models.OneToOneField(Round, on_delete=models.CASCADE)
    tempest_id = models.IntegerField(null=True, unique=True)
    round_points_granted = models.FloatField(default=50, verbose_name='In-Round JUICE Granted')
    outer_points_granted = models.FloatField(default=10, verbose_name='Outside Round JUICE Granted')
    points_required = models.FloatField(default=0, verbose_name='JUICE required')

    class Meta:
        verbose_name = '2021 round data'
        verbose_name_plural = '2021 round data'

class Y2021Settings(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="slug")
    value = models.TextField()

    def __str__(self):
        return f"Y2021 Setting {self.name}={self.value}"


forceUnlock = (
    ('', 'None'),
    ('LOCKED', 'LOCKED'),
    ('AVAILABLE', 'AVAILABLE'),
    ('FOUND', 'FOUND'),
    ('SOLVED', 'SOLVED'),
)

class MMOUnlock(models.Model):
    unlock_id = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    puzzle = models.ForeignKey(Puzzle, null=True, blank=True, on_delete=models.SET_NULL)
    interaction = models.ForeignKey(Interaction, null=True, blank=True, on_delete=models.SET_NULL)
    round = models.ForeignKey(Round, null=True, blank=True, on_delete=models.SET_NULL)
    juice = models.FloatField(null=True, blank=True)
    unlock_time = models.DateTimeField(null=True, blank=True)
    presolve_text = models.TextField(blank=True)
    solve_text = models.TextField(blank=True)
    force = models.CharField(max_length=10, blank=True, default='', choices=forceUnlock)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if SKIP_UNLOCK_SAVE:
            return
        import hunt.mmo_unlock as mu
        mu.unlock_saved(self)

    def __str__(self):
        return u'%s' % (self.unlock_id)

    class Meta:
        verbose_name = 'MMO Unlock'
        verbose_name_plural = 'MMO Unlocks'

class TeamworkSession(models.Model):
    """Generic session information about teamwork time puzzles.

    This model is shared across all puzzles. A team can have multiple sessions,
    but should have at most one active session per puzzle.

    Some teamwork puzzles' sessions require a leader, mainly so that we can
    assign ownership of session-wide actions that should only happen once.
    Management of that leadership is also handled in this model.
    """

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    active = models.BooleanField(default=False, db_index=True)

    # For what it's worth, str(uuid.uuid4()) is 36 characters.
    websocket_group = models.CharField(max_length=60, unique=True, blank=True)

    # This is the websocket channel_name for the consumer belonging to the
    # session leader.
    leader = models.CharField(max_length=100, blank=True)

    # Used for tiebreaks in case they're needed
    last_update = models.DateTimeField(auto_now=True)


class JuiceBox(models.Model):
    round = models.ForeignKey(Round, null=True, blank=True, on_delete=models.SET_NULL)
    juice = models.FloatField(null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    unlock_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        out = ''
        if self.round:
            out = '%d %s JUICE' % (self.juice, self.round.name)
        else:
            out = '%d JUICE' % (self.juice)
        if self.team:
            out += ' for %s' % (self.team.name)
        if not self.active:
            out += ' (inactive)'
        return out

class JuiceSchedule(models.Model):
    students_juice = models.FloatField(null=True, blank=True)
    green_juice = models.FloatField(null=True, blank=True)
    infinite_juice = models.FloatField(null=True, blank=True)
    nano_juice = models.FloatField(null=True, blank=True)
    stata_juice = models.FloatField(null=True, blank=True)
    clusters_juice = models.FloatField(null=True, blank=True)
    tunnels_juice = models.FloatField(null=True, blank=True)
    real_infinite_juice = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField()
    active = models.BooleanField(default=False)

# Dynamic Puzzles
from hunt.sample_puzzle import PuzzleSampleSession, SamplePuzzleTeamData
from hunt.special_puzzles.counting.models import *  # puzzle277
from hunt.special_puzzles.puzzle179 import *
from hunt.special_puzzles.ktane.puzzle import KtaneTeamData, KtaneHighScoreData
from hunt.special_puzzles.puzzle538 import SqueeSqueeState
from hunt.special_puzzles.events.fencing import FencingTeamData
from hunt.special_puzzles.boggle.models import BoggleTeamData, BoggleHighScoreData
