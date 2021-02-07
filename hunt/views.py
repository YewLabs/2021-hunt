import json
import logging
import os
import random
import requests
import string

from django.conf import settings
from django.core.cache import cache
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.template import Template, Context
from django.utils import timezone
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required

import spoilr.actions
from spoilr.decorators import *
from spoilr.puzzle_session import puzzle_session
from spoilr.shortcuts import get_shortcuts
import puzzleviewer.utils as utils

from hunt.actions import *
import hunt.special_puzzles.unchained.generator as infinite_unchained
import hunt.special_puzzles.make_your_own_wordsearch.generator as infinite_wordsearch
import hunt.special_puzzles.library_of_images.generator as infinite_library
import hunt.special_puzzles.infinite_simulator.generator as infinite_simulator

from spoilr.models import *
from spoilr.log import discord_queue
from hunt.models import *
from hunt.constants import *
from hunt.mmo_unlock import get_unlock_value, set_unlock_value

from hunt.interactions import submission_instructions

from django.templatetags.static import static

import hashlib

def puzzle_static(puzzle, solution=False):
    if puzzle.y2021puzzledata.infinite:
        puzzle = puzzle.y2021puzzledata.parent

    if settings.USE_PUZZLE_STATIC:
        if solution:
            return '/srpuzzle/%s/solution/' % (puzzle.url)
        return '/srpuzzle/%s/' % (puzzle.url)

    v = puzzle.url
    if solution:
        v += '_solution'
    fkey = hashlib.sha256((v + '_SROOT_KEY').encode('utf-8')).hexdigest()[-16:]

    return static('puzzle_files/' + fkey + '/')

from django.utils.html import escape

def XHttpResponse(d):
    return HttpResponse(escape(d))

def XHttpResponseBadRequest(d):
    return HttpResponseBadRequest(escape(d))

def round_static(round_url, solution=False):
    if settings.USE_PUZZLE_STATIC:
        return ''

    v = round_url
    if solution:
        v += '_solution'
    fkey = hashlib.sha256(('round_' + v + '_SROOT_KEY').encode('utf-8')).hexdigest()[-16:]

    return static('puzzle_files/' + fkey + '/')

def unlock_image(puzzle):
    key = hashlib.sha256(('%s:%d' % ("SPY21_IMG", puzzle.y2021puzzledata.tempest_id)).encode('utf-8')).hexdigest()
    return static('unlock_images/' + key + '.png')

def show_solutions(team):
    return team.is_admin or team.is_special or settings.POSTHUNT

def get_extra_puzzle_context(team, puzzle):
    slug = puzzle.url
    if puzzle.y2021puzzledata.infinite:
        slug = puzzle.y2021puzzledata.parent.url

        # Call method with team and puzzle that returns a dictionary.
        if slug == 'unchained':
            return infinite_unchained.generate_context(puzzle)
        if slug == 'make-your-own-wordsearch':
            return infinite_wordsearch.generate_context(puzzle)
        if slug == 'library-of-images':
            return infinite_library.generate_context(puzzle)
        if slug == 'infinite-corridor-simulator':
            return infinite_simulator.generate_context(puzzle)

    return {}

def update_obj(team, update):
    ptime = update.publish_time.replace(tzinfo=timezone.utc).astimezone(tz=None)
    hidden = False
    if update.puzzle and not team.puzzleaccess_set.filter(puzzle=update.puzzle).exists():
        hidden = True
    return {'update': update, 'timestamp': ptime.strftime('%A at %I:%M %p %Z'), 'hidden': hidden}

def puzzleaccess_set(team):
    return team.puzzleaccess_set.select_related('team', 'puzzle', 'team__y2021teamdata', 'puzzle__y2021puzzledata').prefetch_related('puzzle__puzzleextradata_set')

def roundaccess_set(team):
    return team.roundaccess_set.select_related('team', 'round', 'round__y2021rounddata')

def puzzle_obj(access):
    ret = {'puzzle': access.puzzle, 'solved': access.solved, 'team': access.team, 'found': access.found , 'auth': access.team.y2021teamdata.auth, 'found_time': access.found_timestamp}
    if access.puzzle.y2021puzzledata.infinite:
        ret['infinite'] = True
        ret['infinite_id'] = access.puzzle.y2021puzzledata.infinite_id
    ret['extra'] = {ed.name: ed.data for ed in access.puzzle.puzzleextradata_set.all()}
    ret['uimage'] = unlock_image(access.puzzle)
    ret['uimage_small'] = ret['uimage'].replace('.png', '_small.png')
    return ret

def nano_tree(levels):
    bypassNano = Y2021Settings.objects.get_or_create(name='reveal_nano')[0].value == 'TRUE'
    if len(levels) == 0:
        return []
    allPuzzles = []
    for pa in levels[0]:
        tid = pa.puzzle.y2021puzzledata.tempest_id
        isMeta = tid in NANO_LEVELS[:-1]
        po = puzzle_obj(pa)
        level = pa.puzzle.y2021puzzledata.level
        po['indent'] = level
        po['meta'] = pa.puzzle.is_meta
        if not isMeta or not (bypassNano or pa.solved):
            allPuzzles.append(po)
        else:
            po['meta'] = True
            allPuzzles.append(po)
            allPuzzles += nano_tree(levels[1:])
    return allPuzzles

