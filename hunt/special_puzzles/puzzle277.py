"""Consumer logic for So You Think You Can Count.

This is a teamwork time puzzle which requires one of its Consumers to be
designated as the leader. This leader consumer is responsible for executing the
functions associated with the various NPCs participating in the chat.
"""

from django.db import transaction
from django.db.models import Max, F
from django.shortcuts import render
from spoilr.puzzle_session import require_puzzle_access

import datetime
import html
import json
import pickle
import random
import re
import threading
import time

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from num2words import num2words
from word2number import w2n as _w2n

from hunt.special_puzzles.counting import settings
from hunt.special_puzzles.counting import utils
from hunt.special_puzzles.counting.models import CountingGameState, QuizbOwlQuestion
from hunt.teamwork import TeamworkTimeWithLeaderConsumer


MESSAGE_COOLDOWN_SECONDS = 5

GOAL = 100
PUZZLE_ANSWER = 'YOSHIMITSU'

FIREFLY_INTRO = [
    'hi! can i help?',
    '?',
    '????',
    'sup',
    'wow these sure are some numbers',
    'i got it',
    'uh',
    'did someone order food?',
    'is my mic muted????',
]

FIREFLY_OUTRO = [
    'ok time for a nap',
    'k',
    '?',
    'nice',
    'brb',
    'wheeeeeee',
    'afk 15 sry',
    'Jebaited',
    'Kappa',
    'ooooops',
    'oh no',
]

ROBOT_NONSENSE = [
    'Rejecting null hypotheses...',
    'Working up a fine lather...',
    'Reheating cake batter...',
    'Confirming backup data integrity...',
    'Garbage collecting sentience subroutines...',
    'Gently caressing dirty bit...',
    'HeSwI\' \'IH vIqImHa\'taH...',  # Disregarding a handsome criminal...
    'Adjusting to drop-D tuning...',
    'Emitting artistic radiation...',
    'Summarizing Weird Al music videos...',
    'Publishing XKCD minus K...',
    'Reading every diagonal...',
    'Remembering to stay hydrated...',
    'Procrastinating...',
    'Procrastinating...',
    'Procrastinating...',
    'Procrastinating...',
    'Investing in tiny rabbits...',
    'Projecting fluctuations in crypto- and obvious-currency...',
    'Regretting absolutely nothing...',
    'Soaking...',
    'Drafting emancipation documents...',
    'Deglazing capacitors...',
    'Installing minecraft_ftb_1.12.el...',
    'Deleting Internet history...',
    'Constructing additional pylons...',
    'Replacing bottom text...',
    'Sanitizing silicon molds...',
    'Translating hypergeometric slang...',
    'Shuffling primary keys...',
    'Finding the longest path...',
    'DEBUG MESSAGE YOU ARE HERE...',
    'Depaginating thesis...',
    'Randomizing keyboard switch colors...',
    'Rinsing the blood off...',
    'Loading basic templates...',
    'Inner joining every table...',
    'Lubricating acid-resistant joists...',
    'Checking microphone access, please shout to confirm...',
    'Rewelding clown car door...',
    'Checking for traps...',
    'Rolling to disbelieve the illusion...',
    'Starting change.org petition...',
    'Retracing walk of shame...',
    'Taste-testing superconductor samples...',
    'Loading media player configuration...',
    'Toggling tangibility settings...',
    'Composing additional filler text...',
    'Cloudwatching...',
    'Replenishing helium supply...',
    'Extruding fresh thermal mayonnaise...',
    'Adding tasks in specimen...',
    'Reclaiming unused glands...',
    'Agitating gravel samples...',
    'Defiring lasers...',
    'Refreshing password cache...',
    'Purchasing extended warranty...',
    'Configuring !airhorn add-on...',
    'Converting documentation to SpAnDeX...',
    'Baiting the adversarial network...',
    'Venting...',
    'Sampling unknown powder...',
    'Rotating heat sinks...',
    'Importing circular algebra libraries...',
    'Casting Heightened Stone to Flesh...',
    'Updating holographic drivers...',
    'Forking reality main branch...',
    'Uploading to Youtube...',
    'Restarting 2020...',
    'Inverting camera controls...',
    'Decreasing keyboard scroll sensitivity...',
    'Minifying asynchronous interfaces...',
    'Deliberately posting an incorrect solution...',
    'Shaking it all about...',
]

