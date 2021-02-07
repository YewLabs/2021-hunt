import random
import re

def make_letter_sets(phrase):
    s = phrase.upper()
    s = re.sub('[^A-Z]', '', s)

    s = [list(s[i:i+5]) for i in range(0, len(s), 5)]
    for i in s:
        random.shuffle(i)
    return ' '.join([''.join(k) for k in s])

def make_trigrams(phrase):
    s = phrase.upper()
    s = re.sub('[^A-Z]', '', s)
    if len(s) % 3 != 0:
        print('wrong length!')
        return ''

    s = [s[i:i+3] for i in range(0, len(s), 3)]
    random.shuffle(s)
    return ' '.join(s)

phrase = input('Enter a phrase: ')

with open('out.csv', 'w') as fd:
    # fd.write(f'> Each set of 5 letters needs to be unscrambled to reveal a hidden message. What is it?\n\n{make_letter_sets(phrase)}\n\n[answer {phrase}]')
    fd.write(f'> Rearrange these trigrams (and add spaces) to reveal a hidden message. What is it?\n\n{make_trigrams(phrase)}\n\n[answer {phrase}]')
