import argparse
import collections
import json
import logging
import pathlib
import random
import re
import time

from hunt.special_puzzles.cafe_luge.question_parser import (
    all_files_with_extension,
    question_set_from_file,
    sanitize,
)
from hunt.special_puzzles.cafe_luge.question_formatter import question_to_msg

WRONG_ANSWER_PENALTY_RATIO = 0.2
TIMEOUT_PENALTY_RATIO = 0.8
TURBO_RATE = 3.0  # Time during turbo deducts this many times faster than normal
TOTAL_TIME = 45 * 60
TIME_REMAINING_WHEN_SPAWN_BOSS = 25 * 60
MAXIMUM_TOTAL_PENALTY_TIME = 35 * 60

BUCKETS = ['easy', 'medium', 'hard', 'boss']
QUESTIONS_BY_DIFFICULTY = {}
QUESTIONS_BY_ID = {}

CAFE_INITIALIZED = False

class CafeTeamData:
    def __init__(self):
        global CAFE_INITIALIZED
        if not CAFE_INITIALIZED:
            load_questions()
        self.active_questions = {}
        self.questions_answered = 0
        self.questions_posed = 0
        self.total_penalty_time_applied = 0
        self.comps = 1
        self.comp_progress = 0
        self.do_nothing_streak = 0
        self.finish_time = None
        self.next_spawn_times = None
        self.status = 'not_started'
        self.got_boss = False
        self.bucket_positions = {b: 0 for b in BUCKETS}

        self.next_qid = 0

    def new_game(self):
        self.finish_time = time.time() + TOTAL_TIME
        self.active_questions = {}
        self.next_spawn_times = { k: time.time() + 10 for k in ['easy', 'medium', 'hard'] }
        self.questions_answered = 0
        self.questions_posed = 0
        self.total_penalty_time_applied = 0
        self.comps = 1
        self.comp_progress = 0
        self.do_nothing_streak = 0
        self.got_boss = False
        self.status = 'in_game'

    def end_game(self):
        self.active_questions = {}
        self.status = 'not_started'

    def state(self):
        # Returns a dictionary representing the game state of this team.
        # Since "turbo mode" is implemented by subtracting time from a team's clock,
        # and no data is actually stored, we reverse the time subtraction here if a
        # team is currently in turbo.
        if self.status == 'in_game':
            if len(self.active_questions) > 0:
                ft = self.finish_time
            else:
                next_spawn_time = 1e15
                spawn_frequencies = self.spawn_frequency_by_bucket()
                for bucket in ['easy', 'medium', 'hard']:
                    if spawn_frequencies[bucket] >= 0:
                        next_spawn_time = min(next_spawn_time, self.next_spawn_times[bucket])

                time_zero_questions = next_spawn_time - time.time()
                ft = self.finish_time + time_zero_questions * (TURBO_RATE - 1.0)
        else:
            ft = 0

        return {
            'type': 'state',
            'cafeFinishTime': ft,
            'canTurbo': (self.questions_posed > 0),
            'comps': self.comps,
            'compProgress': self.comp_progress,
            'nextQuestionTime': self.next_spawn_time(),
            'status': self.status,
            'penaltyRatio': self.penalty_ratio(),
            'answered': self.questions_answered,
            'questions': [
                {
                    'id': k['id'],
                    'finishTime': k['finishTime'],
                    'time': k['time'],
                    'value': k['text'],
                }
                for k in self.active_questions.values()
            ]
        }

    def penalty_ratio(self):
        ratio = 1.2 * (1 - self.total_penalty_time_applied / MAXIMUM_TOTAL_PENALTY_TIME)
        return min(1, max(0, ratio))

    def handle_answer(self, qid, response):
        player_answer = sanitize(response)

        if qid not in self.active_questions:
            # another teammate probably answered it, just pretend it's correct for the client
            return {
                'type': 'answerCheck',
                'id': qid,
                'correct': True,
                'nextQuestionTime': self.next_spawn_time(),
            }

        answers = [str(k['answer']) for k in self.active_questions[qid]['question'].content if 'answer' in k]
        answers = [sanitize(a) for a in answers]

        correct = (player_answer in answers)
        self.do_nothing_streak = 0

        if not correct:
            penalty_time_raw = (
                self.active_questions[qid]['time']
                * WRONG_ANSWER_PENALTY_RATIO
                * self.penalty_ratio()
            )

            old_finish_time = self.finish_time
            self.finish_time += penalty_time_raw
            if self.finish_time > time.time() + TOTAL_TIME:
                self.finish_time = time.time() + TOTAL_TIME
            print('[DEBUG] wrong answer; increasing time by ', penalty_time_raw)
            self.total_penalty_time_applied += (self.finish_time - old_finish_time)
        elif len(self.active_questions) == 1:
            # Reduce finish time to account for turbo.
            # Calculate when the next question will appear
            time_zero_questions = self.next_spawn_time() - time.time()
            turbo_deduction = time_zero_questions * (TURBO_RATE - 1.0)
            self.finish_time -= turbo_deduction
            print(f'[DEBUG] deducted {turbo_deduction} seconds due to turbo')

        if correct:
            self.questions_answered += 1
            active_q = self.active_questions[qid]
            question_start = (active_q['finishTime'] - active_q['time'])
            ratio_time_taken = (time.time() - question_start) / active_q['time']
            del self.active_questions[qid]

            if ratio_time_taken < 0.15:
                self.comp_progress += 3
            else:
                self.comp_progress += 1
            if self.comp_progress >= 30:
                self.comp_progress -= 30
                self.comps += 1

        return {
            'type': 'answerCheck',
            'id': qid,
            'correct': correct,
            'nextQuestionTime': self.next_spawn_time(),
        }

    def comp(self, qid):
        comps_required = 1
        if self.active_questions[qid]['time'] > 15 * 60:
            comps_required = 2

        self.do_nothing_streak = 0
        if self.comps >= comps_required and qid in self.active_questions:
            self.comps -= comps_required

            if len(self.active_questions) == 1:
                # Reduce finish time to account for turbo.
                # Calculate when the next question will appear
                time_zero_questions = self.next_spawn_time() - time.time()
                turbo_deduction = time_zero_questions * (TURBO_RATE - 1.0)
                self.finish_time -= turbo_deduction
                print(f'[DEBUG COMP] deducted {turbo_deduction} seconds due to turbo')

            del self.active_questions[qid]

        return {
            'type': 'comp',
            'id': qid,
            'comps': self.comps,
            'nextQuestionTime': self.next_spawn_time(),
        }

    def next_spawn_time(self):
        if self.status != 'in_game':
            return -1

        # Get the time until this team will receive their next question
        n = 1e15
        spawn_frequencies = self.spawn_frequency_by_bucket()
        for bucket in ['easy', 'medium', 'hard']:
            if spawn_frequencies[bucket] >= 0:
                n = min(n, self.next_spawn_times[bucket])

        return n

    def add_question_from_bucket(self, bucket):
        global QUESTIONS_BY_DIFFICULTY
        q = QUESTIONS_BY_DIFFICULTY[bucket][self.bucket_positions[bucket]]

        questions_in_bucket = len(QUESTIONS_BY_DIFFICULTY[bucket])
        self.bucket_positions[bucket] = (
            (self.bucket_positions[bucket] + 1) % questions_in_bucket
        )

        h = question_to_msg(q)
        self.active_questions[self.next_qid] = {
            'id': self.next_qid,
            'finishTime': time.time() + q.time,
            'time': q.time,
            'question': q,
            'text': h,
        }

        self.questions_posed += 1
        self.next_qid += 1

    def clean_stale_questions(self):
        for q in self.active_questions.values():
            if q['finishTime'] <= time.time() + 3:
                old_finish_time = self.finish_time
                penalty_time_raw = (
                    q['question'].time
                    * TIMEOUT_PENALTY_RATIO
                    * self.penalty_ratio()
                )
                self.finish_time += penalty_time_raw
                if self.finish_time > time.time() + TOTAL_TIME:
                    self.finish_time = time.time() + TOTAL_TIME
                self.total_penalty_time_applied += (self.finish_time - old_finish_time)
                self.do_nothing_streak += 1
                print('[DEBUG] out of time; increasing time by ', q['question'].time)

        self.active_questions = {
            k: v for k, v in self.active_questions.items()
            if v['finishTime'] > time.time() + 3
        }

        if self.do_nothing_streak == 8:
            self.end_game()

    def spawn_frequency_by_bucket(self):
        # Returns a dictionary mapping bucket names to ints,
        # e.g. { 'easy' : 40, 'medium' : 120, 'hard' : 300 }.
        # The integer represents how many seconds (on average) between each
        # puzzle of that type is given.
        # This value is completely dependent on the stage that the team is at.

        time_left = self.finish_time - time.time()
        time_elapsed = max(TOTAL_TIME - time_left, 0)

        stage = 1 + int(8 * time_elapsed / TOTAL_TIME)

        if stage == 1:
            return { 'easy' : 34, 'medium' : -1, 'hard': -1 }
        elif stage == 2:
            return { 'easy' : 36, 'medium' : 160, 'hard': -1 }
        elif stage == 3:
            return { 'easy' : 34, 'medium' : 190, 'hard' : 300 }
        elif stage == 4:
            # Break time
            return { 'easy' : 45, 'medium' : 200, 'hard' : -1 }
        elif stage == 5:
            return { 'easy' : 34, 'medium' : 180, 'hard' : 260 }
        elif stage == 6:
            return { 'easy' : 31, 'medium' : 165, 'hard' : 230 }
        elif stage == 7:
            # This is where the boss spawns
            # Pepper them with lots of easy questions while they're dealing with the boss
            return { 'easy' : 25, 'medium' : 220, 'hard' : -1 }
        elif stage == 8:
            return { 'easy' : 27, 'medium' : 130, 'hard' : 200 }

        print(f'Error: invalid stage {stage} | '
              f'finish time {self.finish_time} time_elapsed {time_elapsed}')
        return { 'easy' : 60, 'medium' : INF, 'hard' : INF }

    def refresh(self):
        if self.status != 'in_game':
            return None

        self.clean_stale_questions()

        if time.time() >= self.finish_time:
            self.status = 'finished'
            self.active_questions = {}
            return {
                'type': 'answer',
            }

        time_left = self.finish_time - time.time()
        time_elapsed = TOTAL_TIME - time_left
        stage = 1 + int(8 * time_elapsed / TOTAL_TIME)

        if not self.got_boss and time_left < TIME_REMAINING_WHEN_SPAWN_BOSS:
            self.got_boss = True
            self.add_question_from_bucket('boss')

            return {
                'type': 'bossAlert',
            }

        spawn_frequency = self.spawn_frequency_by_bucket()
        for bucket in ['easy', 'medium', 'hard']:
            next_spawn = self.next_spawn_times[bucket]

            if time.time() >= next_spawn:
                if spawn_frequency[bucket] < 0:
                    next_spawn = time.time() + 1.0
                    self.next_spawn_times[bucket] = next_spawn
                else:
                    formatted_timeleft = f'{int(time_left/60)}m {int(time_left%60)}s'
                    print(f'[DEBUG] time left {formatted_timeleft} (stage {stage}): '
                          f'serving [{bucket}] question')

                    next_spawn = time.time() + (0.85 + 0.3 * random.random()) * spawn_frequency[bucket]
                    self.next_spawn_times[bucket] = next_spawn
                    self.add_question_from_bucket(bucket)

        return None

