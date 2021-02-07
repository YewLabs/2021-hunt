from django.http import JsonResponse
from spoilr.decorators import *
import urllib
from datetime import datetime, timedelta
from emoji import emojize
import hashlib

@require_puzzle_access
def puzzle407_view(request):
    message = request.GET.get('message', default='')
    message = urllib.parse.unquote(message)
    level = request.GET.get('level', default='')
    level = str(urllib.parse.unquote(level))

    newlevel, newmessage = get_reply(level, message)
    ret = {"level": newlevel, "message": newmessage}
    resp = JsonResponse(ret)
    resp['Access-Control-Allow-Origin'] = '*'
    return resp

def emonum(n):
    return emojize(f':keycap_{n}:')

answers = [
    '-',
    '💯',
    '🖖🖖🏻🖖🏼🖖🏽🖖🏾🖖🏿', 
    '😠😡',
    '🥪🍔',
    '🕴',
    '👯',
    '🌛',
    '🇨🇦',
    emonum(6),
    '🍌',
    '🧠',
    '⭐🌟',
    '🚜',
    '☮️✌🏾✌️✌🏻✌🏼✌🏽✌🏾✌🏿', 
    '👽',
    '💍',
    '✈️',
    []
]
questions = [
    '-',
    '🔟✖️🔟',
    '🗿📄✂️🦎❓',
    '😀😨🤮😢❓',
    '🍞➕🥬➕🥩➕🧀➕🍞',
    '🧑👔⬆️🪄✨',
    '🧑🧑🐰👂👂',
    '🌝➖🌖',
    '🇧🇸🇹🇩🇬🇭🇯🇵🇰🇿🇲🇬🇲🇹🇵🇦🇶🇦🇷🇼❓',
    f'''🥝➕🥝➕🥝↔️9️⃣
🥝➕5️⃣↔️🍍➕🍍
🥝➕🍍↔️🥥➕{emonum(1)}
🥥↔️❓
''',
    '''🍓➕🍓➕🍓↔️🍏➕🍏➕🍌➕9️⃣
🍏➕🍌➕🍇↔️5️⃣
🍏➕🍏➕🍏➕🍇↔️🍓➕2️⃣
🍌➕🍓➕🍇↔️8️⃣
🍏↔️❓
''',
    '🐝🌧️    5️⃣',
    '🐀🐀🔙   4️⃣',
    '🔚☄️🔀🥕     7️⃣',
    '🕘🕜🕢🕥🕜',
    emojize(':candy::candy::candy::person_biking::full_moon::backhand_index_pointing_right::sparkles:')+'    '+emojize(':keycap_1::keycap_9::keycap_8::keycap_2:'),
    '👁📼📺7️⃣🗓☠️    2️⃣0️⃣0️⃣2️⃣',
    '⬆↗⬆⬆⬅⬅↙⬅⬆↗↖⬆➡↘➡➡⬆⬆↖⬆➡↘↘⬇↘➡➡↘↙⬅⬅↙⬇↙↙⬅',
    '👏👏👏 📞➡️📧ⓜ️⭕🗾ℹ️'
]

def emojize_time_left(delta):
    delta = timedelta(seconds=45) - delta
    if delta.seconds < 1:
        return emojize(':keycap_1:')
    else:
        return "".join(map(emonum, str(int(delta.seconds))))

levelcodes = [63538967066, 744086802, 26912758759, 33565834251, 78014900085, 65926038389, 63840277424, 7343523009, 83297297356, 3826235386, 83939961065, 52786000828, 13015560356, 
13012201902, 17423390721, 76592950320, 41617596970, 92877313443, 82476029877, 62493707482]
salt = "TxTEM0J!s@|t"

def decodelstr(levelstr):
    if hashlib.md5(bytes(levelstr[:-32]+salt,"utf8")).hexdigest() != levelstr[-32:]:
        print("hash fail")
        return 0, None
    try:
        i = int(levelstr[:-32])
        level = i % (3**23)
        ts = i // (3**23)    
        level = levelcodes.index(level)
    except ValueError:
        return 0, None
    
    return level, datetime.fromtimestamp(ts/1000000)

def encodelstr(level, time):
    res = str(int(time.timestamp()*1000000) * (3**23) + levelcodes[level])
    hs = hashlib.md5(bytes(res+salt,"utf8")).hexdigest()
    return res+hs

def get_reply(levelstr, message):
    level, last_time = decodelstr(levelstr)
    skip = False
    if level == 0:
        level = 1
        skip = True
    
    expected_answer = answers[level]
    this_time = datetime.now()
    rate_limit = (last_time is not None) and (this_time - last_time < timedelta(seconds=45)) 
    if rate_limit:
        prefix = '⏳⏳⏳❗ '+emojize_time_left(this_time-last_time)+'🥈⌚'
        newlevelstr = levelstr
    elif message and (message[0] in expected_answer):
        level += 1
        prefix = '{}✅❗❗❗\n'.format(message)
        newlevelstr = encodelstr(level, datetime.fromtimestamp(1))
    elif not skip and expected_answer:
        #print("{} instead of {}".format(body,expected_answer))
        prefix = '{}❌\n'.format(message)
        newlevelstr = encodelstr(level, datetime.now())
    else:
        prefix = ''
        newlevelstr = encodelstr(level, datetime.fromtimestamp(1))
    
    ans = prefix if rate_limit else '{}{}'.format(prefix, questions[level])

    return newlevelstr, ans