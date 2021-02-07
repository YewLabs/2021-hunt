import datetime
import os
import re
from string import ascii_uppercase

from django.db import models, transaction
from django.template.loader import render_to_string
from django.utils.timezone import now

from hunt.models import TeamworkSession
from hunt.teamwork import TeamworkTimeConsumer
from hunt.interactions import submission_instructions

VIRTUAL_MESSAGE = "You are solving the virtual version of the puzzle."
VIRTUAL_TRIGGER = "I WANT VIRTUAL BACON"
VIRTUAL_AUTH = "cfee9c9035e238198097d249895576b4b998c2e396c13f994a2532cf1651778e"

OBJECT_PRONOUNS = {
    'he': 'him',
    'she': 'her',
    'they': 'them',
    'it': 'it',
}

CONTRACTED_SUBJECTS = {
    'he': 'he’s',
    'she': 'she’s',
    'they': 'they’re',
    'it': 'it’s',
}

STAGES = [
    'intro',
    'pigsaw',
    'dinner',
    'sleeping',
    'health',
    'feeding1',
    'chewing1',
    'feeding2',
    'chewing2',
    'coins',
    'photo',
    'finish',
    'trueend',
]

SUBPUZZLE_ANSWERS = {
    'pigsaw': 'EATDINNER',
    'health': 'FATANDHAPPY',
    'coins': 'IGOTMYQUARTERSBACK',
    'photo': 'PIGPENPALS',
}

STAGE_TIME = {
    "sleeping": 60,
    "chewing1": 10,
    "chewing2": 10,
}

DO_IT = ['dinner', 'feeding1', 'feeding2']

STARTING_COUNTS = {
    "quarter": 0,
    "dime": 2,
    "nickel": 4,
    "penny": 3,
}

def next_stage(stage):
    idx = STAGES.index(stage) + 1
    idx = idx if idx < len(STAGES) else 0
    return STAGES[idx]


def normalize(guess):
    return re.sub(r'[^A-Z]', '', guess.upper())

class SqueeSqueeState(models.Model):

    # The session should never become inactive.
    session = models.OneToOneField(TeamworkSession, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True)
    pronoun = models.CharField(max_length=10, default='he',
        choices=((s,s) for s in OBJECT_PRONOUNS.keys()))
    stage = models.CharField(max_length=10, default='intro', choices=((s,s) for s in STAGES))
    previous_action_time = models.DateTimeField(null=True, blank=True)
    virtual = models.BooleanField(default=False)
    quarter_count = models.PositiveIntegerField(default=STARTING_COUNTS['quarter'])
    dime_count = models.PositiveIntegerField(default=STARTING_COUNTS['dime'])
    nickel_count = models.PositiveIntegerField(default=STARTING_COUNTS['nickel'])
    penny_count = models.PositiveIntegerField(default=STARTING_COUNTS['penny'])


