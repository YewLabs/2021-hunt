#!/usr/bin/python3

import csv
import glob
import hashlib
import os
import shutil

BASE_PATH = 'static/puzzle_files/'
UNLOCK_IMAGE_PATH = 'static/unlock_images/'

def key(puzzle, solution=False):
    v = puzzle
    if solution:
        v += '_solution'
    return hashlib.sha256((v + '_SROOT_KEY').encode('utf-8')).hexdigest()[-16:]

UNLOCKS_PATH = 'data/unlocks.tsv'

def obfuscate(tid):
    return hashlib.sha256(('%s:%d' % ("SPY21_IMG", tid)).encode('utf-8')).hexdigest()

def upload():
    for topdir in ('puzzle', 'round'):
        for f in glob.glob(topdir + '/**', recursive=True):
            if os.path.isdir(f):
                continue
            if f.endswith('.tmpl'):
                continue
            _, puzzle, rest = f.split('/',2)
            if rest == 'metadata.json' or rest == 'extra.json' or rest == 'hints.json':
                continue

            solution = False
            if rest.startswith('solution/'):
                solution = True
                _, rest = rest.split('/', 1)

            if topdir != 'puzzle':
                puzzle = '%s_%s' % (topdir, puzzle)
            fkey = key(puzzle, solution)
            print('%s (%s, %s): %s' % (puzzle, solution, fkey, rest))
            dest = os.path.join(BASE_PATH, fkey, rest)
            print('%s %s' % (f, dest))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(f, dest)

    os.makedirs(UNLOCK_IMAGE_PATH, exist_ok=True)
    with open(UNLOCKS_PATH) as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for unlockInfo in reader:
            if len(unlockInfo) == 0:
                continue
            uid = unlockInfo[0]
            if len(unlockInfo) > 2 and unlockInfo[2]:
                tid = int(unlockInfo[2])
            else:
                continue
            fkey = obfuscate(tid)
            src = 'unlock_extras/%s.png' % (uid)
            small_src = 'unlock_extras/%s.png' % (uid)
            if os.path.exists(src):
                if not os.path.exists(small_src):
                    small_src = src
                shutil.copy(src, os.path.join(UNLOCK_IMAGE_PATH, '%s.png' % (fkey)))
                shutil.copy(small_src, os.path.join(UNLOCK_IMAGE_PATH, '%s_small.png' % (fkey)))

                print('%s %s' % (src, fkey))

upload()
