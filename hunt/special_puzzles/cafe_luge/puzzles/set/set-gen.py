import glob
from itertools import permutations

out_fd = open('set.yml', 'w')

out_fd.write('''name: set
difficulty: 3/10
coolness: 9/10
time: 3:00

questions:
''')

first = False
for filename in glob.glob('./*.png'):
    filename = filename[2:]
    solns = [''.join(k) for k in permutations(filename[:3])]

    if first:
        out_fd.write('\n')
    first = True
    out_fd.write('    - question:\n')
    out_fd.write('        - text: "What are the letters of the three cards that form a set in this image? (Enter your answer without a space, e.g. \\\"ABC\\\".)"\n\n')
    out_fd.write(f'        - image: set/{filename}\n\n')

    for soln in solns:
        out_fd.write(f'        - answer: {soln.lower()}\n')