def validate_question(q):
    msg = question_to_msg(q)

def load_questions():
    files = all_files_with_extension(['yml'])
    question_sets = []
    #files = ['puzzles\\intro\\intro-jakob.yml']
    for f in files:
        question_sets.append(question_set_from_file(f))

    global QUESTIONS_BY_DIFFICULTY
    QUESTIONS_BY_DIFFICULTY = {b: [] for b in BUCKETS}

    d = collections.defaultdict(int)
    for qs in question_sets:
        if qs.difficulty <= 3:
            bucket = 'easy'
        elif qs.difficulty <= 6:
            bucket = 'medium'
        elif qs.difficulty <= 9:
            bucket = 'hard'
        else:
            bucket = 'boss'

        for q in qs.questions:
            try:
                validate_question(q)
                QUESTIONS_BY_DIFFICULTY[bucket].append(q)
            except Exception as e:
                print(f'[cafe-luge] Error loading question from set {qs.name}!\n> {e}')

    oldSeed = random.random()
    random.seed(53)
    for b in BUCKETS:
        random.shuffle(QUESTIONS_BY_DIFFICULTY[b])
    random.seed(oldSeed)
    total_sets = len(question_sets)
    total_questions = sum([len(q.questions) for q in question_sets])

    global CAFE_INITIALIZED
    CAFE_INITIALIZED = True
    #print(f'[cafe-luge] Loaded {total_questions} questions from {total_sets} sets! '
    #      f'({len(QUESTIONS_BY_DIFFICULTY["easy"])} easy, '
    #      f'{len(QUESTIONS_BY_DIFFICULTY["medium"])} medium, '
    #      f'{len(QUESTIONS_BY_DIFFICULTY["hard"])} hard, '
    #      f'{len(QUESTIONS_BY_DIFFICULTY["boss"])} boss)')