def nano_top_round_obj(ret, access):
    accesses = (puzzleaccess_set(access.team)
        .filter(puzzle__round=access.round)
        .order_by('puzzle__order'))
    NANO_NAMES = ['???', '⊥IW.giga', '⊥IW.kilo', '⊥IW.milli', '⊥IW.nano']
    ret['puzzles'] = [puzzle_obj(x) for x in accesses if x.found]
    levels = [[] for _ in NANO_LEVELS[:-1]]
    maxLevel = 1
    showIndent = False
    for pa in accesses:
        level = pa.puzzle.y2021puzzledata.level
        levels[level].append(pa)
        if pa.solved and pa.puzzle.y2021puzzledata.tempest_id in NANO_LEVELS[2:]:
            showIndent = True
            if level >= maxLevel:
                maxLevel = level + 1
    if not showIndent:
        showIndent = Y2021Settings.objects.get_or_create(name='reveal_nano')[0].value == 'TRUE'

    ret['name'] = NANO_NAMES[maxLevel]
    ret['url'] = ret['name'].split('.')[1]
    ret['all_puzzles'] = nano_tree(levels)
    ret['show_indent'] = showIndent
    return ret

def round_obj(access):
    ret = {'round': access.round, 'name': access.round.name, 'url': access.round.url}
    ret['solved'] = access.team.solved_puzzles.filter(is_meta=True, round=access.round).exists()
    juice_round = access.round.y2021rounddata.tempest_id
    if juice_round == INFINITE_ROUND:
        juice_round = INFINITE_TEMPLATE_ROUND
    juice = access.team.y2021teamdata.get_juice(juice_round)
    ret['juice'] = juice

    nextJuice = None
    nextTime = None
    hasPuzzle = False
    weirdPuzzle = False
    if access.round.url == 'nano':
        solved_nano = set(access.team.solved_puzzles
            .filter(y2021puzzledata__tempest_id__in=NANO_LEVELS[1:])
            .values_list('y2021puzzledata__tempest_id', flat=True))
    next_puzzles = Puzzle.objects.select_related('y2021puzzledata').filter(round__y2021rounddata__tempest_id=juice_round).exclude(puzzleaccess__team=access.team)
    if juice_round == INFINITE_TEMPLATE_ROUND:
        next_puzzles |= Puzzle.objects.select_related('y2021puzzledata').filter(y2021puzzledata__tempest_id=INFINITE_META).exclude(puzzleaccess__team=access.team)
    for pzzl in next_puzzles:
        hasPuzzle = True
        if pzzl.y2021puzzledata.unlock_time is not None:
            if not nextTime or pzzl.y2021puzzledata.unlock_time < nextTime:
                nextTime = pzzl.y2021puzzledata.unlock_time
        if pzzl.y2021puzzledata.points_req is None:
            continue
        juiceThreshold = access.round.y2021rounddata.points_required + pzzl.y2021puzzledata.points_req
        if juiceThreshold <= juice:
            continue
        if nextJuice == None or juiceThreshold < nextJuice:
            nextJuice = int(juiceThreshold)
        else:
            continue
        weirdPuzzle = False
        if pzzl.y2021puzzledata.level and NANO_LEVELS[pzzl.y2021puzzledata.level] not in solved_nano:
            weirdPuzzle = True

    if nextJuice and not weirdPuzzle:
        ret['next_puzzle'] = '%d JUICE' % (nextJuice)
    elif nextTime:
        ret['next_puzzle'] = timezone.localtime(nextTime).strftime("%b %d %H:%M")
    elif hasPuzzle: # and not weirdPuzzle:
        ret['next_puzzle'] = '???'
    else:
        ret['next_puzzle'] = None

    if access.round.url == 'nano':
        return nano_top_round_obj(ret, access)

    ret['all_puzzles'] = [puzzle_obj(x) for x in puzzleaccess_set(access.team)
        .filter(puzzle__round=access.round)
        .order_by('puzzle__order')]
    ret['puzzles'] = [x for x in ret['all_puzzles'] if x['found']]
    return ret

def infinite_round_obj(access, id_start=None):
    ret = round_obj(access)
    if id_start is None:
        ret['id_start'] = ''
        return ret

    all_puzzles = []
    try:
        pa = puzzleaccess_set(access.team).get(puzzle__y2021puzzledata__tempest_id=INFINITE_META)
        all_puzzles.append((None, puzzle_obj(pa), True))
    except:
        pass

    ids = [i for i in range(id_start, id_start + 20) if i >= 1 and i <= 100000]
    tempest_ids = [INFINITE_BASE_ID + i for i in ids]
    existing_puzzles = {x.y2021puzzledata.tempest_id: x for x in Puzzle.objects
        .select_related('y2021puzzledata', 'round__y2021rounddata')
        .filter(y2021puzzledata__tempest_id__in=tempest_ids)}

    puzzles = []
    access_ids = set()
    for i, tempest_id in zip(ids, tempest_ids):
        puzzle = existing_puzzles.get(tempest_id, None)
        if not puzzle: puzzle = get_infinite(tempest_id)
        if not puzzle: continue
        puzzles.append((i, puzzle))
        access_ids.add(puzzle.id)
        access_ids.add(puzzle.y2021puzzledata.parent_id)

    accesses = {x.puzzle_id: x for x in puzzleaccess_set(access.team).filter(puzzle_id__in=access_ids)}
    for i, puzzle in puzzles:
        po = None
        parent_found = False
        try:
            po = puzzle_obj(accesses[puzzle.id])
        except:
            try:
                parent_found = accesses[puzzle.y2021puzzledata.parent_id].found
                po = {'puzzle': puzzle, 'solved': False, 'team': access.team, 'found': False}
            except:
                pass
        all_puzzles.append((i, po, parent_found))

    ret['id_start'] = id_start
    ret['all_puzzles'] = all_puzzles
    return ret

