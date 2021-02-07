import collections
import csv
import json
import datetime

import requests
from django.db import transaction
from django.db.models import Q

import spoilr.actions
import spoilr.signals_register as signals
from spoilr.signals import emit

from spoilr.models import *
from hunt.models import *
from hunt.constants import *

import hunt.interactions as interactions

import logging
logger = logging.getLogger(__name__)

def force_unlock(utime=None, teams=None):
    if not teams:
        teams = Team.objects.all()
    spoilr.actions.set_in_setup()
    for team in teams:
        unlock_puzzles(team, utime)
        logger.info('Unlocked %s' % (team.name))
    spoilr.actions.set_done_setup()


def start_mmo_interaction(team=None, reason=None):
    interaction = Interaction.objects.get(url=MMO_UNLOCK_INTERACTION)
    teams = []
    if team:
        teams = [team]
    else:
        teams = Team.objects.all()
    for t in teams:
        spoilr.actions.release_interaction(t, interaction, reason=None, utime=None)

def finish_mmo_interaction(team):
    interaction = Interaction.objects.get(url=MMO_UNLOCK_INTERACTION)
    spoilr.actions.interaction_accomplished(team, interaction)


def unlock_mmo():
    setting = Y2021Settings.objects.get_or_create(name='mmo_globally_unlocked')[0]
    setting.value = 'TRUE'
    setting.save()
    spoilr.actions.clear_cache(None)
    start_mmo_interaction()

def disable_mmo(utime=None):
    setting = Y2021Settings.objects.get_or_create(name='mmo_disabled')[0]
    setting.value = 'TRUE'
    setting.save()
    spoilr.actions.set_in_setup()
    for pa in PuzzleAccess.objects.filter(found=False).order_by('team'):
        send_to_team_log = True
        if pa.puzzle.round.y2021rounddata.tempest_id in [INFINITE_TEMPLATE_ROUND, BACKUP_ROUND, INFRA_ROUND]:
            send_to_team_log = False
        spoilr.actions.find_puzzle(pa.team, pa.puzzle, team_log=send_to_team_log)
    spoilr.actions.set_done_setup()
    spoilr.actions.clear_cache(None)

def mmo_disabled():
    if settings.POSTHUNT:
        return True
    setting = Y2021Settings.objects.get_or_create(name='mmo_disabled')[0]
    return setting.value == 'TRUE'

def get_mmo_unlocked(team, for_unlocks=False):
    if InteractionAccess.objects.filter(team=team, interaction__url=MMO_UNLOCK_INTERACTION, accomplished=True).exists():
        return True
    return False

