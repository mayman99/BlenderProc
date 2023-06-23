import os
import json

files = os.listdir('C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT')
room_type_size = {}

for f in files:
    if 'json' in f:
        file = json.load(open(os.path.join('C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT', f), 'r'))
        scene = file['scene']
        for room in scene['room']:
            if room['type'] not in room_type_size:
                room_type_size[room['type']] = []
            if ('size' in room.keys()):
                room_type_size[room['type']].append(room['size'])

for key in room_type_size.keys():
    if len(room_type_size[key])>0:
        room_type_size[key] = sum(room_type_size[key]) / len(room_type_size[key])

print(room_type_size)