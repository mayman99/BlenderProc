import h5py
import numpy as np
import os
from PIL import Image
import cv2

data_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp'
output_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp'
points = np.load("C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\points.npy")
files = os.listdir(data_path)

for f in files:
    if 'hdf5' in f:
        hdf = h5py.File(os.path.join(data_path, f),'r')
        color = np.array(hdf["colors"])
        np_array = np.array(hdf["class_segmaps"])
        rgb_img = np.zeros((512, 512, 3), dtype='uint8')
        for pixel_x in range(np_array.shape[0]):
            for pixel_y in range(np_array.shape[1]):
                rgb_img[pixel_x][pixel_y] = points[np_array[pixel_x][pixel_y]]
        cv2.imwrite(os.path.join(output_path, f.replace('.hdf5', '.png')), rgb_img)
        cv2.imwrite(os.path.join(output_path, f.replace('.hdf5', '_color.png')), color)