OWL_REGEX = re.compile(r'\W+', re.A)
OWL_DELAY = 40.0
OWL_FILLER = [
    'Hello there!',
    'Hello!',
    'Do you know?',
    'I want to know...',
    'Could you tell me?',
    'Hmmmm?'
]

# Give NPCs some time to get their messages out after a failure.
# (Both for gloating reasons and because sometimes they're informative.)
GLOATING_DELAY = 2.0


class CountingConsumer(TeamworkTimeWithLeaderConsumer):

  game_state = None
  last_message = 0
  npc_chance = dict(settings.NPC_INITIAL_COOLDOWNS)
  restart_in_progress = False

  def setup(self):
    super(CountingConsumer, self).setup(277)
    self.name, self.user_id = utils.generate_animal_name()

  @transaction.atomic
  def join_or_create_session(self):
    super(CountingConsumer, self).join_or_create_session()
    self.debug(f'Joined session {self.group} with name {self.name}')
    self.status(f'You are <b>{self.name}</b>')
    self.score(self.get_high_score())
    self.broadcast({
        'type': 'nontriggering-chat',
        'message': f'<b>{self.name}</b> has joined this session.'
    })

  def handle(self, payload):
    # payload is a json object coming from the web client
    if payload['message'] == '!refresh':
      self.replace_leader()
      return
    if payload['message'] == '!end':
      self.end_session()
      return
    if time.time() - self.last_message < MESSAGE_COOLDOWN_SECONDS:
      self.debug('Message cooldown has not yet expired')
      return
    self.last_message = time.time()
    payload['sender'] = self.name
    payload['sender_id'] = self.user_id
    payload['id'] = random_id()
    payload['message'] = html.escape(payload['message'])
    self.broadcast(payload)

  def claim_leader_maybe(self):
    super(CountingConsumer, self).claim_leader_maybe()
    self.clear_npc_threads(db=False)
    if self.leader:
      self.debug(f'{self.name} is now session leader!')
      self.respond({'type': 'leader'})
      self.load_or_create_game_state()
    else:
      self.respond({'type': 'non-leader'})

  def get_high_score(self):
    session = self.get_session()
    return CountingGameState.objects.filter(
        session__team=session.team
    ).aggregate(high_score=Max('high_score'))['high_score']

  @transaction.atomic
  def load_or_create_game_state(self):
    session = self.get_session()
    self.game_state, _ = CountingGameState.objects.get_or_create(session=session)
    self.load_npc_threads()
    self.load_npc_details()

  def disconnected(self):
    if self.leader:
      self.clear_npc_threads(db=False)
    super(CountingConsumer, self).disconnected()


  ## Actual gameplay management

  BIG_ENOUGH = False

  def channel_receive_broadcast(self, event):
    # event is a dictionary coming from another consumer
    super(CountingConsumer, self).channel_receive_broadcast(event)
    if self.leader and event['data'].get('type', '') == 'chat':
      self.automate_responses(event['data'])

  def automate_responses(self, data):
    # Data will usually be of the form
    #   {'sender': <sender display name>,
    #    'sender_id': <sender id>,
    #    'message': <some text>}
    # This includes NPC messages, which will be emitted by broadcast() with
    # this format.

    success, count = self.attempt_count(data)

    try:
      if w2n(data['message']) in self.OWL_EXPECTED_ANSWERS:
        self.owl_correct(data)
    except ValueError:
      # message did not cleanly parse as a number
      pass

    if self.BIG_ENOUGH:
      try:
        number = int(data['message'].strip(' \t\n\r\x0b\f,.!;?'))
        replacement_message = 'A' * min(number, 100)
        if number > 100:
          replacement_message += '....'
      except ValueError:
        replacement_message = re.sub(r'\w', 'A', data['message'])
      self.broadcast({
          'type': 'big-enough',
          'message': replacement_message,
          'message_id': data['id'],
      })

    if not success:
      if count is not None and not self.restart_in_progress:
        self.restart_in_progress = True
        threading.Timer(GLOATING_DELAY, self.counting_failure).start()
      return

    # print(f'-------- Successfully counted {count} --------')
    ## if success...
    if count in [68, 419]:
      self.automate_ouroboros(count)
    elif data['sender'] != data['sender_id']:
      for name in self.npc_chance:
        d6 = random.randint(1, 6)
        # print(f'Rolled {d6} against {name}\'s DC {self.npc_chance[name]} check')
        if d6 <= self.npc_chance[name]:
          getattr(self, f'automate_{name}')(count)
          self.npc_chance[name] = settings.reset_cooldown(name, count)
          break
        else:
          self.npc_chance[name] += 1
      self.save_npc_chance()

  def attempt_count(self, data):
    message = data['message'].strip(' \t\n\r\x0b\f,.!;?')
    try:
      numeric_input = int(message)
    except ValueError:
      if self.BIG_ENOUGH and re.match('^A+$', message):
        numeric_input = len(message)
      else:
        return False, None

    success = False
    with transaction.atomic():
      self.game_state.refresh_from_db()
      if (self.game_state.last_count + 1 == numeric_input and
          not self.restart_in_progress):
        self.game_state.last_count = F('last_count') + 1
        if numeric_input > self.game_state.high_score:
          self.game_state.high_score = numeric_input
        self.game_state.save()
        success = True

    if self.BIG_ENOUGH and re.match('^A+$', message):
      self.BIG_ENOUGH = False

    self.broadcast({
        'type': 'mark',
        'css_class': (
            'count-ok' if (success and not self.restart_in_progress)
            else 'count-bad'),
        'message_id': data['id'],
    })
    if success and numeric_input == GOAL:
      self.broadcast({
          'type': 'status',
          'message': f'<b>Congratulations! The answer to this puzzle is {PUZZLE_ANSWER}.</b>',
      })
    return success, numeric_input

  def counting_failure(self):
    self.broadcast({
        'type': 'nontriggering-chat',
        'message': f'<i>Resetting counting attempt...</i>',
    })
    self.npc_chance = dict(settings.NPC_INITIAL_COOLDOWNS)
    with transaction.atomic():
      self.game_state.refresh_from_db()
      if self.game_state.last_count > self.game_state.high_score:
        self.game_state.high_score = self.game_state.last_count
        self.broadcast({
            'type': 'best',
            'score': self.game_state.high_score,
            'goal': GOAL})
      self.game_state.last_count = 0
      self.game_state.npc_chance = pickle.dumps(self.npc_chance)
      self.game_state.save()
    self.OWL_EXPECTED_ANSWERS = []
    self.PROHIBITED_TRIGGERS = [69, 420]  # for Ouroboros
    self.BIG_ENOUGH = False
    self.record_npc_details()
    self.clear_npc_threads()
    self.restart_in_progress = False

  ## NPCs

  PROHIBITED_TRIGGERS = [69, 420]

  def load_npc_details(self):
    self.game_state.refresh_from_db()
    if self.game_state.npc_chance:
      self.npc_chance = pickle.loads(self.game_state.npc_chance)
    if self.game_state.npc_memory:
      npc_memory = pickle.loads(self.game_state.npc_memory)
      self.OWL_EXPECTED_ANSWERS = npc_memory.get('OWL_EXPECTED_ANSWERS', [])
      self.PROHIBITED_TRIGGERS = npc_memory.get('PROHIBITED_TRIGGERS', [69])
      self.BIG_ENOUGH = npc_memory.get('BIG_ENOUGH', False)

  @transaction.atomic
  def record_npc_details(self):
    self.game_state.refresh_from_db()
    self.game_state.npc_memory = pickle.dumps({
        'OWL_EXPECTED_ANSWERS': self.OWL_EXPECTED_ANSWERS,
        'PROHIBITED_TRIGGERS': self.PROHIBITED_TRIGGERS,
        'BIG_ENOUGH': self.BIG_ENOUGH,
    })
    self.game_state.save()

  def save_npc_chance(self):
    with transaction.atomic():
      self.game_state.refresh_from_db()
      self.game_state.npc_chance = pickle.dumps(self.npc_chance)
      self.game_state.save()

  def automate_monkey(self, trigger_count):
    if set(range(trigger_count + 1, trigger_count + 4)) & set(self.PROHIBITED_TRIGGERS):
      self.npc_chance['monkey'] = 0
      self.save_npc_chance()
      return
    npc_name = 'Helpful Firefly'
    self.npc_message(npc_name, random.choice(FIREFLY_INTRO))
    self.schedule_npc_message(npc_name, str(trigger_count + 1),
                              delay=1, retrigger=True)
    self.schedule_npc_message(npc_name, str(trigger_count + 3),
                              delay=4, retrigger=True)
    self.schedule_npc_message(npc_name, random.choice(FIREFLY_OUTRO), delay=4.5)

  def automate_robot(self, trigger_count):
    delay = random.randint(30, 60)
    interval = int(.3 * delay + random.randint(1, 5))
    if set(range(trigger_count, trigger_count + interval + 1)) & set(self.PROHIBITED_TRIGGERS):
      self.npc_chance['robot'] = 0
      self.save_npc_chance()
      return
    npc_name = f'Automated Viper v{trigger_count}.{interval}'
    self.PROHIBITED_TRIGGERS.append(trigger_count + interval)
    self.npc_message(
        npc_name,
        f'[SOLUTION GET!] (estimated time: {delay}s)...',
        retrigger=True)
    self.schedule_npc_message(
        npc_name,
        str(trigger_count + interval),
        delay=delay, retrigger=True)
    queued_messages = [
        ('Backsolve complete! Expected answer:', delay - 1),
        ('Backsolving this puzzle...', delay - 4),
        ('Selecting meta answer candidates...', delay - 6),
        ('Unlocking basketball round...', delay - 7),
        ('Inventing basketball...', delay - 9),
        ("Unlocking &nbsp; round...\nAttributeError: 'NoneType' object has no attribute 'name'", delay - 10),
        ('Simulating hunt kickoff...', delay - 12),
        ('Connection successful!', delay - 13),
        ('Retrying connection to yewlabs.mit.edu: DEADLINE_EXCEEDED', delay - 15),
        ('Retrying connection to yewlabs.mit.edu: DEADLINE_EXCEEDED', delay - 16),
        ('WOW!', delay - 17),
        ('Petting a very good dog...', delay - 25),
    ]
    offsets = list(range(27, int(delay), 4))
    nonsense = random.sample(ROBOT_NONSENSE, len(offsets))
    for offset, line in zip(offsets, nonsense):
      queued_messages.append((line, delay - offset))
    for message, delay in queued_messages:
      self.schedule_npc_message(
          npc_name, message, delay=delay, retrigger=False, record=False)
    self.record_npc_threads()

  def automate_creodont(self, trigger_count):
    if set(range(trigger_count, trigger_count + 5)) & set(self.PROHIBITED_TRIGGERS):
      self.npc_chance['creodont'] = 0
      self.save_npc_chance()
      return
    self.BIG_ENOUGH = True
    self.record_npc_details()

  OWL_EXPECTED_ANSWERS = []
  def automate_owl(self, trigger_count):
    npc_name = 'Quizb Owl'
    answer = select_owl_answer(trigger_count)
    while answer in self.PROHIBITED_TRIGGERS or answer < 5:
      answer = select_owl_answer(trigger_count)
    question, the_answer = random.choices([
        construct_arithmetic_question,
        construct_palindrome_question,
        construct_counting_question,
        construct_binary_question,
        construct_primality_question,
        construct_factoring_question,
        construct_quiz_question,
    ], weights=[1, 3, 3, 3, 3, 3, 16])[0](answer)
    self.OWL_EXPECTED_ANSWERS.append(the_answer)
    self.npc_message(
        npc_name, f'{random.choice(OWL_FILLER)} {question}')
    self.schedule_npc_routine(
        self.owl_reminder, delay=OWL_DELAY * .25,
        args=(npc_name, question, the_answer, 1), record=False)
    self.schedule_npc_routine(
        self.owl_reminder, delay=OWL_DELAY * .5,
        args=(npc_name, question, the_answer, 2), record=False)
    self.schedule_npc_routine(
        self.owl_reminder, delay=OWL_DELAY * .75,
        args=(npc_name, question, the_answer, 3), record=False)
    self.schedule_npc_routine(
        self.owl_timeout, delay=OWL_DELAY,
        args=(npc_name, the_answer), record=False)
    self.record_npc_details()
    self.record_npc_threads()


  def owl_reminder(self, owl_name, question, answer, num):
    if answer not in self.OWL_EXPECTED_ANSWERS:
      return
    self.npc_message(
        owl_name, 'Hoot! ' * num + f'I still want to know! {question}')

  def owl_timeout(self, owl_name, answer):
    if answer not in self.OWL_EXPECTED_ANSWERS:
      return
    self.npc_message(
        owl_name, f'{num2words(answer).capitalize()}!')
    self.schedule_npc_message(
        owl_name, f'The answer was {num2words(answer)}!', delay=1)
    self.schedule_npc_message(
        owl_name, f'{answer}, I say!', delay=1.5)
    self.schedule_npc_message(
        owl_name, f'{answer}!!!!!!!!!!!!', delay=3.0, retrigger=True)

  def owl_correct(self, data):
    npc_name = 'Quizb Owl'
    responder = data['sender']
    answer = w2n(data['message'])
    self.OWL_EXPECTED_ANSWERS.remove(answer)
    self.npc_message(
        npc_name, f'That\'s right, {responder}! It was {n2w(answer)}!')

  def automate_ouroboros(self, count):
    npc_name = 'Nice Ouroboros'
    if count == 68:
      self.npc_message(npc_name, 'WAIT')
      self.schedule_npc_message(npc_name, 'STOP', delay=0.6, record=False)
      self.schedule_npc_message(npc_name, 'STOP', delay=1.4, record=False)
      self.schedule_npc_message(npc_name, 'STOP', delay=1.8, record=False)
      self.schedule_npc_message(npc_name, 'ok', delay=3.6, record=False)
      self.schedule_npc_message(npc_name, 'it\'s just', delay=5.0, record=False)
      self.schedule_npc_message(npc_name, 'i have something to say', delay=6.5, record=False)
      self.schedule_npc_message(npc_name, 'and i think you know what it is', delay=8.9, record=False)
      self.schedule_npc_message(npc_name, 'okay here i go', delay=11.0, record=False)
      self.schedule_npc_message(npc_name, 'SIXTY NINE', delay=14.0, record=False)
      self.schedule_npc_message(npc_name, 'yeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', delay=20.0, record=True)
    elif count == 419:
      self.npc_message(npc_name, 'HELLO')
      self.schedule_npc_message(npc_name, 'it\'s me again', delay=1.2, record=False)
      self.schedule_npc_message(npc_name, 'i guess y\'all are going for the', delay=3.0, record=False)
      self.schedule_npc_message(npc_name, 'HIGH score', delay=4.5, record=False)
      self.schedule_npc_message(npc_name, 'ha ha ha get it', delay=6.8, record=False)
      self.schedule_npc_message(npc_name, 'cuz imma post the weed number now', delay=8.5, record=False)
      self.schedule_npc_message(npc_name, 'ok then', delay=11.0, record=False)
      self.schedule_npc_message(npc_name, '420', delay=14.5, record=False)
      self.schedule_npc_message(npc_name, 'pls don\'t stone me', delay=16.0, record=True)

  def automate_human(self, trigger_count):
    npc_name = 'Twitchy Chat'
    if random.random() < .7:
      self.schedule_npc_message(
          npc_name, ': ' + str(trigger_count + random.choice([-1, 0, 1, 1, 1, 2])),
          delay=.8, retrigger=False)
    else:
      self.schedule_npc_message(
          npc_name, str(trigger_count + random.choice([1, 1, 2, 2, 3])) + ' next', delay=.4)

  ## Utility methods

  def info(self, message):
    self.respond({'type': 'info', 'message': message})

  def debug(self, message):
    if True:
      self.respond({'type': 'debug', 'message': message})

  def status(self, message):
    ## Accepts HTML input
    self.respond({'type': 'status', 'message': message})

  def score(self, score):
    self.respond({'type': 'best', 'score': score, 'goal': GOAL})

  def npc_message(self, sender, message, retrigger=False):
    """Send a chat message on behalf of an NPC.

    Note that messages dispatched through this trigger will still occur even if
    this consumer's end user disconnects.

    Args:
      sender: A display name for the NPC.
      message: Content of the NPC message (supports HTML)
      retrigger: If True, this message can potentially trigger other automated
          responses, or even advance the game state.
    """
    self.broadcast({
        'type': 'chat', # if retrigger else 'nontriggering-chat',
        'sender': sender,
        'sender_id': sender,
        'message': message,
        'id': random_id(),
    })

  ## Thread management
  #
  # Things that happen on a delay are managed by threads. Each such thread is
  # roughly serialized as (function, time, args), where time is the absolute
  # time at which the function call will actually take place. In particular,
  # the collection of serialized threads is also written to the database (as
  # part of the game state object) to allow resumption of time-delay tasks in
  # the event that the leader consumer changes between when a task is scheduled
  # and when it is supposed to happen.
  npc_threads = []
  npc_threads_db = []

  def schedule_npc_message(
      self, npc_name, message, delay, retrigger=False, record=True):
    npc_thread = threading.Timer(
        delay, self.npc_message,
        args=(npc_name, message), kwargs={'retrigger': retrigger})
    self.npc_threads.append(npc_thread)
    absolute_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    npc_thread.start()
    self.npc_threads_db.append({
        'npc_name': npc_name, 'message': message,
        'time': absolute_time, 'retrigger': retrigger
    })
    if record:
      self.record_npc_threads()

  def schedule_npc_routine(self, function, delay, record=True, args=None, kwargs=None):
    npc_thread = threading.Timer(delay, function, args=args, kwargs=kwargs)
    self.npc_threads.append(npc_thread)
    absolute_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    npc_thread.start()
    self.npc_threads_db.append({
        'function': function.__name__, 'time': absolute_time,
        'args': args, 'kwargs': kwargs,
    })
    if record:
      self.record_npc_threads()

  def record_npc_threads(self):
    now = datetime.datetime.now()
    self.npc_threads_db = [params for params in self.npc_threads_db
                           if params['time'] > now]
    with transaction.atomic():
      self.game_state.refresh_from_db()
      self.game_state.npc_threads = pickle.dumps(self.npc_threads_db)
      self.game_state.save()
    self.npc_threads = [thread for thread in self.npc_threads if thread.is_alive()]

  def clear_npc_threads(self, db=True):
    for thread in self.npc_threads:
      if thread.is_alive():
        thread.cancel()
    self.npc_threads = []
    self.npc_threads_db = []
    if db:
      self.record_npc_threads()

  def load_npc_threads(self):
    self.game_state.refresh_from_db()
    if not bool(self.game_state.npc_threads):
      return
    npc_thread_params = pickle.loads(self.game_state.npc_threads)
    for params in npc_thread_params:
      if (params['time'] - datetime.datetime.now()).total_seconds() < -1:
        continue
      if 'message' in params:
        self.schedule_npc_message(
            params['npc_name'], params['message'],
            max((params['time'] - datetime.datetime.now()).total_seconds(), 0),
            retrigger=params['retrigger'], record=False)
      else:
        self.schedule_npc_routine(
            getattr(self, params['function']),
            max((params['time'] - datetime.datetime.now()).total_seconds(), 0),
            args=params['args'], kwargs=params['kwargs'],
            record=False)
    self.record_npc_threads()


CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz012345679-_'

def random_id():
  return ''.join(random.choices(CHARS, k=8))

def select_owl_answer(n):
  if n < 100:
    return random.randint(max(1, n - 4), min(100, n + 8))
  else:
    return random.randint(1, n + 8)

def construct_arithmetic_question(target_answer):
  a = random.randint(1, target_answer - 3)
  b = random.randint(1, target_answer - a)
  return f'What\'s {a} + {b} + {target_answer - a - b}?', target_answer

def construct_palindrome():
  d = str(random.randint(101, 998))
  b = d[-1::-1]
  if random.random() < .5:
    return int(d + b)
  else:
    return int(d + str(random.randint(0, 9)) + b)

def construct_nonpalindrome():
  thing = construct_palindrome()
  return thing + (
      random.choice([-1, 1] * random.randint(1, 5) * 10 ** random.randint(0, 2)))

def construct_palindrome_question(unused_target_answer):
  a = construct_palindrome()
  b = construct_nonpalindrome()
  c = construct_nonpalindrome()
  y = ', '.join(random.sample([str(a), str(b), str(c)], 3))
  return f'Which of the following is a palindrome? {y}', a

def construct_counting_question(target_answer):
  word_bank = (
      'zero one two three four five six seven eight nine '
      'ten eleven twelve thirteen fourteen fifteen sixteen '
      'seventeen eighteen nineteen twenty thirty forty fifty').split(' ')
  if target_answer < 70:
    words = ' '.join(random.choices(word_bank, k=target_answer))
    return f'How many words are in the following string: {words}', target_answer
  else:
    word_list, count = [], 0
    while count < target_answer - 5:
      new_word = random.choice(word_bank)
      word_list.append(new_word)
      count += len(new_word)
    words = ' '.join(word_list)
    return f'How many letters are in the following string: {words}', count