def nano_round_obj(access, level=None):
    ret = round_obj(access)
    if level is None:
        return ret
    bypassNano = Y2021Settings.objects.get_or_create(name='reveal_nano')[0].value == 'TRUE'
    if bypassNano:
        accesses = puzzleaccess_set(access.team).filter(puzzle__y2021puzzledata__tempest_id__in=NANO_LEVELS[1:-1])
        prereq = [x for x in accesses]
    else:
        accesses = puzzleaccess_set(access.team).filter(puzzle__y2021puzzledata__tempest_id__in=NANO_LEVELS[1:-1])
        prereq = [x for x in accesses if x.solved]
    NANO_NAMES = ['???', '⊥IW.giga', '⊥IW.kilo', '⊥IW.milli', '⊥IW.nano']
    if level < 1 or level > len(prereq):
        ret['puzzles'] = []
        ret['nano_puzzles'] = []
        ret['name'] = NANO_NAMES[1]
        ret['url'] = ret['name'].split('.')[1]
        ret['nano_minus'] = None
        ret['nano_level'] = None
        ret['nano_plus'] = None
        if level == 1:
            p = [x for x in accesses if x.puzzle.y2021puzzledata.tempest_id == NANO_LEVELS[level]]
            if p:
                ret['nano_puzzles'] = [(puzzle_obj(p[0]), True)]
        return ret
    all_puzzles = []
    for p in prereq:
        if p.puzzle.y2021puzzledata.tempest_id == NANO_LEVELS[level]:
            all_puzzles.append((puzzle_obj(p), True))
    for p in ret['all_puzzles']:
        if p['puzzle'].y2021puzzledata.level == level:
            all_puzzles.append((p, False))
    ret['nano_puzzles'] = all_puzzles
    ret['name'] = NANO_NAMES[level]
    ret['url'] = ret['name'].split('.')[1]
    ret['nano_minus'] = level - 1 if level > 1 else None
    ret['nano_level'] = level if level != 1 else None
    ret['nano_plus'] = level + 1 if level < len(prereq) else None
    return ret

def shared_rounds_obj(team):
    puzzle_objs = [puzzle_obj(x) for x in puzzleaccess_set(team)
        .order_by('puzzle__order')]
    for access in roundaccess_set(team).order_by('round__order'):
        ret = {'round': access.round, 'name': access.round.name, 'url': access.round.url}
        if access.round.url == 'nano':
            nano_top_round_obj(ret, access)
        else:
            ret['all_puzzles'] = [x for x in puzzle_objs
                if x['puzzle'].round_id == access.round_id]
        yield ret

class SharedContext(Context):
    def __init__(self, team, rand):
        Context.__init__(self)
        self['posthunt'] = settings.POSTHUNT
        self['extra_hints'] = None
        self['team'] = team
        self['puzzle'] = None
        self['juice'] = None
        self['next_puzzle'] = None
        self['rand'] = rand
        self['DEBUG'] = settings.DEBUG
        self['show_solutions'] = show_solutions(team)
        self['solved_metas'] = (team.solved_puzzles
            .select_related('y2021puzzledata')
            .filter(is_meta=True)
            .order_by('id'))
        self['mmo_unlocked'] = get_mmo_unlocked(team)
        self['mmo_disabled'] = mmo_disabled()
        self['shortcuts'] = list(get_shortcuts())
        self['rounds'] = list(shared_rounds_obj(team))
        self['iframe_submissions'] = True
        self['available_interactions'] = (InteractionAccess.objects
            .filter(team=team, accomplished=False))
        self['completed_interactions'] = (InteractionAccess.objects
            .filter(team=team, accomplished=True))

class TopContext(SharedContext):
    def __init__(self, team, rand):
        SharedContext.__init__(self, team, rand)
        self['log_entries'] = [{'entry': x} for x in TeamLog.objects
            .filter(team=team)
            .order_by('-id')]

def GetTopContext(team):
    KEY = 'team%03d:top' % (team.id)
    context = cache.get(KEY)
    if not context:
        context = TopContext(team, random.random()).flatten()
        cache.set(KEY, context, CACHE_TIME)
    try:
        context['mmo_version'] = Y2021Settings.objects.get(name='mmo_version').value
        context['mmo_base'] = '%smmo_client/%s/' % (settings.MMO_STATIC_URL, context['mmo_version'])
    except Y2021Settings.DoesNotExist:
        context['mmo_version'] = ''
        context['mmo_base'] = '%smmo_client/' % (settings.MMO_STATIC_URL)
    return context

