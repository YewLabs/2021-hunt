'''Generate GCS urls for Library of Images puzzle'''

import hashlib
from num2words import num2words

def convert_num_to_words(num):
    return [x.strip().upper() for x in num2words(num).replace("-"," ").replace(",","").split()]


INFINITE_SALT = b"RsrBf45jdNyb6wMa"
def get_hash(s):
    s = bytes(s, 'utf-8')
    h = hashlib.sha256()
    h.update(s + INFINITE_SALT)
    return h.hexdigest()

IMAGE_URL = 'https://storage.googleapis.com/infinite-corridor/loi-{}.png'
def get_url(s):
    return IMAGE_URL.format(get_hash(s.strip().lower()))

def generate_context(puzzle):
    puzzle_id = puzzle.y2021puzzledata.infinite_id
    puzzle_answer = puzzle.answer

    words = ['THE', 'ANSWER', 'TO', 'PUZZLE'] + convert_num_to_words(puzzle_id) + ['IS', puzzle.answer]
    urls = [get_url(word) for word in words]

    return {'image_urls': urls}



if __name__ == '__main__':
    pass



'''
Code below for generating testsolving version. "template" folder contains the files for the repeated images (A,B,C,"the","answer", etc.). index files contain the html for numbers with different number of words in them.

This code is rather slow (fine for 500 but probably not for 20k cases, and probably you want to just generate A through Z first and have some more efficient function combine them.



file = open("infiniteCorridor3/infinitePuzzleWordsTest.txt")
d = [(line.rstrip('\n')).rstrip(' ').lower() for line in file]

puzznum = 1

for j in range(0,len(d)):
    print(puzznum)
    src = 'infiniteCorridor3/template'
    dest = 'infiniteCorridor3/' + str(puzznum)
    destination = shutil.copytree(src,dest)
    startnum = 5
    n = num2words(puzznum).replace("-"," ").replace(",","").split()
    for k in range(len(n)):
        imsave('infiniteCorridor3/' + str(puzznum) + '/1.' + str(startnum) + '.png', makeImage(n[k]))
        startnum += 1
    shutil.copyfile('infiniteCorridor3/is.png','infiniteCorridor3/' + str(puzznum) + '/1.' + str(startnum) + '.png')
    startnum += 1
    imsave('infiniteCorridor3/' + str(puzznum) + '/1.' + str(startnum) + '.png', makeImage(d[j]))
    shutil.copyfile('infiniteCorridor3/index' + str(len(n)) + '.html','infiniteCorridor3/' + str(puzznum) + '/index.html')
    puzznum += random.randint(1,10)
    print(j)
'''