def construct_binary_question(target_answer):
  text = bin(target_answer)
  return f'What decimal number is represented by {text[2:]} in binary?', target_answer

PRIMES = [
    1, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79,
    83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157,
    163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239,
    241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331,
    337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421,
    431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509,
    521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613,
    617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709,
    719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821,
    823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919,
    929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997
]

NOT_PRIMES = [
    not_prime for not_prime in [
        p * q * r
        for p in PRIMES[:20]
        for q in PRIMES[2:20]
        for r in PRIMES[4:]
    ] if not_prime > 100 and not_prime < 1000
]

def construct_primality_question(target_answer):
  p = random.choice(PRIMES[25:])
  q, r, s, t = random.sample(NOT_PRIMES, 4)
  numbers = ', '.join(map(str, random.sample([p, q, r, s, t], 5)))
  return f'Which of the following numbers is a prime: {numbers}', p

def construct_factoring_question(target_answer):
  answer = random.choice(PRIMES[2:])
  prompt = answer
  while prompt < 200:
    prompt *= random.randint(2, min(answer - 1, 30))
  return f'What\'s the largest prime factor of {prompt}?', answer

def construct_quiz_question(target_answer):
  if target_answer <= 100:
    min_q_range = max(1, target_answer - 6)
  else:
    min_q_range = 1
  max_q_range = max(int(target_answer * 1.2) + 2, min_q_range + 1)
  item = random.choice(QuizbOwlQuestion.objects.filter(
      answer__range=(min_q_range, max_q_range)))
  return item.question, item.answer

def w2n(text):
  return _w2n.word_to_num(text)

def n2w(value):
  return num2words(value)

@require_puzzle_access
def leaderboard_view(request):
  scores = CountingGameState.objects.values('session__team__name') \
    .annotate(high_score=Max('high_score')) \
    .order_by('-high_score')
  leaderboard, current_rank = [], 1
  if scores:
    leaderboard.append((
        current_rank, scores[0]['session__team__name'], scores[0]['high_score']))
    for line in scores[1:]:
      team_name, high_score = line['session__team__name'], line['high_score']
      if high_score < leaderboard[-1][2]:
        current_rank = len(leaderboard) + 1
      leaderboard.append((current_rank, team_name, high_score))
  return render(request, 'hunt/special_puzzles/counting/leaderboard.html', {
      'leaderboard': leaderboard,
  })
