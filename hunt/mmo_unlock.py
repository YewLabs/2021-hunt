from django.db import models, transaction

import spoilr.actions
import hunt.models
import spoilr.models as smodels
import spoilr.log as log
from spoilr.signals import emit
import spoilr.signals_register as signals
from django.urls import reverse

from spoilr.models import Puzzle, Round, PuzzleAccess, RoundAccess, InteractionAccess, now
from hunt.models import *
from hunt.actions import *
from hunt.constants import *

import logging
logger = logging.getLogger(__name__)

from django_redis import get_redis_connection

def set_unlock_cache(data):
    try:
        key = 'unlock-%03d-%s' % (data['team'], data['unlock'])
        rcache = get_redis_connection()
        newValue = json.dumps(data).encode('utf-8')
        oldValue = rcache.getset(key, newValue)
        return oldValue != newValue
    except:
        return True

def get_unlock_state(team, unlock):
    key = 'unlock-%03d-%s' % (team.y2021teamdata.tempest_id, unlock)
    rcache = get_redis_connection()
    res = rcache.get(key)
    if res:
        return json.loads(res)
    return None

def set_unlock_value(team, uid, value):
    data = {
        'team': team.y2021teamdata.tempest_id,
        'unlock': uid,
        'status': 'LOCKED',
        'cache': True
    }
    if value:
        data['status'] = 'SOLVED'
    set_unlock_cache(data)
    emit(signals.unlock_update_message, team, uid, data)

def get_unlock_value(team, uid):
    result = get_unlock_state(team, uid)
    if result:
        return result['status'] == 'SOLVED'
    return False

def send_update(team, unlock, status, data=None, extraID=None, cache=True, local=False):
    msg = {
        'team': team.y2021teamdata.tempest_id,
        'unlock': unlock,
        'status': status,
        'cache': cache
    }
    if extraID:
        msg['discoveryID'] = extraID
    if data:
        msg['data'] = data
    if set_unlock_cache(msg) or local:
        if not SKIP_UNLOCK_LOG:
            logger.info('Sending Update: %s' % (msg))
        if not local:
            emit(signals.unlock_update_message, team, unlock, msg)
        return [msg]
    return []

def unlock_saved(unlock):
    for team in Team.objects.all():
        get_state(team, unlock.unlock_id)
        unlock_unlocks(team)

def update_east_campus(team, puzzle_access=None, round_access=None):
    if round_access and round_access.round.url in EAST_CAMPUS_UNLOCK_ROUNDS:
        return True
    if puzzle_access and puzzle_access.puzzle.y2021puzzledata.tempest_id in EAST_CAMPUS_UNLOCK_PUZZLES:
        return True
    return False

def update_main_campus(team, puzzle_access=None, round_access=None):
    if round_access and round_access.round.url in MAIN_CAMPUS_UNLOCK_ROUNDS:
        return True
    if puzzle_access and puzzle_access.puzzle.y2021puzzledata.tempest_id in MAIN_CAMPUS_UNLOCK_PUZZLES:
        return True
    return False

def update_west_campus(team, puzzle_access=None, round_access=None):
    if round_access and round_access.round.url in WEST_CAMPUS_UNLOCK_ROUNDS:
        return True
    if puzzle_access and puzzle_access.puzzle.y2021puzzledata.tempest_id in WEST_CAMPUS_UNLOCK_PUZZLES:
        return True
    return False

def update_campus(team, puzzle_access=None, round_access=None, local=False):
    updates = []
    if update_east_campus(team, puzzle_access, round_access):
        updates += send_update(team, 'east-campus-access', 'SOLVED', local)
    if update_main_campus(team, puzzle_access, round_access):
        updates += send_update(team, 'main-campus-access', 'SOLVED', local)
    if update_west_campus(team, puzzle_access, round_access):
        updates += send_update(team, 'west-campus-access', 'SOLVED', local)
    return updates

def juice_update(team, xunlock=None, cache=True, local=False):
    if xunlock:
        unlocks = [xunlock]
    else:
        unlocks = MMOUnlock.objects.filter(juice__isnull=False).select_related('round', 'round__y2021rounddata')
    unlocked_rounds = set(RoundAccess.objects.filter(team=team).values_list('round_id', flat=True))
    updates = []
    for unlock in unlocks:
        status = 'LOCKED'
        if unlock.round:
            baseThreshold = unlock.round.y2021rounddata.points_required
            currentJuice = team.y2021teamdata.get_juice(unlock.round.y2021rounddata.tempest_id)
            if currentJuice and currentJuice >= unlock.juice + baseThreshold:
                status = 'AVAILABLE'
            if unlock.round_id not in unlocked_rounds:
                status = 'LOCKED'
        else:
            if team.y2021teamdata.get_juice()[0] >= unlock.juice:
                status = 'AVAILABLE'
        if unlock.unlock_time and status == 'LOCKED' and (now() > unlock.unlock_time):
            status = 'AVAILABLE'
        if unlock.force:
            status = unlock.force
        updates += send_update(team, unlock.unlock_id, status, None, None, cache, local)
    if not xunlock:
        updates += update_campus(team, local=local)
    return updates