class RoundContext(SharedContext):
    def __init__(self, team, round, special, rand):
        SharedContext.__init__(self, team, rand)
        self['special'] = special
        try:
            round_access = roundaccess_set(team).get(round=round)
        except:
            logger.exception('team "%s" doesn\'t have access to round "%s"', team.url, round.url)
            return
        if round.url == 'infinite':
            self['round'] = infinite_round_obj(round_access, special)
        elif round.url == 'nano':
            self['round'] = nano_round_obj(round_access, special)
        else:
            self['round'] = round_obj(round_access)
        self['puzzles'] = self['round']['puzzles']
        self['all_puzzles'] = self['round']['all_puzzles']
        self['juice'] = self['round']['juice']
        self['next_puzzle'] = self['round']['next_puzzle']
        # (this function probably already exists somewhere, but I'm not sure where)
        def canonicalize(answer):
            return ''.join(c for c in answer.lower() if c in string.ascii_lowercase)
        self['puzzle_answer_lookup'] = {canonicalize(puzzle['puzzle'].answer): puzzle for puzzle in self['puzzles']}
        self['solved'] = team.solved_puzzles.values_list('url', flat=True)
        self['round_solved'] = team.solved_puzzles.filter(round=round).count()
        self['normal_round_solved'] = team.solved_puzzles.filter(round=round, is_meta=False).count()
        self['has_solution'] = os.path.exists(os.path.join(settings.ROUND_DATA, round.url, 'solution', 'nav-solution.html'))
        self['student_center_meta_unlocked'] = (
            team.puzzles.filter(url='student-center', puzzleaccess__found=True).exists()
        )

def GetRoundContext(team, round, special=1):
    KEY = 'team%03d:round-%d-%d' % (team.id, round.id, special)
    context = cache.get(KEY)
    if True or not context:
        context = RoundContext(team, round, special, random.random()).flatten()
        cache.set(KEY, context, CACHE_TIME)
    return context

class PuzzleContext(SharedContext):
    def __init__(self, team, puzzle, rand):
        SharedContext.__init__(self, team, rand)
        try:
            round_access = roundaccess_set(team).get(round=puzzle.round)
        except:
            logger.exception('team "%s" doesn\'t have access to round "%s"', team.url, puzzle.round.url)
            return
        if puzzle.round.url == 'nano':
            self['round'] = nano_round_obj(round_access, puzzle.y2021puzzledata.level)
        else:
            self['round'] = round_obj(round_access)
        try:
            puzzle_access = puzzleaccess_set(team).get(puzzle=puzzle)
        except:
            logger.exception('team "%s" doesn\'t have access to puzzle "%s"', team.url, puzzle.url)
            return
        self['puzzle'] = puzzle_obj(puzzle_access)
        self['extra'] = get_extra_puzzle_context(team, puzzle)
        self['solved'] = team.solved_puzzles.filter(round=puzzle.round).values_list('url', flat=True)
        self['round_solved'] = len(self['solved'])
        if puzzle.interaction.exists():
            self['submission_instructions'] = submission_instructions(puzzle.interaction.first(), team)
            self['submission_email'] = submission_instructions(puzzle.interaction.first(), team, False)


def GetPuzzleContext(team, puzzle):
    KEY = 'team%03d:puzzle-%d' % (team.id, puzzle.id)
    context = cache.get(KEY)
    if not context:
        context = PuzzleContext(team, puzzle, random.random()).flatten()
        cache.set(KEY, context, CACHE_TIME)
    return context

def load_metadata(puzzle_slug):
    filename = os.path.join(settings.PUZZLE_DATA, puzzle_slug, 'metadata.json')
    if os.path.exists(filename):
        return json.load(open(filename))

@require_team
def unlock(request):
    team = request.team
    unlock_puzzles(team)
    spoilr.actions.clear_cache(team)
    return redirect('/')

def global_tick(request):
    if not unlock_tick():
        return JsonResponse(status=500, data={'success': False, 'time': now()})
    unsnoozed_list = InteractionAccess.objects.filter(accomplished=False, snooze_ack=False, snooze_time__lte=now())
    for ia in unsnoozed_list:
        discord_queue('interaction%04d' % (ia.id), ia.team, 'Ready for interaction "%s" (unsnoozed)' % (ia.interaction.name), reverse('interaction_queue', args=(ia.interaction.url,)))
        ia.snooze_ack = True
        ia.save()

    return JsonResponse(data={'success': True, 'time': now()})

