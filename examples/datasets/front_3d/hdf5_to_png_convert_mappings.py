import h5py
import numpy as np
import os
import cv2
import csv

data_path = 'C:\\Users\\super\\ws\\data\\front_3d\\25_5_2023_bedrooms'
output_path = 'C:\\Users\\super\\ws\\data\\front_3d\\25_5_2023_bedrooms\\lhs_27'
points = np.load("C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\blenderproc\\resources\\front_3D\\lhs_27.npy")
points_max = points.shape[0] - 1
files = os.listdir(data_path)

old_id_to_cat = {}
old_cat_to_id = {}
new_id_to_cat = {}
new_cat_to_id = {}
path = 'C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\blenderproc\\resources\\front_3D'
old_file = '3D_front_mapping_merged_new_complete.csv'
new_file = 'bedroom_minimal.csv'

with open(os.path.join(path, old_file), 'r', encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        old_cat_to_id[row["name"]] = int(row["id"])
        old_id_to_cat[row["id"]] = row["name"]

with open(os.path.join(path, new_file), 'r', encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        new_cat_to_id[row["name"]] = int(row["id"])
        new_id_to_cat[row["id"]] = row["name"]

def convert_from_old_csv_mapping(old_id: int):
    old_cat = old_id_to_cat[str(old_id)]
    if old_cat not in new_cat_to_id:
        return points_max
    return new_cat_to_id[old_cat]

for f in files:
    necessary_cats_exists = False
    if '.hdf5' in f:
        hdf = h5py.File(os.path.join(data_path, f),'r')
        np_array = np.array(hdf["class_segmaps"])
        rgb_img = np.zeros((512, 512, 3), dtype='uint8')
        for pixel_x in range(np_array.shape[0]):
            for pixel_y in range(np_array.shape[1]):
                v = np_array[pixel_x][pixel_y]
                new_id = convert_from_old_csv_mapping(v)

                if new_id > len(points):
                    rgb_img[pixel_x][pixel_y] = points[points_max]
                else:
                    rgb_img[pixel_x][pixel_y] = points[new_id]

        cv2.imwrite(os.path.join(output_path, f.split('.')[0]+'.png'), rgb_img)
