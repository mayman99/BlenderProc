import blenderproc as bproc
from blenderproc.python.types.EntityUtility import delete_multiple
import argparse
import os
import numpy as np
import json
import bpy
from blenderproc.python.types.MeshObjectUtility import get_all_mesh_objects
from blenderproc.python.types.MeshObjectUtility import MeshObject
from typing import Set
from mathutils import Vector

def object_inside_camera(location: list, scale: int):
    if abs(location[0])<scale/2 and abs(location[1])<scale/2 and abs(location[2])<scale/2:
        return True
    return False

parser = argparse.ArgumentParser()
parser.add_argument("output_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\front_3d\\temp", help="Path to where the data should be saved")
parser.add_argument("data_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT", help="Path to where the data should be saved")
args = parser.parse_args()

bproc.init()
mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping_merged_new.csv"))
models_info = bproc.utility.resolve_resource(os.path.join("front_3D", "model_info.json"))
mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)

matrix_world = bproc.math.build_transformation_mat([0.0, 0.0, 1.5], [0, 0, 0])
bproc.camera.add_camera_pose(matrix_world)

scale = 6
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.camera.data.type = 'ORTHO'
bpy.context.scene.camera.data.ortho_scale = scale

files = os.listdir(args.data_dir)
output_number = 381

already_written_scenes = []
if not os.path.exists(os.path.join(args.output_dir, "existing_scenes.json")):
    # create it
    with open(os.path.join(args.output_dir, "existing_scenes.json"), 'w') as outfile:  
        json.dump({'files': []}, outfile)
else:
    with open(os.path.join(args.output_dir, "existing_scenes.json"), "r") as f:
        _ = json.load(f)
        already_written_scenes = _['files']

for f in files:
    if 'json' in f:
        if f in already_written_scenes:
            continue

        # load the front 3D objects
        loaded_objects = bproc.loader.load_front3d(
            json_path=os.path.join(args.data_dir, str(f)),
            future_model_path="C:\\Users\\super\\ws\\data\\front_3d\\3D-FUTURE-model",
            front_3D_texture_path="C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT-texture",
            label_mapping=mapping,
            models_info_path=models_info,
            room_type="bedroom"
        )

        if len(loaded_objects) < 2:
            continue

        center = None
        for obj in get_all_mesh_objects():
            if 'floor' in obj.get_name().lower():
                center = sum(obj.get_bound_box()) / 8
                break

        for obj in get_all_mesh_objects():
            obj.set_location(obj.get_location() - center)

        output_number += 1
    break