@require_team
def puzzle_view(request, puzzle):
    team = request.team
    puzzle_url = puzzle
    puzzle = None
    try:
        puzzle = get_puzzle_by_name(puzzle_url)
    except:
        logger.exception('Cannot find puzzle "%s"', puzzle_url)
        return XHttpResponseBadRequest('Cannot find puzzle ' + puzzle_url)
    try:
        PuzzleAccess.objects.get(team=team, puzzle=puzzle, found=True)
    except:
        logger.exception('Team "%s" does not have access to puzzle "%s"', team, puzzle)
        if request.user and request.user.is_staff:
            if get_puzzle_access(team, puzzle):
                return redirect(reverse('admin_find', args=(team.url, puzzle.url,)))
        return XHttpResponseBadRequest('Cannot find puzzle ' + puzzle_url)
    folder = puzzle.url
    if puzzle.y2021puzzledata.infinite:
        folder = puzzle.y2021puzzledata.parent.url
    filename = os.path.join(settings.PUZZLE_DATA, folder, 'index.html')
    if not os.path.exists(filename):
        return XHttpResponse('Unknown puzzle "%s"' % (puzzle.url))
    posthunt = os.path.join(settings.PUZZLE_DATA, folder, 'posthunt', 'index.html')
    has_posthunt = os.path.exists(posthunt)
    if has_posthunt and settings.POSTHUNT:
        filename = posthunt
    html = None
    with open(filename) as f:
        html = f.read()
    context = GetPuzzleContext(team, puzzle)
    if puzzle.round.url == 'infinite-template':
        return redirect(reverse('round_view', args=('infinite',)))
    if team.is_limited and request.GET.get('solved', '0') == '1':
        context['puzzle']['solved'] = True
    context['sroot'] = puzzle_static(puzzle)
    context['sproot'] = puzzle_static(puzzle)
    if '/solution/' in puzzle_url:
        context['sroot'] = puzzle_static(puzzle, True)
    context['index_html'] = Template(html).render(Context(context))
    canned_hints = []
    if show_solutions(team):
        filename = os.path.join(settings.PUZZLE_DATA, puzzle.url, 'hints.json')
        if os.path.exists(filename):
            with open(filename) as f:
                canned_hints = json.load(f)
    context['canned_hints'] = canned_hints
    return render(request, 'round/%s/puzzle/index.html.tmpl' % (puzzle.round.url), context)

@require_puzzle_access
def solution_view(request):
    team = request.team
    puzzle = request.puzzle
    if not show_solutions(team):
        return HttpResponseForbidden('Solutions are not available yet!')
    if puzzle.y2021puzzledata.infinite:
        return redirect(reverse('puzzle_solution', args=(puzzle.y2021puzzledata.parent.url,)))
    filename = os.path.join(settings.PUZZLE_DATA, puzzle.url, 'solution', 'index.html')
    if not os.path.exists(filename):
        return XHttpResponse('Unknown puzzle "%s"' % (puzzle.url))
    html = None
    with open(filename) as f:
        html = f.read()
    context = GetPuzzleContext(team, puzzle)
    context['sroot'] = puzzle_static(puzzle, True)
    context['sproot'] = puzzle_static(puzzle)
    context['index_html'] = Template(html).render(Context(context))
    context['credits'] = load_metadata(puzzle.url)['credits']
    round_url = puzzle.round.url
    if round_url == 'infinite-template':
        context['puzzle']
        round_url = 'infinite'
    return render(request, 'round/%s/solution/index.html.tmpl' % round_url, context)

@require_puzzle_access
def hints_view(request):
    team = request.team
    puzzle = request.puzzle
    if not show_solutions(team):
        return HttpResponseForbidden('Hints are not available for this team yet!')
    filename = os.path.join(settings.PUZZLE_DATA, puzzle.url, 'hints.json')
    hints = [(0, 'hex', 'hell')]
    if os.path.exists(filename):
        with open(filename) as f:
            hints = json.load(f)
    context = GetPuzzleContext(team, puzzle)
    context['hints'] = hints
    return render(request, 'round/hints.html.tmpl', context)

@require_round_access
def round_view(request):
    if request.round.url == 'infinite-template':
        return redirect(reverse('round_view', args=('infinite',)))
    context = GetRoundContext(request.team, request.round, int(request.GET.get('special', 1)))
    return render(request, 'round/%s/round.html.tmpl' % (request.round.url), context)

@require_round_access
def round_asset_view(request, resource):
    team = request.team
    round = request.round
    if resource == 'solution':
        return redirect(reverse('round_solution', args=(round.url,)))
    if resource.startswith('solution/') and not show_solutions(team):
        return HttpResponseForbidden('Solutions are not available yet!')
    if resource.endswith('.tmpl'):
        return HttpResponseForbidden('No peeking!')
    if resource.endswith('/'):
        resource += 'index.html'
    round_url = round.url
    if round_url == 'infinite-template':
        round_url = 'infinite'
    filename = os.path.join(settings.ROUND_DATA, round_url, resource)
    if not os.path.exists(filename):
        return XHttpResponse('Unknown file "%s"' % (filename))
    return FileResponse(open(filename, 'rb'))

@require_round_access
def round_solution_view(request):
    team = request.team
    round = request.round
    if not show_solutions(team):
        return HttpResponseForbidden('Solutions are not available yet!')
    context = GetRoundContext(team, round)
    if not context['has_solution']:
        return XHttpResponse('Unknown round "%s"' % (round.url))
    filename = os.path.join(settings.ROUND_DATA, round.url, 'solution', 'nav-solution.html')
    context['sroot'] = round_static(round.url, True)
    context['sproot'] = round_static(round.url)
    with open(filename) as f:
        context['index_html'] = Template(f.read()).render(Context(context))
    return render(request, 'round/%s/solution/nav-solution.html.tmpl' % round.url, context)

@require_team
def top_view(request):
    context = GetTopContext(request.team)
    if not context['mmo_unlocked']:
        return round_view(request, round='yew-labs')
    return render(request, 'index.html', context)