def update_juice(team):
    old_global, old_round = team.y2021teamdata.get_juice()

    all_rounds = {round.tempest_id: round for round in Y2021RoundData.objects.all()}
    global_juice = 0
    calculated_round_juice = collections.defaultdict(int)
    for round_id, puzzle_id in team.solved_puzzles.filter(is_meta=False).values_list('round__y2021rounddata__tempest_id', 'y2021puzzledata__tempest_id'):
        if puzzle_id == EVENTS_BONUS:
            global_juice += EVENTS_BONUS_JUICE
            continue
        if puzzle_id == INFINITE_META:
            round_id = INFINITE_TEMPLATE_ROUND
        round = all_rounds[round_id]
        global_juice += round.outer_points_granted
        calculated_round_juice[round_id] += round.round_points_granted - round.outer_points_granted
    calculated_round_juice[INFINITE_ROUND] = calculated_round_juice[INFINITE_TEMPLATE_ROUND]
    round_juice = {}
    for r in all_rounds.keys():
        if r in [INTRO_ROUND, ATHLETICS_ROUND, EVENTS_ROUND]:
            continue
        if r in calculated_round_juice:
            round_juice[r] = calculated_round_juice[r]
        else:
            round_juice[r] = 0
    utime = now()

    for box in JuiceBox.objects.filter(active=True).filter(Q(team__isnull=True)|Q(team=team)).filter(Q(unlock_time__isnull=True)|Q(unlock_time__lte=utime)).select_related('round__y2021rounddata'):
        if box.round:
            round_juice[box.round.y2021rounddata.tempest_id] += box.juice
        else:
            global_juice += box.juice

    sch = JuiceSchedule.objects.filter(active=True).filter(timestamp__lte=now()).order_by('-timestamp').first()
    if sch:
        def rectify(global_juice, round_juice, target, tid):
            if target is not None:
                J = round_juice[tid] + global_juice
                round_juice[tid] = max(J, (J + target) / 2) - global_juice
        rectify(global_juice, round_juice, sch.students_juice, STUDENTS_ROUND)
        rectify(global_juice, round_juice, sch.green_juice, GREEN_ROUND)
        rectify(global_juice, round_juice, sch.infinite_juice, INFINITE_ROUND)
        rectify(global_juice, round_juice, sch.nano_juice, NANO_ROUND)
        rectify(global_juice, round_juice, sch.stata_juice, STATA_ROUND)
        rectify(global_juice, round_juice, sch.clusters_juice, CLUSTERS_ROUND)
        rectify(global_juice, round_juice, sch.tunnels_juice, TUNNELS_ROUND)
        rectify(global_juice, round_juice, sch.real_infinite_juice, INFINITE_TEMPLATE_ROUND)
    if INFINITE_TEMPLATE_ROUND in round_juice:
        round_juice[INFINITE_ROUND] = round_juice[INFINITE_TEMPLATE_ROUND]
    team.y2021teamdata.set_juice(global_juice, round_juice)
    new_global, new_round = team.y2021teamdata.get_juice()
    changed = False
    if old_global != new_global or old_round != new_round:
        changed = True
    return changed, (new_global, new_round)

def unlock_puzzle(team, puzzle, utime=None):
    send_to_team_log = True
    if puzzle.round.y2021rounddata.tempest_id in [INFINITE_TEMPLATE_ROUND, BACKUP_ROUND, INFRA_ROUND]:
        send_to_team_log = False
    spoilr.actions.release_puzzle(team, puzzle, utime=utime, team_log=send_to_team_log)
    if puzzle.round.y2021rounddata.tempest_id in [INTRO_ROUND, EVENTS_ROUND, INFRA_ROUND] or mmo_disabled():
        spoilr.actions.find_puzzle(team, puzzle, utime=utime, team_log=send_to_team_log)
    spoilr.actions.clear_cache(team)

def discover_puzzle(team, puzzle, utime=None):
    send_to_team_log = True
    if puzzle.round.y2021rounddata.tempest_id in [INFINITE_TEMPLATE_ROUND, BACKUP_ROUND, INFRA_ROUND]:
        send_to_team_log = False
    return spoilr.actions.find_puzzle(team, puzzle, utime=utime, team_log=send_to_team_log)


def unlock_unlocks(team):
    import hunt.mmo_unlock as mu

    for pzzl in Puzzle.objects.filter(y2021puzzledata__unlock_req__isnull=False).exclude(puzzleaccess__team=team):
        unlocks = pzzl.y2021puzzledata.unlock_req.split(',')
        unlockPuzzle = True
        for unlock in unlocks:
            result = mu.get_unlock_state(team, unlock)
            if not result or result['status'] == 'LOCKED':
                unlockPuzzle = False
        if unlockPuzzle:
            unlock_puzzle(team, pzzl)


