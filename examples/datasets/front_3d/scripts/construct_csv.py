import os
import csv
import json
import numpy as np
import csv

# read model_info
with open("/home/m/ws/3dfront/3D-FRONT-models/3D-FUTURE-model-part1/3D-FUTURE-model/model_info.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

categories_dict = {}
id = 99
for idx, model in enumerate(data):
    if model["category"] != None:
        cat = model["category"].lower().strip()
        if cat not in categories_dict.keys():
            categories_dict[cat] = str(id)
            id += 1

header = ['id', 'name']
print(categories_dict)

with open('/home/m/ws/BlenderProc/blenderproc/resources/front_3D/3D_front_mapping_merged_new.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    for key in categories_dict.keys():
        # write the data
        writer.writerow([categories_dict[key], key])
