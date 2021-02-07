
from typing import Optional
from django.http import JsonResponse
from numpy.core.arrayprint import BoolFormat

from spoilr.decorators import require_puzzle_access
from django.views.decorators.csrf import csrf_exempt

# Oh, the Places You'll Go!

asks = {
    'The scholar':{
        'writing': "\"I invented it myself; I can write faster than you can talk,\" the scholar proudly explains.",
        'other': "The scholar asks you if you have a story to tell him, for he would like to record it.",
    },
    'The stone woman': {
        'moon': '"I hope we are able to bring it back to make Father Earth happy again, even if I turn to stone in the process," she says.',
        'daughter': '"Do you know where she is?" she says.',
        'damaya': '"That naive girl is gone," she says.',
        'syenite': '"That naive girl is gone," she says.',
        'essun': '"What do you mean by that question?" she asks.',
        'alabaster': '"I\'ll rusting kill that stone eater," she says.',
        'guardians': "\"They are evil, and they cannot take my children,\" she says."
    },
    'The still dude': {
        'tin man': "He says, \"I like that guy.\"",
        'lion': "He says, \"I like that guy.\"",
        'cowardly lion': "He says, \"I like that guy.\"",
        'other': "He says, \"I don't know what you're talking about. I don't know anything.\"",
    },
    'The pirate': {
        'other': "\"What are you looking at? Do you want to be pirated?\" the pirate replies.",
        "buttercup": "\"I miss her. One day I will win her back!\" replies the pirate.",
        "dread pirate roberts": "\"Yes, that is who I am,\" the pirate replies, but you can sense that he may not be telling the whole truth.",
        "westley": "\"How did you know my true identity? Prepare to die!\" the pirate shouts. You should probably leave before he makes good on that threat."
    },
    'The young boy': {
        'wendy': "\"I wish she would agree to stay young forever with me,\" he replies somberly.",
        'tinker bell': "\"She taught me how to fly!\" he says delightedly, \"but I don't have any fairy dust here.\"",
    }
    
}
tells = {
    'The scholar': {
        'other': "The scholar thanks you for your story and writes it down, using a strange writing system you've never seen before."
    }
}
things = {
    'The scholar': {
        'the dragon book': "The scholar gestures broadly and smiles, \"My book! I hope you enjoyed it. The draccus is such a fascinating creature.\"",
    },
    'The stone woman': {
        'the crystal': "The woman stares at the crystal, and she says, \"Do you know how dangerous this obelisk is? There is power inside it to change things on a celestial scale. Do not tread lightly with it.\""
    },
    "The reindeer": {
        "the carrot": "The reindeer munches happily on the carrot."
    },
    'The still dude': {
        'the diploma': "He looks at the diploma, and then takes it, saying, \"The sum of the square root of any two sides of an isosceles triangle is equal to the square root of the third side.\""
    },
    'The pirate': {
        'the mysterious white powder': "He looks at you pityingly. \"Ha! You thought you could poison me? I'm immune to this stuff!\"",
    },
    "The gardener": {
        'the daggers': "The gardener looks at you gravely and says, \"How did you get these? They were given to my comrades and me as we we set out on a great journey.\""
    }, 
    'The scientist': {
        'the dog': "\"Aubergine!\" he shouts, happily. \"You know, when I came here to study this unusual place, I feared I never would see my dog again. Thank you!\""
    },
    'The young boy': {
        "the pipes": "The boy takes the pipes, and he plays them with some skill. The song is beautiful, and it makes you smile."
    }
}
import string

def askPerson(person: str, command: str):
    lookup = asks.get(person, None)
    if lookup is not None:
        command = command.lower()
        spot = command.find("about")
        if spot == -1:
            return "I don't understand, are you trying to ASK someone ABOUT something?"
        topic = command[spot+6:]
        topic = "".join(x for x in topic if x in string.ascii_lowercase or x == ' ')
        if topic in lookup:
            return lookup[topic]
        elif 'other' in lookup:
            return lookup['other']
    return person+" looks at you blankly."


def tellPerson(person: str, command: str):
    if person == 'yourself':
        return "You don't reply. Obviously."
    lookup = tells.get(person, None)
    if lookup is not None:
        command = command.lower()
        spot = command.find("about")
        if spot == -1:
            return "I don't understand, are you trying to TELL someone ABOUT something?"
        topic = command[spot+6:]
        topic = "".join(x for x in topic if x in string.ascii_lowercase or x == ' ')
        if topic in lookup:
            return lookup[topic]
        elif 'other' in lookup:
            return lookup['other']
    return person+" looks at you blankly."

def giveThing(person: str, thing: str):
    lookup = things.get(person, {})
    response = lookup.get(thing, None)
    if response:
        return response,True
    return f"{person} ignores you.",False

from typing import Tuple
def get_text(request) -> Tuple[str, bool]:
    try:
        action = request.POST['action']
        arga = request.POST['arg1']
        argb = request.POST['arg2']
        if action == 'give':
            return giveThing(arga, argb)
        elif action == 'tell':
            return tellPerson(arga, argb), False
        elif action == 'ask':
            return askPerson(arga, argb), False
        else:
            return "Please contact HQ if you see this text, and include the command that led to it.", False
    except:
        return "Unable to process your command. Please contact HQ and report a bug.", False


@csrf_exempt
@require_puzzle_access
def puzzle434_view(request):
    resp, extra = get_text(request)
    return JsonResponse({'reply': resp, 'success': extra})
