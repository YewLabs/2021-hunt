from pathlib import Path
from jinja2 import Template

import json

from .check import check, Puzzle, WORDS

PUZZLE_DATA_PATH = Path(__file__).parent / 'resources/myows_puzzles.json'
PUZZLE_DATA = json.load(open(PUZZLE_DATA_PATH))


def generate_context(puzzle):
    puzzle_id = puzzle.y2021puzzledata.infinite_id
    puzzle_answer = puzzle.answer
    
    constraints_json = PUZZLE_DATA[str(puzzle_id)]
    constraints = Puzzle.from_obj(constraints_json)

    return {
        'constraints': constraints
    }


def filter_non_alpha(word):
    return ''.join(c for c in word if c.isupper())


def check_puzzle(puzzle, grid, words):
    puzzle_id = puzzle.y2021puzzledata.infinite_id
    puzzle_answer = puzzle.answer

    try:
        constraints_json = PUZZLE_DATA[str(puzzle_id)]
        constraints = Puzzle.from_obj(constraints_json)
    except Exception as e:
        print(e)
        return "Error: can't find puzzle with that id."

    res, error = check(grid, words, constraints)
    if res is None:
        return error
    else:
        extraction, extraction_template = res
        template_path = Path(__file__).parent / 'templates' / extraction_template
        template = Template(open(template_path, 'r').read())

        return template.render(extraction=extraction)


def lookup(word):
    word = filter_non_alpha(word.upper())

    if len(word) <= 3:
        return "Your word must be at least 4 letters long."
    
    if word not in WORDS:
        return "{} is not a common word.".format(word)
    else:
        return "{} is a common word.".format(word)
