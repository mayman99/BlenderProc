import h5py
import numpy as np
import os
import cv2
import csv, json
from scipy.ndimage import label
from collections import Counter

data_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp'
images_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp\\images'
json_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp\\temp\\new_metadata.jsonl'
points = np.load("C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\blenderproc\\resources\\front_3D\\points.npy")
files = os.listdir(data_path)

max_hdf5 = 2853
id_to_cat = {}
cat_to_id = {}
path = 'C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\blenderproc\\resources\\front_3D\\3D_front_mapping_merged_new_complete.csv'


def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print(filename, " does not exist")

def should_not_include(obj_name):
    if 'wall' in obj_name or 'ceiling' in obj_name or 'door' in obj_name or 'window' in obj_name or 'pocket' in obj_name or 'front' in obj_name or 'back' in obj_name or 'baseboard' in obj_name or 'void' in obj_name or 'hole' in obj_name or 'slab' in obj_name:
        return True
    return False

with open(path, 'r', encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        cat_to_id[row["name"]] = int(row["id"])
        id_to_cat[row["id"]] = row["name"]

metadata_list = []
metadata_list_new = []
with open("C:\\Users\\super\\ws\\data\\front_3d\\temp\\metadata_fixed.jsonl", "r") as f:
    metadata_list = list(f)

new_texts = []
for idx, _ in enumerate(metadata_list):
    hdf = h5py.File(os.path.join(data_path, str(idx)+".hdf5"),'r')
    np_array = np.array(hdf["class_segmaps"])
    # find unique values
    unique = np.unique(np_array)
    # map the ids to the categories
    unique = [id_to_cat[str(x)] for x in unique]
    text = ''
    if (len(unique) < 4):
        text = 'empty'
    else:
        for i in range(len(unique)):
            if not should_not_include(unique[i]):
                text += unique[i] + ', '
    new_texts.append(text)

new_index = 0
for index, json_str in enumerate(metadata_list):
    result = json.loads(json_str)
    if new_texts[index] != 'empty':
        result["file_name"] = str(new_index) + ".png"
        result["text"] = "segmentation map, orthographic view, furnished apartment, Bedroom,"+ new_texts[index]
        metadata_list_new.append(result)
        new_index += 1
    else:
        # delete the file
        delete_file(os.path.join(images_path, str(index)+".png"))
        # rename the files
        for i in range(index+1, max_hdf5):
            if os.path.exists(os.path.join(images_path, str(i)+".png")):
                os.rename(os.path.join(images_path, str(i)+".png"), os.path.join(images_path, str(i-1)+".png"))

with open("C:\\Users\\super\\ws\\data\\front_3d\\temp\\metadata_fixed_new.jsonl", "w") as f:
    for item in metadata_list_new:
        json.dump(item, f)
        f.writelines('\n')

