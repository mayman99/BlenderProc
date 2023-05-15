import blenderproc as bproc
import argparse
from blenderproc.python.types.EntityUtility import delete_multiple
import json
import os
from blenderproc.python.types.MeshObjectUtility import get_all_mesh_objects
from mathutils import Matrix, Vector
import numpy as np
import bpy

def loc_pixels_to_meteers(loc: list):
    # 512x512 canvas is a 12x12 meters scene
    x = loc[0]/12
    y = loc[1]/12
    z = 0.1
    return [x, y, z]

def add_floor(floor_path: str):
    """
    """
    # load the objects into the scene
    objs = bproc.loader.load_obj(floor_path)


def add_wall_segments(walls_binary_mask_path):
    """
    """
    walls_binary_mask = np.load(walls_binary_mask_path)
    for x in range(512):
        if x%5==0:
            for y in range(512):
                if y%5==0:
                    if walls_binary_mask[x][y] == 1:
                        # render a box of size 12/512 @ location 12*x/512,12*y/512
                        bpy.ops.mesh.primitive_cube_add(size=10, enter_editmode=False, align='WORLD', location=(x/12, y/12, 0.05), scale=(12*2/512, 12*2/512, 1))

parser = argparse.ArgumentParser()
parser.add_argument('objs', nargs='?', default="C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\data\\output" , help="Path to the camera file, should be examples/resources/camera_positions")
parser.add_argument('models_dir', nargs='?', default="./../data/3dmodels/" , help="Path to the camera file, should be examples/resources/camera_positions")
args = parser.parse_args()

bproc.init()

delete_multiple(get_all_mesh_objects(), remove_all_offspring=True)

add_wall_segments((os.path.join(args.objs, '1_2.npy')))

with open(os.path.join(args.objs, '1_2.json')) as user_file:
    objects = json.load(user_file)
    for obj_cat_path in objects.keys():
        for obj_loc in objects[obj_cat_path]:
            # load the objects into the scene
            obj = bproc.loader.load_obj(obj_cat_path)
            obj[0].set_location(loc_pixels_to_meteers(obj_loc))


# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([0, 0, 4])
light.set_energy(1000)

