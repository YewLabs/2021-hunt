import json
import random

from pathlib import Path

WORDLIST = 'resources/wordlist.txt'
WORDS = {word.strip() for word in open(Path(__file__).parent / WORDLIST, 'r')}

DIRECTIONS = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
KNIGHTS = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]

DIRECTION_LOOKUP = {'N': (0, -1), 
                   'NE': (1, -1), 
                   'E': (1, 0), 
                   'SE': (1, 1),
                   'S': (0, 1),
                   'SW': (-1, 1),
                   'W': (-1, 0),
                   'NW': (-1, -1)}
DIRECTION_NAMES = {DIRECTION_LOOKUP[name] : name for name in DIRECTION_LOOKUP}

SEMAPHORE_ALPHABET = {
    'A': ('S', 'SW'),
    'B': ('S', 'W'),
    'C': ('S', 'NW'),
    'D': ('S', 'N'),
    'E': ('S', 'NE'),
    'F': ('S', 'E'),
    'G': ('S', 'SE'),
    'H': ('SW', 'W'),
    'I': ('SW', 'NW'),
    'J': ('N', 'E'),
    'K': ('SW', 'N'),
    'L': ('SW', 'NE'),
    'M': ('SW', 'E'),
    'N': ('SW', 'SE'),
    'O': ('W', 'NW'),
    'P': ('W', 'N'),
    'Q': ('W', 'NE'),
    'R': ('W', 'E'),
    'S': ('W', 'SE'),
    'T': ('NW', 'N'),
    'U': ('NW', 'NE'),
    'V': ('N', 'SE'),
    'W': ('NE', 'E'),
    'X': ('NE', 'SE'),
    'Y': ('NW', 'E'),
    'Z': ('E', 'SE'),
}

class Puzzle:
    def __init__(self):
        self.dimensions = (8, 8)
        self.letters = ''
        self.constraints = []
        self.has_letter_constraint = True

    @property
    def text_rules(self):
        rules = []

        # other constraints
        for constraint in self.constraints:
            rules.append(constraint.text_rule())
        return rules

    @staticmethod
    def from_obj(puzz_data, force_answer=None):
        puzzle = Puzzle()
        
        puzzle.dimensions = (puzz_data.get('rows', 8), puzz_data.get('columns', 8))
        puzzle.letters = puzz_data.get('letters', '')
        
        puzzle.answer = puzz_data.get('answer', 'TEMPANSWER')
        if force_answer:
            puzzle.answer = force_answer

        puzzle.extraction_method = puzz_data.get('extraction_method', 'unused')

        for constraint_json in puzz_data['constraints']:
            constraint_type = CONSTRAINT_LOOKUP[constraint_json['type']]
            puzzle.constraints.append(constraint_type(*constraint_json.get('params', [])))
        
        return puzzle

    @staticmethod
    def from_json(fname, force_answer=None):
        puzz_data = json.load(open(fname, 'r'))
        return Puzzle.from_obj(puzz_data, force_answer)

class Constraint:
    def check(self, grid, words):
        raise NotImplementedError

    def text_rule(self):
        raise NotImplementedError

class ScoreConstraint(Constraint):
    def __init__(self, score):
        self.score = score

    def check(self, grid, words):
        cscore = sum(max(len(w) - 3, 0) for w in words)
        if cscore >= self.score:
            return True, None
        else:
            return False, "Your word search has a score of {}. You must achieve a score of at least {}.".format(cscore, self.score)

    def text_rule(self):
        return "For each word of length L you use, you get L-3 points. Your word search must achieve a score of at least {} points.".format(self.score)

class DistinctRowColumnConstraint(Constraint):
    def check(self, grid, words):
        n, m = len(grid), len(grid[0])
        rlines = [[grid[y][x] for x in range(m)] for y in range(n)]
        clines = [[grid[y][x] for y in range(n)] for x in range(m)] 
        lines = rlines + clines
        if any(len(set(line)) != len(line) for line in lines):
            return False, "All letters in each row and column must be distinct."
        return True, None
    
    def text_rule(self):
        return "All letters in each row and column must be distinct."

class NoAdjacentEqualConstraint(Constraint):
    def check(self, grid, words):
        n, m = len(grid), len(grid[0])
        for y in range(n):
            for x in range(m):
                for dx, dy in DIRECTIONS:
                    nx, ny = x + dx, y + dy
                    if nx < 0 or nx >= m or ny < 0 or ny >= n:
                        continue
                    if grid[ny][nx] == grid[y][x]:
                        return False, "No two equal letters may be horizontally, vertically, or diagonally adjacent."
        return True, None
    
    def text_rule(self):
        return "No two equal letters may be horizontally, vertically, or diagonally adjacent."


class LetterBagConstraint(Constraint):
    def __init__(self, *letter_bag):
        self.letter_bag = letter_bag

    def check(self, grid, words):
        grid_concat = ''.join(row for row in grid)
        for constraint in self.letter_bag:
            letter, freq = constraint
            letter_count = grid_concat.count(letter)
            if letter_count != freq:
                return False, "The letter {} appears {} times but must appear exactly {} times.".format(letter, letter_count, freq)

        return True, None
    
    def text_rule(self):    
        bag_as_text = ", ".join("{} {}'s".format(freq, letter) for letter, freq in sorted(self.letter_bag))
        return "Your grid must contain exactly the following collection of letters: {}.".format(bag_as_text)


