import blenderproc as bproc
import argparse
from blenderproc.python.types.EntityUtility import delete_multiple
import json
import os
from blenderproc.python.types.MeshObjectUtility import get_all_mesh_objects
from mathutils import Matrix, Vector

parser = argparse.ArgumentParser()
parser.add_argument('objs', nargs='?', default="./../data/output/1_1.png.json" , help="Path to the camera file, should be examples/resources/camera_positions")
parser.add_argument('models_dir', nargs='?', default="./../data/3dmodels/" , help="Path to the camera file, should be examples/resources/camera_positions")
args = parser.parse_args()

bproc.init()

delete_multiple(get_all_mesh_objects(), remove_all_offspring=True)

def loc_pixels_to_meteers(loc: list):
    # 512x512 canvas is a 12x12 meters scene
    x = loc[0]/12
    y = loc[1]/12
    z = 0.1
    return [x, y, z]

def render_walls(walls_binary_mask):
    """
    First: edit the data and retrain the model on only one category of walls
    """
    for x in range(512):
        for y in range(512):
            if walls_binary_mask[x][y] == 1:
                # render a box of size 12/512 @ location 12*x/512,12*y/512
                bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(x/512, y/512, 0.05 ), scale=(12/512, 12/512, 12/512))

with open(args.objs) as user_file:
    objects = json.load(user_file)
    for obj_cat in objects.keys():
        for obj_instance in objects[obj_cat]:
            # load the objects into the scene
            obj = bproc.loader.load_obj(os.path.join(args.models_dir, obj_cat, "normalized_model.obj"))
            obj[0].set_location(loc_pixels_to_meteers(obj_instance))
            if 'chair' in obj_cat:
                 obj[0].set_scale(Vector([0.001, 0.001, 0.001]))


# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
light.set_location([5, -5, 5])
light.set_energy(1000)

# define the camera resolution
# bproc.camera.set_resolution(512, 512)

# # read the camera positions file and convert into homogeneous camera-world transformation
# with open(args.camera, "r") as f:
#     for line in f.readlines():
#         line = [float(x) for x in line.split()]
#         position, euler_rotation = line[:3], line[3:6]
#         matrix_world = bproc.math.build_transformation_mat(position, euler_rotation)
#         bproc.camera.add_camera_pose(matrix_world)

# # activate normal and depth rendering
# bproc.renderer.enable_normals_output()
# bproc.renderer.enable_depth_output(activate_antialiasing=False)

# # render the whole pipeline
# data = bproc.renderer.render()

# # write the data to a .hdf5 container
# bproc.writer.write_hdf5(args.output_dir, data)
