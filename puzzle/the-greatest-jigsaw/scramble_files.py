import os
import random

os.chdir('Jigsaw')
filelist = os.listdir()
random.shuffle(filelist)

rotate = True

if rotate:
    from PIL import Image

i = 1
for f in filelist:
    new_name = f'img{i:03}.png'
    os.rename(f, new_name)
    if rotate:
        im = Image.open(new_name)
        angle = random.randint(0,3)*90
        out = im.rotate(angle, expand=True)
        out.save(new_name)
    i += 1
