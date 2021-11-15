from PIL import Image
import os


def is_black(color, accuracy=255, accu_per_channel=50):
    return True if color[0] + color[1] + color[2] <= accuracy and color[3] > 0 and color[0] <= accu_per_channel and color[1] <= accu_per_channel and color[2] <= accu_per_channel else False


os.chdir('G:\SteamLibrary\steamapps\common\RimWorld\Mods\Anthro-Rewrite\Textures\Anthro\Heads')

allfiles = [f for f in os.listdir() if '.png' in f]
files = [f for f in allfiles if 'm.png' not in f]
l = len(files)

mask_colors = [(255, 0, 0), (0, 255, 0)]

for n, f in enumerate(files):
    wrds = f.split('.')
    if f'{wrds[0]}m.{wrds[1]}' in allfiles:
        continue
    print(f'{n+1}/{l}: {f}')

    img = Image.open(f, 'r')
    maska = Image.new('RGBA', img.size)

    x, y = img.size

    colors = {}

    # make mask layout
    for w in range(x):
        for h in range(y):
            oR, oG, oB, oA = img.getpixel((w, h))
            clra = (oR, oG, oB, oA)
            black = (0, 0, 0, 255)
            blank = (0, 0, 0, 0)
            maska.putpixel((w, h), black if is_black(clra) else blank)

            clr = (oR, oG, oB)
            if clr in colors:
                colors[clr] += 1
            else:
                colors[clr] = 1

    colors = dict(
        sorted(colors.items(), key=lambda item: item[1], reverse=True)
    )

    colors_filtered = list(colors.keys())[1:]

    # get regions
    for w in range(x):
        for h in range(y):
            clra = img.getpixel((w, h))
            clr = (clra[0], clra[1], clra[2])
            if clr in colors_filtered:
                maska.putpixel(
                    (w, h), mask_colors[colors_filtered.index(clr) % 2])

    # print(colors_filtered)

    # maska.show()
    maska.save(f'{wrds[0]}m.{wrds[1]}')

    # break
