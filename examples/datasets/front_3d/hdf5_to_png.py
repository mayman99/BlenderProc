import h5py
import numpy as np
import os
import cv2
import csv

data_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp'
output_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp\\images_from_metadata_fix'
points = np.load("C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\blenderproc\\resources\\front_3D\\points.npy")
files = os.listdir(data_path)

metadata_list = []
with open("C:\\Users\\super\\ws\\data\\front_3d\\temp\\metadata_fixed_new.jsonl", "r") as f:
    metadata_list = list(f)

for idx, _ in enumerate(metadata_list):
    hdf = h5py.File(os.path.join(data_path, str(idx)+".hdf5"),'r')
    np_array = np.array(hdf["class_segmaps"])
    rgb_img = np.zeros((512, 512, 3), dtype='uint8')
    for pixel_x in range(np_array.shape[0]):
        for pixel_y in range(np_array.shape[1]):
            v = np_array[pixel_x][pixel_y]
            rgb_img[pixel_x][pixel_y] = points[v]

    cv2.imwrite(os.path.join(output_path, str(idx)+'.png'), rgb_img)

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
