import h5py
import numpy as np
import os
import cv2
import csv
import json
import random

def should_not_include(obj_name):
    if 'wall' in obj_name or 'floor' in obj_name or 'ceiling' in obj_name or 'door' in obj_name or 'window' in obj_name or 'pocket' in obj_name or 'front' in obj_name or 'back' in obj_name or 'baseboard' in obj_name or 'hole' in obj_name or 'slab' in obj_name or 'lamp' in obj_name:
        return True
    return False

data_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled'
output_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\images'
points = np.load("C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\blenderproc\\resources\\front_3D\\points.npy")
images_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\images\\'
files = os.listdir(data_path)

id_to_cat = {}
cat_to_id = {}
path = 'C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\blenderproc\\resources\\front_3D'
old_file = '3D_front_mapping_merged_new_complete.csv'

with open(os.path.join(path, old_file), 'r', encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        cat_to_id[row["name"]] = int(row["id"])
        id_to_cat[row["id"]] = row["name"]

metadata_list = []
with open("C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\images\\metadata.jsonl", "r") as f:
    metadata_list = list(f)

def conver_rot_data(rot_data_path:str, output_path:str):
    hdfs = os.listdir(rot_data_path)
    for idx, file in enumerate(hdfs):
        if '.hdf5' not in file:
            continue
        hdf = h5py.File(os.path.join(rot_data_path, file),'r')
        np_array = np.array(hdf["class_segmaps"])
        rgb_img = np.zeros((np_array.shape[0], np_array.shape[1], 3), dtype='uint8')
        rgb_images = []
        for v in range(len(points)):
            if v == 51 or v == 0 or should_not_include(id_to_cat[str(v)]):
                continue
            for pixel_x in range(np_array.shape[0]):
                for pixel_y in range(np_array.shape[1]):
                    if np_array[pixel_x][pixel_y] == 0:
                        rgb_img[pixel_x][pixel_y] = points[51]
                    else:
                        rgb_img[pixel_x][pixel_y] = points[v]
            # rgb_images.append(rgb_img)
            cv2.imwrite(os.path.join(output_path, file.split('.')[0]+ "_" + str(v) +'.png'), rgb_img)

conver_rot_data("C:\\Users\\super\\ws\\data\\rotation_data", "C:\\Users\\super\\ws\\data\\rotation_data\\all_images")

    
def func():
    for idx, json_str in enumerate(metadata_list):
        result = json.loads(json_str)
        hdf = h5py.File(os.path.join(data_path, result["file_name"].split('.')[0]+".hdf5"),'r')
        np_array = np.array(hdf["class_segmaps"])
        rgb_img = np.zeros((512, 512, 3), dtype='uint8')
        for pixel_x in range(np_array.shape[0]):
            for pixel_y in range(np_array.shape[1]):
                v = np_array[pixel_x][pixel_y]
                rgb_img[pixel_x][pixel_y] = points[v]

        cv2.imwrite(os.path.join(output_path, result["file_name"].split('.')[0]+'.png'), rgb_img)


# for f in files:
#     if '.hdf5' in f:
#         hdf = h5py.File(os.path.join(data_path, f),'r')
#         np_array = np.array(hdf["class_segmaps"])
#         rgb_img = np.zeros((512, 512, 3), dtype='uint8')
#         for pixel_x in range(np_array.shape[0]):
#             for pixel_y in range(np_array.shape[1]):
#                 v = np_array[pixel_x][pixel_y]
#                 rgb_img[pixel_x][pixel_y] = points[v]

#         cv2.imwrite(os.path.join(output_path, f.split('.')[0]+'.png'), rgb_img)
