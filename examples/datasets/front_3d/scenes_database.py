import os
import json

files = os.listdir('C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT')
scenes_database = {}

for index, f in enumerate(files):
    if 'json' in f:
        scenes_database[str(index)] = os.path.join('C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT', f)

with open("C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT\\scenes_database.json", "w") as f:
    json.dump(scenes_database, f)