def unlock_puzzles(team, utime=None):
    changed, (global_juice, round_juice) = update_juice(team)
    mmo_unlocked = get_mmo_unlocked(team, True)

    for rnd in Round.objects.exclude(roundaccess__team=team).select_related('y2021rounddata'):
        if rnd.y2021rounddata.tempest_id not in [INTRO_ROUND] and not mmo_unlocked:
            continue
        tr_juice = global_juice
        if str(rnd.y2021rounddata.tempest_id) in round_juice:
            tr_juice += round_juice[str(rnd.y2021rounddata.tempest_id)]
        if rnd.y2021rounddata.points_required <= tr_juice:
            send_to_team_log = True
            if rnd.y2021rounddata.tempest_id in [INFINITE_TEMPLATE_ROUND, BACKUP_ROUND, INFRA_ROUND]:
                send_to_team_log = False
            spoilr.actions.release_round(team, rnd, utime=utime, team_log=send_to_team_log)

    for pzzl in (Puzzle.objects
        .filter(round__in=team.rounds.all().exclude(url='infinite'))
        .exclude(puzzleaccess__team=team)
        .select_related('y2021puzzledata', 'round', 'round__y2021rounddata')
    ):
        rid = str(pzzl.round.y2021rounddata.tempest_id)
        unlockPuzzle = False
        if pzzl.y2021puzzledata.points_req is not None:
            if pzzl.round.y2021rounddata.points_required + pzzl.y2021puzzledata.points_req <= global_juice + round_juice[rid]:
                unlockPuzzle = True
        if pzzl.y2021puzzledata.feeder_req is not None:
            if team.solved_puzzles.filter(y2021puzzledata__feeder_tag=pzzl.y2021puzzledata.feeder_tag).count() >= pzzl.y2021puzzledata.feeder_req:
                unlockPuzzle = True
        if pzzl.y2021puzzledata.feeder_tag == 'special-meta':
            # Dorm Row Meta
            if pzzl.y2021puzzledata.tempest_id == DORM_ROW_METAMETA:
                if team.solved_puzzles.filter(y2021puzzledata__tempest_id__in=DORM_ROW_METAS).count() == len(DORM_ROW_METAS):
                    unlockPuzzle = True
            # Student Center Meta
            if pzzl.y2021puzzledata.tempest_id == STUDENT_CENTER_METAMETA:
                if team.solved_puzzles.filter(y2021puzzledata__tempest_id__in=STUDENT_CENTER_METAS).count() == len(STUDENT_CENTER_METAS):
                    unlockPuzzle = True
            # Athletics Meta
            if pzzl.y2021puzzledata.tempest_id == ATHLETICS_METAMETA:
                if team.solved_puzzles.filter(y2021puzzledata__tempest_id__in=ATHLETICS_METAS).count() == len(ATHLETICS_METAS):
                    unlockPuzzle = True
            # Events Post-Meta
            if pzzl.y2021puzzledata.tempest_id == EVENTS_METAMETA:
                if team.solved_puzzles.filter(y2021puzzledata__tempest_id=EVENTS_META).exists():
                    unlockPuzzle = True

        if pzzl.y2021puzzledata.unlock_time is not None:
            if pzzl.y2021puzzledata.unlock_time < now():
                unlockPuzzle = True
        if pzzl.y2021puzzledata.required_available_puzzle is not None:
            prereq = pzzl.y2021puzzledata.required_available_puzzle
            if team.puzzles.filter(id=prereq.id).exists():
                unlockPuzzle &= True
            else:
                unlockPuzzle &= False

        if pzzl.y2021puzzledata.level is not None:
            prereq = NANO_LEVELS[pzzl.y2021puzzledata.level]
            bypassNano = Y2021Settings.objects.get_or_create(name='reveal_nano')[0].value == 'TRUE'
            if prereq and not bypassNano:
                if team.solved_puzzles.filter(y2021puzzledata__tempest_id=prereq).exists():
                    unlockPuzzle &= True
                else:
                    unlockPuzzle &= False
        if unlockPuzzle:
            unlock_puzzle(team, pzzl, utime)

    try:
        infiniteMeta = Puzzle.objects.get(y2021puzzledata__tempest_id=INFINITE_META)
        if infiniteMeta.y2021puzzledata.points_req <= global_juice + round_juice[str(INFINITE_TEMPLATE_ROUND)]:
            unlock_puzzle(team, infiniteMeta, utime)
    except:
        pass

    if changed:
        _, new_juice = update_juice(team)
    else:
        changed, new_juice = update_juice(team)
        if changed:
            logger.error("ERROR: JUICE CHANGED AFTER UNLOCK")
    if changed:
        emit(signals.juice_update_message, team, new_juice)

    unlock_unlocks(team)

