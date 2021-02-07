import re
from django.http import JsonResponse
from spoilr.decorators import *
import urllib

@require_puzzle_access
def puzzle206_view(request):
    entry = request.GET.get('word', default='')
    entry = urllib.parse.unquote(entry)
    fills = bracketFills(entry)
    resp = JsonResponse(fills)
    resp['Access-Control-Allow-Origin'] = '*'
    return resp

def bracketFills(word):
    # generate the full set of bracket results for an input word
    fills = {}

    # Calculate the winner of the main bracket

    (win, los, a, b) = fullContest("Codenim", word)
    fills['score:g'] = a
    fills['score:h'] = b
    fills['ad'] = win

    (win, los, a, b) = fullContest("Do", fills['ad'])
    fills['score:ac'] = a
    fills['score:ad'] = b
    fills['aab'] = win
    fills['zc'] = los

    (win, los, a, b) = fullContest("Stone Rage", fills['aab'])
    fills['score:aaa'] = a
    fills['score:aab'] = b
    fills['aaaa'] = win
    fills['zi'] = los

    (win, los, a, b) = fullContest(fills['aaaa'], "Thee & Thy")
    fills['score:aaaa'] = a
    fills['score:AAAA'] = b
    fills['aaaaa'] = win
    fills['zm'] = los

    (win, los, a, b) = fullContest(fills['aaaaa'], "Windex Ooze")
    fills['score:aaaaa'] = a
    fills['score:aaaab'] = b
    fills['winwon'] = win
    fills['zo'] = los

    # Calculate the winner of the loser's bracket

    (win, los, a, b) = fullContest(fills['zc'], "Rock & Roll")
    fills['score:zc'] = a
    fills['score:zd'] = b
    fills['zzb'] = win

    (win, los, a, b) = fullContest(fills['zi'], "Bomb Bros")
    fills['score:zi'] = a
    fills['score:zza'] = b
    fills['zzza'] = win

    (win, los, a, b) = fullContest("Battlesnake", fills['zzb'])
    fills['score:zj'] = a
    fills['score:zzb'] = b
    fills['zzzb'] = win

    (win, los, a, b) = fullContest(fills['zzza'], fills['zzzb'])
    fills['score:zzza'] = a
    fills['score:zzzb'] = b
    fills['zzzza'] = win

    (win, los, a, b) = fullContest(fills['zm'], fills['zzzza'])
    fills['score:zm'] = a
    fills['score:zzzza'] = b
    fills['zzzzza'] = win

    (win, los, a, b) = fullContest(fills['zzzzza'], "Gelatinous Cone")
    fills['score:zzzzza'] = a
    fills['score:zzzzzb'] = b
    fills['zzzzzza'] = win

    (win, los, a, b) = fullContest(fills['zo'], fills['zzzzzza'])
    fills['score:zo'] = a
    fills['score:zzzzzza'] = b
    fills['advance'] = win
    fills['loswon'] = win

    # Grand finals

    (win, los, a, b) = fullContest(fills['winwon'], fills['loswon'])
    fills['score:winwon'] = a
    fills['score:loswon'] = b
    fills['final'] = win

    return fills

def fullContest(a, b):
    return (contest(a, b), loser(a, b), score(a, b), score(b, a))

def contest(contestA, contestB):
    inputA = re.sub("\\s+", "", contestA.upper())
    inputB = re.sub("\\s+", "", contestB.upper())

    if inputA =="":
        return contestB
    if inputB =="":
        return contestA

    if statEval(inputA) > statEval(inputB):
        return contestA
    if statEval(inputB) > statEval(inputA):
        return contestB

    if zodEval(inputA) > zodEval(inputB):
        return contestA
    if zodEval(inputB) > zodEval(inputA):
        return contestB

    if pairEval(inputA) > pairEval(inputB):
        return contestA
    if pairEval(inputB) > pairEval(inputA):
        return contestB

    if scrabEval(inputA) < scrabEval(inputB):
        return contestA
    if scrabEval(inputB) < scrabEval(inputA):
        return contestB

    return ""

def loser(inputA, inputB):
    if contest(inputA, inputB) == inputA:
        return inputB
    else:
        return inputA

def score(contestA, contestB):
    inputA = re.sub("\\s+", "", contestA.upper())
    inputB = re.sub("\\s+", "", contestB.upper())

    if inputA == "":
        return "N/A"
    if statEval(inputA) != statEval(inputB):
        return str(statEval(inputA))
    if zodEval(inputA) != zodEval(inputB):
        return str(zodEval(inputA))
    if pairEval(inputA) != pairEval(inputB):
        return str(pairEval(inputA))
    if scrabEval(inputA) != scrabEval(inputB):
        return str(scrabEval(inputA)) + "!"

    return "N/A";

def statEval(input):
    #function to check D&D stat abbreviations
    try:
        input.index("STR")
        return 6
    except:
        pass
    try:
        input.index("DEX")
        return 5
    except:
        pass
    try:
        input.index("CON")
        return 4
    except:
        pass
    try:
        input.index("INT")
        return 3
    except:
        pass
    try:
        input.index("WIS")
        return 2
    except:
        pass
    try:
        input.index("CHA")
        return 1
    except:
        return 0

def zodEval(input):
    try:
        input.index("RAT")
        return 12
    except:
        pass
    try:
        input.index("OX")
        return 11
    except:
        pass
    try:
        input.index("TIGER")
        return 10
    except:
        pass
    try:
        input.index("RABBIT")
        return 9
    except:
        pass
    try:
        input.index("DRAGON")
        return 8
    except:
        pass
    try:
        input.index("SNAKE")
        return 7
    except:
        pass
    try:
        input.index("HORSE")
        return 6
    except:
        pass
    try:
        input.index("GOAT")
        return 5
    except:
        pass
    try:
        input.index("MONKEY")
        return 4
    except:
        pass
    try:
        input.index("ROOSTER")
        return 3
    except:
        pass
    try:
        input.index("DOG")
        return 2
    except:
        pass
    try:
        input.index("PIG")
        return 1
    except:
        return 0

def pairEval(input):
    def makeRegex(vowel):
        return "^[^AEIOU]*"+vowel+"[^AEIOU]*"+vowel+"[^AEIOU]*$"

    if re.search(makeRegex("A"), input):
        return 5
    if re.search(makeRegex("E"), input):
        return 4
    if re.search(makeRegex("I"), input):
        return 3
    if re.search(makeRegex("O"), input):
        return 2
    if re.search(makeRegex("U"), input):
        return 1
    return 0

def scrabEval(input):
    scores = { 'a': 1, 'e': 1, 'i': 1, 'o': 1, 'u': 1, 'l': 1, 'n': 1, 'r': 1, 's': 1, 't': 1, 'd': 2, 'g': 2, 'b': 3, 'c': 3, 'm': 3, 'p': 3, 'f': 4, 'h': 4, 'v': 4, 'w': 4, 'y': 4, 'k': 5, 'j': 8, 'x': 8, 'q': 10, 'z': 10 }
    return sum([scores[c] for c in input.lower() if c in scores.keys()])
