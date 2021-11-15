from PIL import Image, ImageDraw
import os
import colour


def is_black(color, accuracy=255, accu_per_channel=50, alpha=255):
    return True if color[0] + color[1] + color[2] <= accuracy and not (not color[3] <= alpha) and color[0] <= accu_per_channel and color[1] <= accu_per_channel and color[2] <= accu_per_channel else False


def under_treshold(rgba1, rgba2, total_tresh=150, channel_tresh=50, alpha_tresh=50):
    if len(rgba1) != 4:
        rgba1 += (255,)
    if len(rgba2) != 4:
        rgba2 += (255,)

    diff = tuple(map(lambda i, j: abs(i-j), rgba1, rgba2))

    return True if sum(list(diff)) <= total_tresh and diff[0] <= channel_tresh and diff[1] <= channel_tresh and diff[2] <= channel_tresh and diff[3] <= alpha_tresh else False


def bruh(groups, groupedfiles):
    for num, fileset in enumerate(groupedfiles):
        group = groups[num]
        wrds = fileset[0].split('.')

        '''if f'{wrds[0]}m.{wrds[1]}' in allfiles:
            continue'''  # for skipping already masked files

        print(f'{num+1}/{len(groupedfiles)}: {group}')

        img = Image.open(fileset[0], 'r')
        maska = Image.new('RGBA', img.size)

        x, y = img.size

        colors = {}

        '''# make mask layout
        for w in range(x):
            for h in range(y):
                oR, oG, oB, oA = img.getpixel((w, h))
                clra = (oR, oG, oB, oA)

                maska.putpixel((w, h), black if is_black(clra) else white)

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
                        (w, h), mask_colors[colors_filtered.index(clr) % 2])'''

        # print(colors_filtered)

        # maska.show()
        # maska.save(f'{wrds[0]}m.{wrds[1]}')

        break


def get_img_outlines(img: Image.Image) -> Image.Image:
    w, h = img.size
    temp = Image.new('RGBA', (w, h))
    for x in range(w):
        for y in range(h):
            rgb = img.getpixel((x, y))[:3]
            # print(rgb)
            temp.putpixel((x, y), (0, 0, 0) if under_treshold(
                (0, 0, 0), rgb) else (255, 255, 255, 0))
    return temp


def image_to_mask(img: Image.Image) -> Image.Image:
    w, h = img.size
    temp = Image.new('RGBA', (w, h))

    for x in range(w):
        for y in range(h):
            rgba = img.getpixel((x, y))
            temp.putpixel((x, y), (0, 0, 0, 255) if rgba ==
                          (0, 0, 0, 0) else (255, 255, 255, 255))
    return temp


def get_shapes(img: Image.Image, maxshapes=5, divider=15):
    w, h = img.size
    shapes = []
    work_img = img.copy().convert('RGB')

    working = True
    while working:
        changed = False
        shape_img = Image.new('RGBA', (w, h))
        for x in range(0, w, divider):
            for y in range(0, h, divider):
                rgb = work_img.getpixel((x, y))[:3]
                # print(rgb)
                if rgb == (0, 0, 0):
                    pass
                else:
                    ImageDraw.floodfill(work_img, (x, y), (255, 0, 0))
                    changed = True
                    break
            if changed:
                break
        if len(shapes) == maxshapes or not changed:
            working = False
            break

        for x in range(w):
            for y in range(h):
                rgb = work_img.getpixel((x, y))
                shape_img.putpixel((x, y), (255 if rgb == (
                    255, 0, 0) else 0, 0, 0, 255 if rgb == (255, 0, 0) else 0))
                if rgb == (255, 0, 0):
                    work_img.putpixel((x, y), (0, 0, 0))
        shapes.append(shape_img.copy())

    return shapes


def main():
    os.chdir(
        'G:\SteamLibrary\steamapps\common\RimWorld\Mods\Anthro-Rewrite\Textures\Anthro\Heads')

    allfiles = [f for f in os.listdir() if '.png' in f]
    files = [f for f in allfiles if 'm.png' not in f]

    groups = list(set(f.split('_')[0] for f in files))
    groups.sort()

    groupedfiles = [[f for f in files if groups[i] in f]
                    for i in range(len(files)//3)]

    mask_colors = [(255, 0, 0), (0, 255, 0)]

    img = get_img_outlines(Image.open(files[0]))
    shapes = get_shapes(img)
    print(shapes)
    for shape in shapes:
        shape.show()


if __name__ == '__main__':
    main()