def check_mmo_status(team):
    mmo_message_available = False
    mmo_unlocked = False
    time_left = 0
    try:
        interaction = InteractionAccess.objects.get(team=team, interaction__url=MMO_UNLOCK_INTERACTION)
        mmo_message_available = True
        if interaction.accomplished:
            mmo_unlocked = True
        else:
            setting = Y2021Settings.objects.get_or_create(name='mmo_delay', defaults={'value': '60'})[0]
            time_left = datetime.timedelta(seconds=float(setting.value)) - (now() - interaction.timestamp)
            if time_left.total_seconds() <= 0:
                finish_mmo_interaction(team)
                mmo_unlocked = True
    except InteractionAccess.DoesNotExist:
        pass
    return mmo_message_available, mmo_unlocked, time_left

@require_team
def mmo_view(request):
    if request.team.is_limited:
        return redirect('/')
    context = GetTopContext(request.team)
    if not context['mmo_unlocked']:
        _, mmo_unlocked, _ = check_mmo_status(request.team)
        if mmo_unlocked:
            context = GetTopContext(request.team)
        else:
            return redirect(reverse('round_view', args=('yew-labs',)))
    context['extra_hints'] = 'device'
    return render(request, 'mmo.html', context)

@require_team
def mmo_message_view(request):
    team = request.team
    mmo_message_available, mmo_unlocked, time_left = check_mmo_status(team)
    context = GetTopContext(team)
    if mmo_unlocked:
        context['time_left'] = datetime.timedelta(seconds=0)
    elif mmo_message_available:
        context['time_left'] = time_left
    else:
        return redirect(reverse('round_view', args=('yew-labs',)))
    return render(request, 'mmo_message.html', context)

@require_team
def all_view(request):
    return render(request, 'all.html', GetTopContext(request.team))

@require_prelaunch_team
def faq_view(request):
    return render(request, 'faq.html', GetTopContext(request.team))

@require_team
def updates_view(request):
    context = GetTopContext(request.team)
    context['updates'] = [update_obj(request.team, x) for x in HQUpdate.objects
                          .filter(published=True).filter(Q(team__isnull=True) | Q(team=request.team))
                          .order_by('-publish_time')]
    return render(request, 'updates.html', context)

@require_prelaunch_team
def storylog_view(request):
    return render(request, 'storylog.html', GetTopContext(request.team))

@require_prelaunch_team
def eventschedule_view(request):
    context = GetTopContext(request.team)
    if any(round['round'].url == 'charles-river' for round in context['rounds']):
        return redirect(reverse('round_view', args=('charles-river',)))
    return render(request, 'eventschedule.html', context)

@require_prelaunch_team
def sponsors_view(request):
    return render(request, 'sponsors.html', GetTopContext(request.team))

@require_prelaunch_team
def statistics_view(request):
    return render(request, 'statistics.html', GetTopContext(request.team))

@require_prelaunch_team
def credits_view(request):
    return render(request, 'credits.html', GetTopContext(request.team))

@require_team
def completelog_view(request):
    return render(request, 'completelog.html', GetTopContext(request.team))

@require_team
def endgame_puzzle_view(request):
    return render(request, 'endgame_puzzle.html', GetTopContext(request.team))

@require_team
def endgame_solution_view(request):
    return render(request, 'endgame_solution.html', GetTopContext(request.team))

@require_team
def pmis_view(request):
    context = GetTopContext(request.team)
    context['green_sroot'] = round_static('green-building')
    return render(request, 'pmis.html', context)

@require_prelaunch_team
def prelaunch_view(request):
    if request.is_it_hunt_yet:
        return redirect('/')
    return render(request, 'prelaunch.html')

@require_puzzle_access
def puzzle_asset_view(request, resource):
    team = request.team
    puzzle = request.puzzle
    if resource == 'solution':
        return redirect(reverse('puzzle_solution', args=(puzzle.url,)))
    if resource.startswith('solution/') and not show_solutions(team):
        return HttpResponseForbidden('Solutions are not available yet!')
    if resource == 'metadata.json' and not (team.is_admin or team.is_special):
        return HttpResponseForbidden('No peeking!')
    if resource.endswith('/'):
        resource += 'index.html'
    folder = puzzle.url
    if puzzle.y2021puzzledata.infinite:
        folder = puzzle.y2021puzzledata.parent.url
    filename = os.path.join(settings.PUZZLE_DATA, folder, resource)
    return FileResponse(open(filename, 'rb'))

@require_puzzle_access
def local_puzzle_asset_view(request, resource):
    team = request.team
    puzzle = request.puzzle
    if resource == 'solution':
        return redirect(reverse('puzzle_solution', args=(puzzle.url,)))
    if resource.startswith('solution/') and not show_solutions(team):
        return HttpResponseForbidden('Solutions are not available yet!')
    if resource == 'metadata.json' and not (team.is_admin or team.is_special):
        return HttpResponseForbidden('No peeking!')
    if resource.endswith('/'):
        resource += 'index.html'
    folder = puzzle.url
    if puzzle.y2021puzzledata.infinite:
        folder = puzzle.y2021puzzledata.parent.url
    context = {}
    context['sroot'] = puzzle_static(puzzle)
    filename = os.path.join(settings.PUZZLE_DATA, folder, resource)
    if not os.path.exists(filename):
        return XHttpResponse('Unknown file "%s"' % (filename))
    if filename.endswith('.js') or filename.endswith('.json') or filename.endswith('.css') or filename.endswith('.html'):
        ctype = 'text/plain'
        if filename.endswith('.css'):
            ctype = 'text/css'
        elif filename.endswith('.html'):
            ctype = 'text/html'
        else:
            ctype = 'application/javascript'
        return HttpResponse(open(filename).read().replace('{{sroot}}', context['sroot']), content_type=ctype)
    print("Old Style Static File: %s" % (filename))
    return FileResponse(open(filename, 'rb'))

