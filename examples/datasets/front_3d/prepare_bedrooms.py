import blenderproc as bproc
from blenderproc.python.types.EntityUtility import delete_multiple
import argparse
import os
import numpy as np
import json
import bpy
from blenderproc.python.types.MeshObjectUtility import get_all_mesh_objects
import MeshObject from blenderproc.python.types.MeshObject
from blenderproc.python.types.MatrixUtility import Matrix   
from typing import Set

def object_inside_camera(location: list, scale: int):
    if abs(location[0])<scale/2 and abs(location[1])<scale/2 and abs(location[2])<scale/2:
        return True
    return False

parser = argparse.ArgumentParser()
parser.add_argument("output_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\front_3d\\temp", help="Path to where the data should be saved")
parser.add_argument("data_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT", help="Path to where the data should be saved")
args = parser.parse_args()

def visible_objects(object_in_room: MeshObject, sqrt_number_of_rays: int = 10) -> Set[MeshObject]:
    """ Returns a set of objects visible from the given camera pose.

    Sends a grid of rays through the camera frame and returns all objects hit by at least one ray.

    :param cam2world_matrix: The world matrix which describes the camera orientation to check.
    :param sqrt_number_of_rays: The square root of the number of rays which will be used to determine the
                                visible objects.
    :return: A set of objects visible hit by the sent rays.
    """
    cam2world_matrix = Matrix(cam2world_matrix)

    visible_objects_set = set()
    cam_ob = bpy.context.scene.camera
    cam = cam_ob.data

    # Get position of the corners of the near plane
    frame = cam.view_frame(scene=bpy.context.scene)
    # Bring to world space
    frame = [cam2world_matrix @ v for v in frame]

    # Compute vectors along both sides of the plane
    vec_x = frame[1] - frame[0]
    vec_y = frame[3] - frame[0]

    # Go in discrete grid-like steps over plane
    position = cam2world_matrix.to_translation()
    for x in range(0, sqrt_number_of_rays):
        for y in range(0, sqrt_number_of_rays):
            # Compute current point on plane
            end = frame[0] + vec_x * x / float(sqrt_number_of_rays - 1) + vec_y * y / float(sqrt_number_of_rays - 1)
            # Send ray from the camera position through the current point on the plane
            _, _, _, _, hit_object, _ = bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),
                                                                   position, end - position)
            # Add hit object to set
            if hit_object:
                visible_objects_set.add(MeshObject(hit_object))

    return visible_objects_set


bproc.init()
mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping_merged_new.csv"))
models_info = bproc.utility.resolve_resource(os.path.join("front_3D", "model_info.json"))
mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)

matrix_world = bproc.math.build_transformation_mat([0.0, 0.0, 1.5], [0, 0, 0])
bproc.camera.add_camera_pose(matrix_world)

scale = 12
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
            models_info_path=models_info
        )

        rooms_objects_count = {}
        for obj in loaded_objects:
            obj_name = obj.get_name().lower().split('.')[0]
            if obj.has_cp("room_type_id") and "others" not in obj_name and object_inside_camera(obj.get_location(), scale):
                room_id = obj.get_cp("room_type_id")






        output_number += 1
    break
