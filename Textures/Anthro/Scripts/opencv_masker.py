import os
import numpy as np
import cv2
import imutils
from PIL import Image
import threading
import queue


def cv2_to_pil(image: np.ndarray):
    return Image.fromarray(cv2.cvtColor(image,cv2.COLOR_BGR2RGB))


def pil_to_cv2(image: Image.Image):
    return np.asarray(image)


def get_mask(image: np.ndarray, tresh_low: np.ndarray, tresh_high:np.ndarray) -> np.ndarray:
    return cv2.inRange(image.copy(), tresh_low, tresh_high)


def get_shapes(image: np.ndarray, mask_params = (np.array([90, 90, 90]), np.array([255, 255, 255]))) -> list:
    shapes = []
    sizes = []
    shapemask = get_mask(image, *mask_params)
    # get contours from image
    cnts = cv2.findContours(shapemask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # cycle through contours
    for c in cnts:
        mask = np.zeros_like(image)
        out = np.zeros_like(image)
    # create texture from contour
        cv2.drawContours(mask, [c], -1, (255,)*3, -1)
    # mask out original image
        out[mask==255] = image[mask==255]
    # add masked out image to return list
        shapes.append(out.copy())
        sizes.append(np.size(c))
        
    return shapes, sizes


def is_symetrical(image: np.ndarray, treshold: float = 5, return_image: bool = False) -> bool:
    work_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)                             #convert image to greyscale
    w,*_ = work_image.shape                                                                 #get image size
    sym_line = w//2                                                                         #get vertical mid point
    img_half_1 = work_image[:, :sym_line]                                                   #left half of original image
    img_half_2 = work_image[:, sym_line:]                                                   #right half of original image
    img_half_2 = cv2.flip(img_half_2, 2)                                                    #flip right side
    differences = cv2.compare(img_half_1, img_half_2, cv2.CMP_NE)                           #compare split images
    ret_val = True if np.sum(differences)/2.55/np.size(differences) <= treshold else False
    return img_half_1 if ret_val and return_image else ret_val
        

def get_groups(files: list, split_faces: bool = False) -> list:
    heads = files.copy()
    # extract head shapes with face variants from file names
    subgroups = list(set(f.split('_')[0] for f in files))
    subgroups.sort()
    # extract head shapes only from file names
    groups = list(set(subgroups[i][:-1] for i in range(len(subgroups))))
    groups.sort()
    
    if split_faces:
        faces = [[f for f in heads if f.startswith(f'{subgroups[i]}_')] for i in range(len(subgroups))]
    #divide by head shape then face type
        shapes = [[f for f in faces if groups[i] in f[0] and f[0][len(groups[i])+1] == '_'] for i in range(len(groups))]

    else:
    # divide by head shape only
        shapes = [[f for f in files if groups[i] in f and f[len(groups[i])+1] == '_'] for i in range(len(groups))]

    return subgroups if split_faces else groups, shapes


def generate_color_mask_part(image: np.ndarray, color: tuple) -> Image.Image:
    work_image = cv2_to_pil(image.copy())
    work_image = Image.Image.convert(work_image, 'RGBA')
    w,h = work_image.size
    for x in range(w):
        for y in range(h):
            rgba = work_image.getpixel((x, y))
            work_image.putpixel((x, y), (0,)*4 if rgba[:3] == (0, 0, 0) else color)
    return work_image


def reconstruct_image_cv2(image: np.ndarray) -> np.ndarray:
    work_image = image.copy()
    work_image = cv2.flip(work_image, 2)
    work_image = cv2.hconcat([image.copy(), work_image])
    return work_image


def reconstruct_image_pil(image: Image.Image) -> Image.Image:
    return Image.fromarray(reconstruct_image_cv2(pil_to_cv2(image)))


def merge_color_mask_parts(images: list) -> np.ndarray:
    pass