def global_asset_view(request, asset_path):
    filename = asset_path
    if not os.path.exists(filename):
        return XHttpResponse('Unknown file "%s"' % (filename))
    return FileResponse(open(filename, 'rb'))

def set_mmo_version(request):
    from google.cloud import storage
    store = storage.Client()
    mmo_bucket = store.get_bucket('silenda-dev')

    version = request.GET.get('v', None)
    if version is None:
        return JsonResponse(status=400, data={
            'success': False,
            'error': 'Must provide an mmo version with the "v" query param',
        })

    # Make sure an mmo build at this version has already been synced into the
    # bucket
    r = requests.get(settings.MMO_STATIC_URL + 'mmo_client/{}/Build/Build.json'.format(version))
    if r.status_code != 200:
        return JsonResponse(status=400, data={
            'success': False,
            'error': 'staticfiles could not find a deployed mmo_client with version "{}"'.format(version),
        })


    try:
        fname = 'static/mmo_client/{}/Build/UnityLoader.js'.format(version)
        dataFile = mmo_bucket.get_blob(fname)
        data = dataFile.download_as_string()
        data = data.replace(b'Mac OS X (10', b'Mac OS X (1[0-1]')
        newFile = mmo_bucket.get_blob(fname)
        newFile.upload_from_string(data)

        try:
            mmo_version_obj = Y2021Settings.objects.get(name='mmo_version')
            mmo_version_obj.value = version
        except Y2021Settings.DoesNotExist:
            mmo_version_obj = Y2021Settings(name='mmo_version', value=version)
        mmo_version_obj.save()

        return JsonResponse(data={
            'success': True,
            'version': version,
        })

    except e:
        return JsonResponse(status=500, data={
            'success': False,
            'error': str(e),
        })

def get_mmo_version(request):
    try:
        mmo_version_obj = Y2021Settings.objects.get(name='mmo_version')
        return JsonResponse(data={
            'success': True,
            'version': mmo_version_obj.value,
        })
    except Y2021Settings.DoesNotExist:
        return JsonResponse(status=500, data={
            'success': False,
            'error': 'Unknown MMO Version',
        })

def api_team_obj(team):
    return (team.y2021teamdata.tempest_id, team.y2021teamdata.emoji, team.name, team.username, team.size_int, team.y2021teamdata.auth)

def get_teams(request):
    auth = request.GET.get('auth', None)
    if auth != settings.SECRET_AUTH:
        return JsonResponse(status=400, data={
            'success': False,
            'error': 'Invalid token',
        })

    teams = []
    for t in Team.objects.select_related('y2021teamdata').all():
        teams.append(api_team_obj(t))
    return JsonResponse(data={
        'success': True,
        'teams': teams,
    })

def set_unlock_state(request):
    auth = request.GET.get('auth', None)
    if auth != settings.SECRET_AUTH:
        return JsonResponse(status=400, data={
            'success': False,
            'error': 'Invalid token',
        })

    try:
        uid = request.GET.get('uid', None)
        state = request.GET.get('state', None)
        u = MMOUnlock.objects.get(unlock_id=uid)
        if state is not None:
            found = False
            for (s, t) in forceUnlock:
                if state == s or state == t:
                    state = s
                    found = True
            if found:
                u.force = state.strip().upper()
                u.save()
            else:
                return JsonResponse(status=500, data={
                    'success': False,
                    'error': 'Unknown state',
                })


        return JsonResponse(data={
            'success': True,
            'uid': u.unlock_id,
            'state': u.force,
        })

    except e:
        return JsonResponse(status=500, data={
            'success': False,
            'error': str(e),
        })

@staff_member_required
def admin_find_view(request, team_url, puzzle_url):
    team = None
    puzzle = None
    try:
        team = Team.objects.get(url=team_url)
        puzzle = get_puzzle_by_name(puzzle_url)
    except Team.DoesNotExist:
        logger.exception('Cannot find team "%s"', team_url)
        return XHttpResponseBadRequest('Cannot find team ' + team_url)
    except Puzzle.DoesNotExist:
        logger.exception('Cannot find puzzle "%s"', puzzle_url)
        return XHttpResponseBadRequest('Cannot find puzzle ' + puzzle_url)
    success = False
    if request.method == 'POST' and 'find' in request.POST:
        try:
            assert discover_puzzle(team, puzzle)
        except:
            logger.exception('Team "%s" does not have access to puzzle "%s"', team, puzzle)
            return XHttpResponseBadRequest('Cannot find puzzle ' + puzzle_url)
        success = True
    return render(request, 'manual_find.html', {'team': team, 'puzzle': puzzle, 'success': success})

