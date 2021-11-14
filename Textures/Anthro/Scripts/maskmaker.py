from PIL import Image
import os

os.chdir('G:\SteamLibrary\steamapps\common\RimWorld\Mods\Anthro-Rewrite\Textures\Anthro\Heads')

allfiles = [f for f in os.listdir() if '.png' in f]
files = [f for f in allfiles if 'm.png' not in f]
l = len(files)

for n, f in enumerate(files):
    wrds = f.split('.')
    if f'{wrds[0]}m.{wrds[1]}' in allfiles:
        continue
    print(f'{n+1}/{l}: {f}')

    img = Image.open(f)
    maska = Image.new('RGBA', (256, 256))
    x, y = img.size

    for w in range(x):
        for h in range(y//2):
            o_r, o_g, o_b, o_a = img.getpixel((w, h))
            maska.putpixel((w, h), (0 if o_r != 0 else 0,
                                    0 if o_g == 0 else 255, 0 if o_b != 0 else 0, 0 if o_a == 0 else 255))
        for h in range(y//2, y):
            o_r, o_g, o_b, o_a = img.getpixel((w, h))
            maska.putpixel((w, h), (0 if o_r == 0 else 255,
                                    0 if o_g != 0 else 0, 0 if o_b != 0 else 0, 0 if o_a == 0 else 255))

    maska.save(f'{wrds[0]}m.{wrds[1]}')

    # break
