import glob
import os
import re
import yaml
from collections import namedtuple


QuestionSet = namedtuple(
    'QuestionSet',
    ['name', 'difficulty', 'coolness', 'time', 'questions'],
)


Question = namedtuple(
    'Question',
    ['content', 'time'],
)

def sanitize(str):
    try:
        s = str.encode('ascii')
        str = str.lower()
        str = re.sub('-', ' ', str)
        str = re.sub('[^a-z0-9 ]', '', str)
    except UnicodeEncodeError:
        pass

    return str.strip()


def all_files_with_extension(extensions = ['txt']):
    r = []
    for root, dirs, files in os.walk('2021-hunt/hunt/special_puzzles/cafe_luge/puzzles'):
        for file in files:
            if any([file.endswith('.' + p) for p in extensions]):
                r.append(os.path.join(root, file))

    return r


def question_set_from_file(path):
    try:
        with open(path, 'r') as fd:
            r = yaml.safe_load(fd.read())
    except Exception as e:
        raise Exception(f'Exception loading {path}')

    name = r['name']
    difficulty = int(r['difficulty'].split('/')[0])
    coolness = int(r['coolness'].split('/')[0])
    time = r['time']
    questions = [Question(k['question'], time) for k in r['questions']]

    return QuestionSet(name, difficulty, coolness, time, questions)