class NoKnightEqualConstraint(Constraint):
    def check(self, grid, words):
        n, m = len(grid), len(grid[0])

        for y in range(n):
            for x in range(m):
                for dx, dy in KNIGHTS:
                    nx, ny = x + dx, y + dy
                    if nx < 0 or nx >= m or ny < 0 or ny >= n:
                        continue
                    if grid[ny][nx] == grid[y][x]:
                        return False, "No two equal letters may be a knight's move away."
        return True, None

    def text_rule(self):
        return "No two equal letters may be a knight's move away."

class WordLengthConstraint(Constraint):
    def __init__(self, word_length):
        self.word_length = word_length

    def check(self, grid, words):
        if all(len(w) == self.word_length for w in words):
            return True, None
        else:
            return False, "Every word used must be {} letters long.".format(self.word_length)

    def text_rule(self):
        return "Every word used must be {} letters long.".format(self.word_length)


CONSTRAINT_LOOKUP = {
    'score': ScoreConstraint,
    'distinct_row_column': DistinctRowColumnConstraint,
    'no_adjacent_equal': NoAdjacentEqualConstraint,
    'no_knights_equal': NoKnightEqualConstraint,
    'word_length_constraint': WordLengthConstraint,
    'letter_bag': LetterBagConstraint,
}

# Old semaphore extraction -- currently not used
def semaphore_extract(grid, word_locations, answer):
    lookup = {DIRECTION_NAMES[direction]: [] for direction in DIRECTIONS}

    for word, location in word_locations:
        _, _, dx, dy = location
        lookup[DIRECTION_NAMES[(dx, dy)]].append(word)
    
    def choose_word(direction):
        if lookup[direction]:
            return random.choice(lookup[direction])
        else:
            return '???'

    extract = []
    for c in answer:
        d1, d2 = SEMAPHORE_ALPHABET[c]
        extract.append((choose_word(d1), choose_word(d2)))
    
    return extract, 'semaphore_extraction.html'


def unused_extract(grid, word_locations, answer):
    n, m = len(grid), len(grid[0])

    used = [[False for _ in range(m)] for _ in range(n)]

    for word, location in word_locations:
        x, y, dx, dy = location
        for i in range(len(word)):
            cx, cy = x + i*dx, y + i*dy
            used[cy][cx] = True

    unused = []
    for y in range(n):
        for x in range(m):
            if not used[y][x]:
                unused.append(grid[y][x])
    
    diff_letters = len(answer) - len(unused)

    def format_num(n):
        if n > 0:
            return "+" + str(n)
        else:
            return str(n)

    offsets = [format_num(ord(c1) - ord(c2)) for c1, c2 in zip(answer, unused)]
    if diff_letters > 0:
        offsets += ["({} more)".format(diff_letters)]
    elif diff_letters < 0:
        offsets += ["X"] * (-diff_letters)

    extract = ' '.join(offset for offset in offsets)
    return extract, 'unused_extraction.html'

EXTRACTION_LOOKUP = {
    'semaphore': semaphore_extract,
    'unused': unused_extract
}

def find_word(grid, w):
    l = len(w)
    n, m = len(grid), len(grid[0])
    
    locations = []
    for y in range(n):
        for x in range(m):
            for dx, dy in DIRECTIONS:
                ex, ey = x + dx*(l-1), y + dy*(l-1)
                if ex < 0 or ex >= m or ey < 0 or ey >= n:
                    continue
                if all(grid[y + i*dy][x + i*dx] == w[i] for i in range(l)):
                    locations.append((x, y, dx, dy))
    return locations


def check(grid, words, puzzle):
    if len(grid) != puzzle.dimensions[0] or any(len(row) != puzzle.dimensions[1] for row in grid):
        return None, "Your grid must have {} rows and {} columns.".format(
            puzzle.dimensions[0], puzzle.dimensions[1]
        )

    gridstr = ''.join(''.join(row) for row in grid)
    if not all(c in puzzle.letters for c in gridstr):
        return None, "This grid uses an invalid letter. Your word search can only use the following letters: {}".format(
            ' '.join(puzzle.letters))

    if len(set(words)) != len(words):
        return None, "All words in your grid must be unique."
    for i, word in enumerate(words):
        if len(word) <= 3:
            return None, "You may not use words of length 3 or less."
        if word not in WORDS:
            return None, "The word {} is not in the allowed wordlist.".format(word)
        for i2, word2 in enumerate(words):
            if i2 == i:
                continue

            if word in word2 or word[::-1] in word2:
                return None, "The word {} is contained entirely within the word {}.".format(word, word2)
    
    # Check if words in grid
    word_locations = []
    for word in words:
        locations = find_word(grid, word)
        if len(locations) == 0:
            return None, "The word {} cannot be found in the grid.".format(word)
        if len(locations) >= 2:
            return None, "The word {} appears more than once in the grid.".format(word)
        word_locations.append((word, locations[0]))
        

    for constraint in puzzle.constraints:
        res, err = constraint.check(grid, words)
        if not res:
            return None, err

    extract = EXTRACTION_LOOKUP[puzzle.extraction_method](grid, word_locations, puzzle.answer)
    return extract, None