def juice_update_wrapper(team, juice):
    return juice_update(team)

def puzzle_update(team, puzzle, xunlock=None, always_cache=True, local=False):
    discoverID = None
    if puzzle.round.url == 'infinite-template':
        discoverID = puzzle.y2021puzzledata.tempest_id
    status = 'LOCKED'
    try:
        access = get_puzzle_access(team, puzzle)
    except PuzzleAccess.DoesNotExist:
        access = None
    if access:
        status = 'AVAILABLE'
        if access.found:
            status = 'FOUND'
        if access.solved:
            status = 'SOLVED'
    puzzleURL = reverse('puzzle_view', kwargs={'puzzle': puzzle.url})
    unlockPuzzleURL = reverse('find_puzzle', kwargs={'puzzle': puzzle.url, 'puzzle_id': puzzle.y2021puzzledata.obfuscated_id})

    if xunlock:
        unlocks = [xunlock]
    elif puzzle.y2021puzzledata.infinite:
        infiniteID = puzzle.y2021puzzledata.infinite_id
        unlocks = [MMOUnlock(unlock_id='infinite%d' % (infiniteID), puzzle=puzzle)]
    else:
        unlocks = MMOUnlock.objects.filter(puzzle=puzzle)
    globalStatus = status
    updates = []
    for unlock in unlocks:
        data = '/'
        status = globalStatus
        cache = True
        if unlock.unlock_time and status == 'LOCKED' and (now() > unlock.unlock_time):
            status = 'AVAILABLE'
        if not always_cache:
            if status == 'LOCKED':
                cache = False
        if unlock.force:
            status = unlock.force
            cache = True
        if status != 'LOCKED':
            data = puzzleURL
        if status == 'AVAILABLE':
            data = unlockPuzzleURL
        name = ''
        if puzzle.round.url in NPC_NAMES:
            name = NPC_NAMES[puzzle.round.url]
            if puzzle.round.url == 'infinite' and puzzle.y2021puzzledata.parent is not None:
                type_id = puzzle.y2021puzzledata.parent.y2021puzzledata.tempest_id
                if type_id in INFINITE_NAMES:
                    name = INFINITE_NAMES[type_id]
        if status != 'LOCKED':
            try:
                name = PuzzleExtraData.objects.get(puzzle=puzzle, name='npc_name').data
            except PuzzleExtraData.DoesNotExist:
                pass
        data += ':' + name
        if status == 'SOLVED':
            if len(unlock.solve_text) > 0:
                data += ':' + unlock.solve_text
        else:
            if len(unlock.presolve_text) > 0:
                data += ':' + unlock.presolve_text
        updates += send_update(team, unlock.unlock_id, status, data, discoverID, cache, local)
    if not xunlock:
        updates += update_campus(team, puzzle_access=access, local=local)
    return updates

def round_update(team, round, xunlock=None, always_cache=True, local=False):
    try:
        access = RoundAccess.objects.get(team=team, round=round)
    except RoundAccess.DoesNotExist:
        access = None
    status = 'LOCKED'
    if access:
        status = 'AVAILABLE'
    roundURL = reverse('round_view', kwargs={'round': round.url if round.url != 'nano' else 'giga'})
    if xunlock:
        unlocks = [xunlock]
    else:
        unlocks = MMOUnlock.objects.filter(round=round)
    globalStatus = status
    updates = []
    for unlock in unlocks:
        if unlock.juice:
            baseThreshold = round.y2021rounddata.points_required
            if team.y2021teamdata.get_juice(round.y2021rounddata.tempest_id) < unlock.juice + baseThreshold:
                continue
        data = roundURL
        status = globalStatus
        cache = True
        if unlock.unlock_time and status == 'LOCKED' and (now() > unlock.unlock_time):
            status = 'AVAILABLE'
        if not always_cache:
            if status == 'LOCKED':
                cache = False
        if unlock.force:
            status = unlock.force
            cache = True
        if status == 'SOLVED' and len(unlock.solve_text) > 0:
            data += ':' + unlock.solve_text
        updates += send_update(team, unlock.unlock_id, status, data, None, cache, local)
    if not xunlock:
        updates += update_campus(team, round_access=access, local=local)
    return updates

def time_update(team, xunlock=None, always_cache=True, local=False):
    if xunlock:
        unlocks = [xunlock]
    else:
        unlocks = MMOUnlock.objects.filter(unlock_time__isnull=False)
    updates = []
    for unlock in unlocks:
        data = ''
        status = 'LOCKED'
        if now() > unlock.unlock_time:
            status = 'AVAILABLE'
        cache = True
        if not always_cache:
            if status == 'LOCKED':
                cache = False
        if unlock.force:
            status = unlock.force
            cache = True
        updates += send_update(team, unlock.unlock_id, status, '', 0, cache, local)
    return updates

