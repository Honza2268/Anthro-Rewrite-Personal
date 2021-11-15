from PIL import Image
import os

os.chdir('G:\SteamLibrary\steamapps\common\RimWorld\Mods\Anthro-Rewrite\Textures\Anthro\Heads')

files = [f for f in os.listdir() if '.png' in f]

groups = [f.split('_')[1] for f in files]
groups = list(set(groups))

bad = [files[f]
       for f in range(len(files)) if 'm.png' in files[f] or 'Female' in files[f]]

for f in bad:
    os.remove(f)

files = [f for f in os.listdir() if '.png' in f]

'''for f in files:
    _, name = f.split('_', 1)
    os.rename(f, name)'''