def unlock_tick():
    lastTime = None
    nowTime = now()
    tick_obj = Y2021Settings.objects.get_or_create(name='last_tick')[0]
    if tick_obj.value:
        lastTime = datetime.datetime.fromtimestamp(float(tick_obj.value), tz=datetime.timezone.utc)
    tick_obj.value = str(nowTime.timestamp())

    for team in Team.objects.all():
        for pzzl in Puzzle.objects.filter(round__in=team.rounds.all().exclude(url='infinite'), y2021puzzledata__unlock_time__isnull=False).exclude(puzzleaccess__team=team):
            if pzzl.y2021puzzledata.unlock_time < nowTime:
                unlock_puzzle(team, pzzl, nowTime)

        changed, new_juice = update_juice(team)
        if changed:
            unlock_puzzles(team)
            emit(signals.juice_update_message, team, new_juice)
        for unlock in MMOUnlock.objects.filter(unlock_time__isnull=False):
            if lastTime and lastTime > unlock.unlock_time:
                continue
            if nowTime > unlock.unlock_time:
                emit(signals.get_state_message, team, unlock.unlock_id)
    tick_obj.save()
    return True

def puzzle_solved(team, puzzle):
    if puzzle.y2021puzzledata.infinite:
        puzzle = puzzle.y2021puzzledata.parent
        try:
            pa = PuzzleAccess.objects.get(team=team, puzzle=puzzle)
        except PuzzleAccess.DoesNotExist:
            return
        if pa.solved:
            spoilr.actions.clear_cache(team)
            return
        pa.solved = True
        pa.solved_time = datetime.datetime.now()
        pa.save()

    p21 = puzzle.y2021puzzledata
    if not p21.hint_stuck_duration:
        solve_count = PuzzleAccess.objects.filter(puzzle=puzzle, solved=True).order_by('solved_time').count()
        if solve_count >= p21.hint_solve_threshold:
            worst_time = None
            for pa in PuzzleAccess.objects.filter(puzzle=puzzle, solved=True).order_by('solved_time')[:p21.hint_solve_threshold]:
                dt = pa.solved_time - pa.found_timestamp
                if not worst_time or dt > worst_time:
                    worst_time = dt
            p21.hint_stuck_duration = worst_time
            p21.save()

    unlock_puzzles(team)
    interactions.puzzle_solved(team, puzzle)
    spoilr.actions.clear_cache(team)

@transaction.atomic
def get_or_create_infinite(tempest_id):
    if Puzzle.objects.filter(y2021puzzledata__tempest_id=tempest_id).exists():
        return Puzzle.objects.get(y2021puzzledata__tempest_id=tempest_id)
    infid = tempest_id - INFINITE_BASE_ID
    INFINITES = {}
    with open(INFINITE_PATH) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        for puzzleInfo in reader:
            if len(puzzleInfo) == 0:
                continue
            INFINITES[int(puzzleInfo[0])] = puzzleInfo
    if infid not in INFINITES:
        return None
    pi = INFINITES[infid]
    base_puzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=pi[1])
    puzzle = Puzzle()
    puzzle.round = Round.objects.get(y2021rounddata__tempest_id=INFINITE_ROUND)
    puzzle.url = 'infinite-%d' % (infid)
    puzzle.name = 'Puzzle %d: %s' % (infid, base_puzzle.name)
    puzzle.answer = pi[2]
    puzzle.credits = base_puzzle.credits
    puzzle.order = infid
    puzzle.is_meta = False
    puzzle.save()
    puzzle2021 = Y2021PuzzleData()
    puzzle2021.puzzle = puzzle
    puzzle2021.tempest_id = tempest_id
    puzzle2021.obfuscated_id = obfuscate(puzzle2021.tempest_id)
    puzzle2021.infinite = True
    puzzle2021.parent = base_puzzle
    puzzle2021.save()
    return puzzle

def get_infinite(tempest_id):
    if Puzzle.objects.filter(y2021puzzledata__tempest_id=tempest_id).exists():
        return Puzzle.objects.get(y2021puzzledata__tempest_id=tempest_id)
    return get_or_create_infinite(tempest_id)