def masking_process(head_group, primary_mask, secondary_mask):
    # has structure: {str (image_name): np.array (the image), ...}
    faces = {}
    # has structure: {str (image_name): {str (shape_name): np.array (shape), ...}, ...}
    shapes_list = {}
    # has structure: {str (image_name): int (size), ...}
    shapes_sizes = {}
    # has structure: {int (color value): [{str (shape): np.array (shape)}, ...], ...}
    color_list = {}
    # has structure: {int (color value): int (size), ...}
    color_sizes = {}
    # has structure: {srt (mask_part_name): Image.Image (mask_part), ...}
    color_mask_parts = {}
    
    for head in head_group:
        work_face = cv2.imread(head)
        # check face for symetry, add them to dict with their name as a key
        if is_symetrical(work_face):
            faces[f'{head}_half'] = cv2.cvtColor(is_symetrical(work_face, return_image=True), cv2.COLOR_GRAY2BGR)
        else:
            faces[head] = work_face
    
    # split images into specific shapes, add dict of them with their shape names to dict with their origins name as a key
    for name, face in list(faces.items()):
        shapes, sizes = get_shapes(face)
        shapes_list[name] = {f'{i}_{name}': shapes[i] for i in range(len(shapes))}
        shapes_sizes.update({f'{i}_{name}': sizes[i] for i in range(len(sizes))}) 
    
    # go through shapes, check their color, split their dict entries into dict with the color as a key
    for shapes in list(shapes_list.values()):
        for name, shape in list(shapes.items()): 
            # highest color channel value in shape
            max_val = np.max(cv2.cvtColor(shape, cv2.COLOR_BGR2GRAY))
            # append shape to its color value dict entry, create new if it doesn't exist
            if max_val in color_list.keys():
                color_list[max_val][name] = shape
            else:
                color_list[max_val] = {name: shape}
                
    # go through colors, get their total pixel count
    for color, shapes in list(color_list.items()):
        sum_size = sum(shapes_sizes[shape] for shape in list(shapes.keys()))
        color_sizes[color] = sum_size
    
    # assign their mask colors based on size (dominant -> primary, other -> secondary)
    dominant_color = max(color_sizes, key=lambda k: color_sizes[k])
    for color, shapes in list(color_list.items()):
        mask_color = primary_mask if color == dominant_color else secondary_mask
        for name, shape in list(shapes.items()):
            color_mask_parts[name] = generate_color_mask_part(shape, mask_color)
    
    # get names of mask part image grups for sorting
    part_groups = list(set(['_'.join(p.split('_')[1:]) for p in color_mask_parts]))
    # sort mask part images into groups
    grouped_images = {p_g: [] for p_g in part_groups}
    for part_group in part_groups:
        for part in color_mask_parts:
            if part_group in part:
                grouped_images[part_group].append(color_mask_parts[part])
                
    for image_group, images in list(grouped_images.items()):
        temp = Image.new('RGBA', images[0].size)
        for image in images:
            temp = Image.alpha_composite(temp, image)
        if image_group.endswith('_half'):
            temp = reconstruct_image_pil(temp)
        image_name = f'{image_group.split(".")[0]}m.png'
        temp = temp.convert('RGB')
        temp.save(image_name)


def process_wrapper(id, head_group, primary_mask, secondary_mask, counter=[0], amount=0):
    print(f'Starting work on group {id}...')
    counter[1] += 1
    masking_process(head_group, primary_mask, secondary_mask)
    counter[0] += 1
    counter[1] -= 1
    print(f'Finished work on group {id}. ({counter[0]}/{amount})')


def main():
    
    os.chdir('G:\SteamLibrary\steamapps\common\RimWorld\Mods\Anthro-Rewrite\Textures\Anthro\Heads')
    
    # RGBA
    primary_mask = (255, 0, 0, 255)
    secondary_mask = (0, 255, 0, 255)

    # get all textures including masks as long as they are .png and conatin at leas 1 underscore
    # filter out existing masks
    allfiles = [f for f in os.listdir() if '.png' in f and '_' in f]
    files = [f for f in allfiles if 'm.png' not in f]

    # get groups of images: [<- returned list [<- list of images of head shape ], [ ... ], ... ]
    groups = dict(zip(*get_groups(files)))
    
    counter = [0, 0]
    
    # processes groupings of head shapes
    threads = [threading.Thread(None, process_wrapper, args=(id, hg, primary_mask, secondary_mask, counter, len(groups))) for id, hg in groups.items()]
    
    q = queue.Queue()
    for thread in threads:
        q.put(thread)
        
    while not q.empty():
        if counter[1] < 5:
            q.get().start()
        
 
        

        



if __name__ == '__main__':
    main()
    


