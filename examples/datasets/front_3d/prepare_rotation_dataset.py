import blenderproc as bproc
from blenderproc.python.types.EntityUtility import delete_multiple
import argparse
import os
import bpy
from blenderproc.python.types.MeshObjectUtility import get_all_mesh_objects
from blenderproc.python.loader.ObjectLoader import load_obj
from blenderproc.python.utility.Utility import should_not_include, object_inside_camera, should_delete
import numpy as np
import json
import math

parser = argparse.ArgumentParser()
parser.add_argument("output_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\rotation_data", help="Path to where the data should be saved")
args = parser.parse_args()

scale = 1

bproc.init()
matrix_world = bproc.math.build_transformation_mat([0.0, 0.0, 1.8], [0, 0, 0])
bproc.camera.add_camera_pose(matrix_world)
bpy.context.scene.render.resolution_x = 128
bpy.context.scene.render.resolution_y = 128
bpy.context.scene.camera.data.type = 'ORTHO'
bpy.context.scene.camera.data.ortho_scale = scale

# load pointy cone object
pointy_cone = load_obj(filepath="C:\\Users\\super\\ws\\data\\pointy_cone\\cube_cone.obj")[0]
pointy_cone.set_scale([0.15, 0.15, 0.15])
pointy_cone.set_cp("category_id", 1)

def write_objects_orintations_data(objects, file_path):
    """
    write the objects orintations data to the csv file
    in the format:
    file_name, y_rotation
    """
    with open(file_path, 'w') as f:
        for obj in objects:
            f.write("{},{}\n".format(obj.name, obj.get_rotation_euler[2]))

def main():
    for i in range(0, 360, 10):
        z_euler = i*math.pi/180
        pointy_cone.set_rotation_euler([pointy_cone.get_rotation_euler()[0], pointy_cone.get_rotation_euler()[1], z_euler]) 
        data = bproc.renderer.render_segmap(output_dir=args.output_dir, map_by=["class"])
        bproc.writer.write_hdf5(args.output_dir, data, True)
        with open(os.path.join(args.output_dir, 'rotation_dataset.csv'), 'a+') as f:
            f.write("{},{}\n".format(int(i/10), i))

if __name__ == '__main__':
    main()