def get_puzzle(tempest_id):
    try:
        return Puzzle.objects.get(y2021puzzledata__tempest_id=tempest_id)
    except Puzzle.DoesNotExist:
        pass
    if tempest_id >= INFINITE_BASE_ID:
        return get_infinite(tempest_id)

def get_puzzle_by_name(slug):
    try:
        return Puzzle.objects.select_related(
            'round', 'y2021puzzledata', 'y2021puzzledata__parent').get(url=slug)
    except Puzzle.DoesNotExist:
        pass
    if slug.startswith('infinite-'):
        try:
            return get_infinite(INFINITE_BASE_ID + int(slug[9:]))
        except:
            return None

def get_puzzle_access(team, puzzle):
    if not puzzle:
        return None
    try:
        return PuzzleAccess.objects.get(team=team, puzzle=puzzle)
    except PuzzleAccess.DoesNotExist:
        pass
    if puzzle.y2021puzzledata.infinite and PuzzleAccess.objects.filter(team=team, puzzle=puzzle.y2021puzzledata.parent, found=True).exists():
        return PuzzleAccess(team=team, puzzle=puzzle)

def interaction_released(team, interaction):
    from hunt.notifications import notify_mmo_unlocked
    if interaction.url == MMO_UNLOCK_INTERACTION:
        notify_mmo_unlocked(team)
    else:
        spoilr.actions.clear_cache(team)

def interaction_finished(team, interaction):
    if interaction.url == MMO_UNLOCK_INTERACTION:
        unlock_puzzles(team)
    spoilr.actions.clear_cache(team)

def start_team(team, utime=None):
    update_juice(team)
    spoilr.actions.release_round(team, Round.objects.get(y2021rounddata__tempest_id=INTRO_ROUND), utime=utime)
    for pzzl in INTRO_PUZZLES:
        puzzle = Puzzle.objects.get(y2021puzzledata__tempest_id=pzzl)
        spoilr.actions.release_puzzle(team, puzzle, utime=utime)
        spoilr.actions.find_puzzle(team, puzzle, utime=utime)
    spoilr.actions.clear_cache(team)
    unlock_unlocks(team)

def start_all(utime=None, teams=None):
    intro_round = Round.objects.get(y2021rounddata__tempest_id=INTRO_ROUND)
    puzzles = [Puzzle.objects.get(y2021puzzledata__tempest_id=i) for i in INTRO_PUZZLES]
    if not teams:
        teams = Team.objects.all()
    count = 0
    total = teams.count()
    spoilr.actions.set_in_setup()
    for team in teams:
        count += 1
        update_juice(team)
        spoilr.actions.release_round(team, intro_round, utime=utime)
        for puzzle in puzzles:
            spoilr.actions.release_puzzle(team, puzzle, utime=utime)
            spoilr.actions.find_puzzle(team, puzzle, utime=utime)
        spoilr.actions.clear_cache(team)
        unlock_unlocks(team)
        logger.info('%03d/%03d: Started %s' % (count, total, team.name))
    spoilr.actions.set_done_setup()
    spoilr.actions.clear_cache(None)
    logger.info('Started %d teams.' % (count))

def launch_hunt(teams=None):
    setting = Y2021Settings.objects.get_or_create(name='is_it_hunt_yet')[0]
    setting.value = 'TRUE'
    setting.save()
    if not teams:
        teams = Team.objects.all()
    from hunt.notifications import notify_hunt_launched
    for team in teams:
        notify_hunt_launched(team)

def puzzle_released(team, puzzle):
    spoilr.actions.clear_cache(team)

def round_released(team, round):
    spoilr.actions.clear_cache(team)

def puzzle_found(team, puzzle):
    if puzzle.y2021puzzledata.tempest_id == NANO_AUTO:
        spoilr.actions.solve_puzzle(team, puzzle)
    interactions.puzzle_found(team, puzzle)
    spoilr.actions.clear_cache(team)