def interaction_update(team, interaction, xunlock=None, always_cache=True, local=False):
    try:
        access = InteractionAccess.objects.get(team=team, interaction=interaction, accomplished=True)
    except InteractionAccess.DoesNotExist:
        access = None
    status = 'LOCKED'
    if access:
        status = 'SOLVED'
    if xunlock:
        unlocks = [xunlock]
    else:
        unlocks = MMOUnlock.objects.filter(interaction=interaction)
    globalStatus = status
    updates = []
    for unlock in unlocks:
        data = interaction.url
        status = globalStatus
        cache = True
        if not always_cache:
            if status == 'LOCKED':
                cache = False
        if unlock.force:
            status = unlock.force
            cache = True
        updates += send_update(team, unlock.unlock_id, status, data, None, cache, local)
    return updates


def get_state(team, unlock_id, local=False):
    try:
        unlock = MMOUnlock.objects.get(unlock_id=unlock_id)
    except MMOUnlock.DoesNotExist:
        if unlock_id.startswith('infinite'):
            puzzle = get_puzzle(INFINITE_BASE_ID + int(unlock_id[8:]))
            if not puzzle:
                return []
            unlock = MMOUnlock(unlock_id=unlock_id, puzzle=puzzle)
            return puzzle_update(team, puzzle, unlock, False, local)
        elif unlock_id.startswith('endgame-'):
            if get_unlock_value(team, unlock_id):
                status = 'SOLVED'
            else:
                status = 'LOCKED'
            return send_update(team, unlock_id, status, None, None, True, local)
        else:
            return []
    if unlock.puzzle:
        return puzzle_update(team, unlock.puzzle, unlock, True, local)
    if unlock.interaction:
        return interaction_update(team, unlock.interaction, unlock, True, local)
    if unlock.juice:
        return juice_update(team, unlock, True, local)
    if unlock.round:
        return round_update(team, unlock.round, unlock, True, local)
    if unlock.unlock_time:
        return time_update(team, unlock, True, local)
    if unlock.force:
        return send_update(team, unlock.unlock_id, unlock.force, None, None, True, local)
    if unlock.unlock_id == 'east-campus-access':
        for r in team.rounds.filter(url__in=EAST_CAMPUS_UNLOCK_ROUNDS):
            return send_update(team, unlock.unlock_id, 'SOLVED', local=local)
        for p in team.puzzles.filter(y2021puzzledata__tempest_id__in=EAST_CAMPUS_UNLOCK_PUZZLES):
            return send_update(team, unlock.unlock_id, 'SOLVED', local=local)
    if unlock.unlock_id == 'main-campus-access':
        for r in team.rounds.filter(url__in=MAIN_CAMPUS_UNLOCK_ROUNDS):
            return send_update(team, unlock.unlock_id, 'SOLVED', local=local)
        for p in team.puzzles.filter(y2021puzzledata__tempest_id__in=MAIN_CAMPUS_UNLOCK_PUZZLES):
            return send_update(team, unlock.unlock_id, 'SOLVED', local=local)
    if unlock.unlock_id == 'west-campus-access':
        for r in team.rounds.filter(url__in=WEST_CAMPUS_UNLOCK_ROUNDS):
            return send_update(team, unlock.unlock_id, 'SOLVED', local=local)
        for p in team.puzzles.filter(y2021puzzledata__tempest_id__in=WEST_CAMPUS_UNLOCK_PUZZLES):
            return send_update(team, unlock.unlock_id, 'SOLVED', local=local)

    return send_update(team, unlock.unlock_id, "LOCKED", None, None, True, local)

def get_puzzle_update(team, puzzle):
    if puzzle.y2021puzzledata.infinite:
        return get_state(team, 'infinite%d' % (puzzle.y2021puzzledata.infinite_id))
    return puzzle_update(team, puzzle)

def get_global_team_state(team):
    count = 0
    allUpdates = []
    for unlock in MMOUnlock.objects.all():
        count += 1
        allUpdates += get_state(team, unlock.unlock_id, True)
    return allUpdates

def reset_global_state():
    mmo_unlocks = MMOUnlock.objects.all()
    for team in Team.objects.all():
        for unlock in mmo_unlocks:
            msg = {
                'team': team.y2021teamdata.tempest_id,
                'unlock': unlock.unlock_id,
                'status': 'LOCKED',
                'cache': True
            }
            set_unlock_cache(msg)

def get_unlock_list():
    unlocks = []
    for unlock in MMOUnlock.objects.all():
        unlocks.append(unlock.unlock_id)
    return unlocks
