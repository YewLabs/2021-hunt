import json
from pathlib import Path

PUZZLE_DATA_PATH = Path(__file__).parent / 'resources/unchained_puzzles.json'
PUZZLE_DATA = json.load(open(PUZZLE_DATA_PATH))

def generate_context(puzzle):
    puzzle_id = puzzle.y2021puzzledata.infinite_id
    puzzle_answer = puzzle.answer
    
    return PUZZLE_DATA[str(puzzle_id)]