class SqueeSqueeConsumer(TeamworkTimeConsumer):

    puzzle_state = None

    def setup(self):
        super(SqueeSqueeConsumer, self).setup(538)
    
    @transaction.atomic
    def join_or_create_session(self):
        super(SqueeSqueeConsumer, self).join_or_create_session()
        session = self.get_session()
        self.puzzle_state, _ = SqueeSqueeState.objects.get_or_create(session=session)

    def handle(self, payload):
        if payload['type'] == 'refresh':
            context = self.update_and_get_context()
            content = render_puzzle_stages(context, payload['virtual-auth'])
            selection = (
                "virtual" if context['virtual'] else
                "physical" if context['name'] is not None else
                "none")

            # send response to client
            self.respond({
                'type': 'refresh',
                'content': content,
                'selection': selection,
            })
        elif payload['type'] == 'pronoun':
            self.update_pronoun(payload['pronoun'])
            # broadcast to other clients
            self.broadcast(payload)
        elif payload['type'] == 'doIt':
            if self.do_it():
                self.broadcast({'type': 'refresh_request'})
        elif payload['type'] == 'guess':
            correct, response = self.submit(payload['guess'])
            if correct:
                self.broadcast({'type': 'refresh_request'})
            elif response == VIRTUAL_MESSAGE:
                self.respond({'type': "incorrect_guess", "msg": response})
                self.broadcast({'type': 'refresh_request'})
            else:
                self.respond({'type': "incorrect_guess", "msg": response})
        elif payload['type'] == 'reset':
            self.reset()
            self.broadcast({'type': 'refresh_request'})
        elif payload['type'] == 'rename':
            self.rename()
            self.broadcast({'type': 'refresh_request'})
        elif payload['type'] == 'coin':
            self.update_coin(payload['coin'], payload['count'])
            self.broadcast(payload)


    @transaction.atomic
    def update_and_get_context(self):
        self.puzzle_state.refresh_from_db()
        stage = self.puzzle_state.stage
        pronoun = self.puzzle_state.pronoun
        name = self.puzzle_state.name
        prev_time = self.puzzle_state.previous_action_time
        virtual = self.puzzle_state.virtual

        context = {
            'name': name,
            'subject_pronoun': pronoun,
            'contracted_subject': CONTRACTED_SUBJECTS[pronoun],
            'object_pronoun': OBJECT_PRONOUNS[pronoun],
            'virtual': virtual,
        }

        for coin in STARTING_COUNTS:
            context[coin] = getattr(self.puzzle_state, coin+"_count")

        if name is not None:
            context['fav_num'] = ord('W') - ord(name[0].upper())

        for p in OBJECT_PRONOUNS.keys():
            context[p + "_pronoun"] = p == pronoun

        if stage in STAGE_TIME:
            time_elapsed = (now() - prev_time).seconds
            time_remaining = STAGE_TIME[stage] - time_elapsed
            context['m_remaining'] = time_remaining//60
            context['s_remaining'] = time_remaining%60
            if time_remaining <= 0:
                stage = next_stage(stage)
                # commit to DB
                self.puzzle_state.stage = stage
                self.puzzle_state.save()
        context['stage'] = stage

        context['submission_instructions'] = submission_instructions(
            self.puzzle.interaction.first(), self.team)

        return context

    @transaction.atomic
    def update_pronoun(self, pronoun):
        if pronoun not in OBJECT_PRONOUNS.keys():
            return
        # update pronoun in DB
        self.puzzle_state.refresh_from_db()
        self.puzzle_state.pronoun = pronoun
        self.puzzle_state.save()

    @transaction.atomic 
    def submit(self, guess):
        self.puzzle_state.refresh_from_db()
        stage = self.puzzle_state.stage
        if stage == "intro":
            guess = guess.strip()
            if len(guess) == 0: 
                return False, "Name cannot be blank"
            if guess[0].upper() not in ascii_uppercase:
                return False, "Invalid name"
            if normalize(guess) == normalize(VIRTUAL_TRIGGER):
                self.puzzle_state.virtual = True
                self.puzzle_state.save()
                return False, VIRTUAL_MESSAGE
            self.puzzle_state.stage = next_stage(stage)
            self.puzzle_state.name = guess
            self.puzzle_state.save()
            return True, None

        guess = normalize(guess)
        if stage in SUBPUZZLE_ANSWERS:
            if guess == SUBPUZZLE_ANSWERS[stage]:
                # commit to DB
                self.puzzle_state.previous_action_time = now()
                self.puzzle_state.stage = next_stage(stage)
                self.puzzle_state.save()
                return True, None

        return False, guess + " is incorrect"

    @transaction.atomic
    def update_coin(self, coin, count):
        if coin in STARTING_COUNTS:
            setattr(self.puzzle_state, coin+"_count", count)
            self.puzzle_state.save()

    @transaction.atomic
    def do_it(self):
        self.puzzle_state.refresh_from_db()
        stage = self.puzzle_state.stage
        if stage in DO_IT or (self.puzzle_state.virtual and stage == "finish"):
            # commit to DB
            self.puzzle_state.previous_action_time = now()
            self.puzzle_state.stage = next_stage(stage)
            self.puzzle_state.save()
            return True
        return False

    @transaction.atomic
    def rename(self):
        self.puzzle_state.refresh_from_db()
        self.puzzle_state.stage = "intro"
        self.puzzle_state.name = None
        self.puzzle_state.previous_action_time = None
        self.puzzle_state.save()


    @transaction.atomic
    def reset(self):
        self.puzzle_state.refresh_from_db()
        self.puzzle_state.stage = "intro"
        self.puzzle_state.pronoun = "he"
        self.puzzle_state.name = None
        self.puzzle_state.previous_action_time = None
        self.puzzle_state.virtual = False
        for coin, count in STARTING_COUNTS.items():
            setattr(self.puzzle_state, coin+"_count", count)
        self.puzzle_state.save()

def render_puzzle_stages(context, virtual_auth):
    current_stage = context['stage']
    unlocked = True
    for stage in STAGES:
        context[stage + "_unlocked"] = unlocked
        if stage == current_stage or (context['virtual'] and virtual_auth != VIRTUAL_AUTH):
            unlocked = False

    return render_to_string('puzzle/squee-squee/squee_squee.html', context)
