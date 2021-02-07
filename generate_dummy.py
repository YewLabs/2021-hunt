#!/usr/bin/python

import csv
import glob
import json
import os
import shutil



DUMMYS_PATH = 'data/dummys.tsv'
with open(DUMMYS_PATH) as f:
    reader = csv.reader(f, delimiter="\t")
    next(reader)
    for dummyInfo in reader:
        if len(dummyInfo) == 0:
            continue
        pid = int(dummyInfo[0])
        answer = dummyInfo[1]
        title = dummyInfo[2]
        link = dummyInfo[3]
        bdir = os.path.join('puzzle', 'dummy%d' % (pid))
        if os.path.exists(bdir):
            shutil.rmtree(bdir)
        os.mkdir(bdir)
        with open(os.path.join(bdir, 'index.html'), 'w') as indexFile:
            if link.strip() == 'ANSWER':
                indexFile.write("""<p>Answer: %s</p>""" % (answer))
            else:
                indexFile.write("""<p>This puzzle isn't written yet! Solve <a href="%s">this puzzle</a> instead. Contact an editor once you solve it!.</p>""" % (link))
        with open(os.path.join(bdir, 'metadata.json'), 'w') as mdFile:
            mdFile.write("""{"puzzle_title": "%s (Dummy Puzzle)", "credits": "by Skynet", "answer": "%s", "puzzle_idea_id": %d, "puzzle_slug": "dummy%d"}""" % (title, answer, pid, pid))
