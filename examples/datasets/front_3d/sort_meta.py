import os
import json

max_hdf5 = 2853
metadata_list = []
metadata_fixed = []
with open("C:\\Users\\super\\ws\\data\\front_3d\\temp\\metadata.jsonl", "r") as f:
    metadata_list = list(f)

new_index = 0
for json_str in metadata_list:
    result = json.loads(json_str)
    result["file_name"] = str(new_index) + ".png"
    new_index += 1
    metadata_fixed.append(result)

with open("C:\\Users\\super\\ws\\data\\front_3d\\temp\\metadata_fixed.jsonl", "w") as f:
    for item in metadata_fixed:
        json.dump(item, f)
        f.writelines('\n')