@require_team
def find_puzzle_view(request, puzzle, puzzle_id):
    team = request.team
    puzzle_url = puzzle
    puzzle = None
    try:
        puzzle = get_puzzle_by_name(puzzle_url)
        assert(puzzle.y2021puzzledata.obfuscated_id == puzzle_id)
    except:
        logger.exception('Cannot find puzzle "%s"', puzzle_url)
        return XHttpResponseBadRequest('Cannot find puzzle ' + puzzle_url)
    if team.is_limited and puzzle.y2021puzzledata.infinite and puzzle.y2021puzzledata.infinite_id > 20:
        return XHttpResponseBadRequest('Cannot find puzzle ' + puzzle_url)
    try:
        parent = puzzle.y2021puzzledata.parent
        if parent:
            assert discover_puzzle(team, parent)
        assert discover_puzzle(team, puzzle)
    except:
        logger.exception('Team "%s" does not have access to puzzle "%s"', team, puzzle)
        return XHttpResponseBadRequest('Cannot find puzzle ' + puzzle_url)
    return redirect(reverse('puzzle_view', args=(puzzle.url,)))

@require_team
def register_discord_view(request, discord_id):
    team = request.team
    context = GetTopContext(request.team)
    context['registered_team'] = None
    context['error'] = None
    entry = None
    try:
        entry = TeamExtraData.objects.get(name='discord', data=discord_id)
        entry.team = team
        entry.save()
    except TeamExtraData.DoesNotExist:
        entry = TeamExtraData.objects.create(team=team, name='discord', data=discord_id)
    context['registered_team'] = entry.team
    return render(request, 'register_discord.html', context)

def remove_discord_view(request):
    auth = request.GET.get('auth', None)
    if auth != settings.SECRET_AUTH:
        return JsonResponse(status=400, data={
            'success': False,
            'error': 'Invalid token',
        })
    user_id = request.GET.get('user_id', None)
    if user_id is not None:
        try:
            entry = TeamExtraData.objects.get(name='discord', data=user_id)
            entry.delete()
            return JsonResponse(data={
                'success': True,
                'user_id': entry.data,
                'team': api_team_obj(entry.team),
            })
        except TeamExtraData.DoesNotExist:
            return JsonResponse(data={
                'success': False,
                'user_id': user_id,
            })
    return JsonResponse(status=400, data={
        'success': False,
        'error': 'Must provide user_id',
    })

def lookup_discord_view(request):
    auth = request.GET.get('auth', None)
    if auth != settings.SECRET_AUTH:
        return JsonResponse(status=400, data={
            'success': False,
            'error': 'Invalid token',
        })

    user_id = request.GET.get('user_id', None)
    if user_id is not None:
        try:
            entry = TeamExtraData.objects.get(name='discord', data=user_id)
            return JsonResponse(data={
                'success': True,
                'user_id': entry.data,
                'team': api_team_obj(entry.team),
            })
        except TeamExtraData.DoesNotExist:
            return JsonResponse(data={
                'success': False,
                'user_id': user_id,
            })

    team_id = request.GET.get('team_id', None)
    if team_id is not None:
        try:
            entries = TeamExtraData.objects.filter(
                team__y2021teamdata__tempest_id=team_id,
                name='discord').all()
            return JsonResponse(data={
                'success': True,
                'user_ids': [entry.data for entry in entries],
                'team': api_team_obj(entries[0].team),
            })
        except IndexError:
            return JsonResponse(data={
                'success': False,
                'team_id': team_id,
            })

    return JsonResponse(status=400, data={
        'success': False,
        'error': 'Must provide user_id or team_id',
    })

@staff_member_required
def endgame_view(request, team_url):
    xglobal = False
    yglobal = False
    if team_url == 'global':
        xglobal = True
        team = Team.objects.get(url='dog')
    elif team_url == 'winbatch':
        yglobal = True
        team = Team.objects.get(url='dog')
    else:
        try:
            team = Team.objects.get(url=team_url)
        except Team.DoesNotExist:
            return XHttpResponseBadRequest('Team "%s" does not exist.' % (team_url))
        if not InteractionAccess.objects.filter(team=team, interaction__url='endgame').exists():
            return XHttpResponseBadRequest('Team "%s" does not have access to the endgame.' % (team.name))
    status = None
    if request.method == 'POST' and 'device' in request.POST and 'state' in request.POST:
        device = request.POST['device']
        location = None
        for (d, l) in ENDGAME_DEVICES:
            if d == device:
                location = l
        state = request.POST['state'] == 'ENABLE'
        if xglobal:
            for t in Team.objects.all():
                set_unlock_value(t, device, state)
        elif yglobal:
            interaction = Interaction.objects.get(url='endgame')
            for ia in InteractionAccess.objects.filter(interaction=interaction, accomplished=False):
               set_unlock_value(ia.team, device, state)
        set_unlock_value(team, device, state)
        status = 'Updated %s (%s) to %s' % (device, location, request.POST['state'] + 'D')
    states = []
    for (d, location) in ENDGAME_DEVICES:
        states.append({'device': d, 'location': location, 'enabled': get_unlock_value(team, d)})
    return render(request, 'endgame.html', {'team': team, 'devices': states, 'status': status})
