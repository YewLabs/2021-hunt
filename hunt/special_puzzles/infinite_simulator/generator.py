'''Generate GCS urls for Infinite Corridor Simulator puzzle'''

import hashlib


INFINITE_SALT = b"RsrBf45jdNyb6wMa"
def get_hash(s):
    s = bytes(s, 'utf-8')
    h = hashlib.sha256()
    h.update(s + INFINITE_SALT)
    return h.hexdigest()


PUZZLE_URL = 'https://infinite-corridor.storage.googleapis.com/ics-{}.json'
def get_url(s):
    return PUZZLE_URL.format(get_hash(s.strip()))


def generate_context(puzzle):
    puzzle_id = puzzle.y2021puzzledata.infinite_id

    url = get_url(str(puzzle_id))
    print(url)

    return {'ics_url': url}


if __name__ == '__main__':
    pass