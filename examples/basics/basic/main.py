import blenderproc as bproc
import argparse
from blenderproc.python.types.EntityUtility import delete_multiple
import json
import os
from blenderproc.python.types.MeshObjectUtility import get_all_mesh_objects
from mathutils import Matrix, Vector

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


def add_wall_segments(walls_binary_mask):
    """
    """
    for x in range(512):
        for y in range(512):
            if walls_binary_mask[x][y] == 1:
                # render a box of size 12/512 @ location 12*x/512,12*y/512
                bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(x/512, y/512, 0.05 ), scale=(12/512, 12/512, 12/512))


parser = argparse.ArgumentParser()
parser.add_argument('objs', nargs='?', default="./../data/output/1_1.png.json" , help="Path to the camera file, should be examples/resources/camera_positions")
parser.add_argument('models_dir', nargs='?', default="./../data/3dmodels/" , help="Path to the camera file, should be examples/resources/camera_positions")
args = parser.parse_args()

bproc.init()

delete_multiple(get_all_mesh_objects(), remove_all_offspring=True)

with open(args.objs) as user_file:
    objects = json.load(user_file)
    for obj_cat in objects.keys():
        for obj_instance in objects[obj_cat]:
            # load the objects into the scene
            obj = bproc.loader.load_obj(os.path.join(args.models_dir, obj_cat, "normalized_model.obj"))
            obj[0].set_location(loc_pixels_to_meteers(obj_instance))

# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([0, 0, 4])
light.set_energy(1000)

