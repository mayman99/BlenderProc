import h5py
import numpy as np
import os
import cv2
import csv, json
from scipy.ndimage import label
from collections import Counter
# from blenderproc.python.utility.Utility import should_not_include, object_inside_camera, should_delete

def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print(filename, " does not exist")

points = np.load("C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\blenderproc\\resources\\front_3D\\points.npy")

def write_metadata(meta_list_path:str="C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\metadata.jsonl", images_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\images', output_file:str="C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\images\\metadata.jsonl"):
    hdf5_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled'
    images_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp\\images'
    json_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp\\temp\\new_metadata.jsonl'
    hdf5s = os.listdir(hdf5_path)

    id_to_cat = {}
    cat_to_id = {}
    mapping_path = 'C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\blenderproc\\resources\\front_3D\\3D_front_mapping_merged_new_complete.csv'

    with open(mapping_path, 'r', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            cat_to_id[row["name"]] = int(row["id"])
            id_to_cat[row["id"]] = row["name"]

    metadata_list_new = []
    with open(output_file, "r") as f:
        metadata_list = list(f)

    new_texts = []
    for idx, hdf5_name in enumerate(hdf5s):
        hdf = h5py.File(os.path.join(hdf5_path, hdf5_name,'r'))
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

    # write new metadata
    with open("C:\\Users\\super\\ws\\data\\front_3d\\temp\\metadata_fixed_new.jsonl", "w") as f:
        for item in metadata_list_new:
            json.dump(item, f)
            f.writelines('\n')

def delete_files_with_short_metadata_text(meta_list_path:str="C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\metadata.jsonl", images_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\images', output_file:str="C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\images\\metadata.jsonl"):
    metadata_list = []
    with open(meta_list_path, "r") as f:
        metadata_list = list(f)

    metadata_list_new = []
    for index, json_str in enumerate(metadata_list):
        result = json.loads(json_str)
        # if text is less than 130 characters delete the file and remove record from metadata
        if len(result["text"]) < 130:
            # delete the file
            delete_file(os.path.join(images_path, str(result["file_name"])))
        else:
            metadata_list_new.append(result)
        
    with open(output_file, "w") as f:
        for item in metadata_list_new:
            json.dump(item, f)
            f.writelines('\n')

delete_files_with_short_metadata_text()