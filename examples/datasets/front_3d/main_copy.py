import blenderproc as bproc
import argparse
import os
import numpy as np
import bpy

# parser = argparse.ArgumentParser()
# parser.add_argument("front", help="Path to the 3D front file")
# parser.add_argument("future_folder", help="Path to the 3D Future Model folder.")
# parser.add_argument("front_3D_texture_path", help="Path to the 3D FRONT texture folder.")
# parser.add_argument("output_dir", help="Path to where the data should be saved")
# args = parser.parse_args()

# if not os.path.exists(args.front) or not os.path.exists(args.future_folder):
#     raise Exception("One of the two folders does not exist!")

bproc.init()
mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping_merged_new.csv"))
mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)

models_info = bproc.utility.resolve_resource(os.path.join("front_3D", "model_info.json"))

matrix_world = bproc.math.build_transformation_mat([0.0, 0.0, 1.5], [0, 0, 0])
bproc.camera.add_camera_pose(matrix_world)

bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.camera.data.type = 'ORTHO'
bpy.context.scene.camera.data.ortho_scale = 14

# set the light bounces
bproc.renderer.set_light_bounces(diffuse_bounces=200, glossy_bounces=200, max_bounces=200,
                                  transmission_bounces=200, transparent_max_bounces=200)

# load the front 3D objects
loaded_objects = bproc.loader.load_front3d(
    json_path="/home/m/ws/3dfront/3D-FRONT/5ca4c392-dcc6-4dc1-a607-44b66785ac6d.json",
    future_model_path="../3dfront/3D-FRONT-models/3D-FUTURE-model-part1/3D-FUTURE-model/",
    front_3D_texture_path="../3dfront/3D-FRONT-texture/",
    label_mapping=mapping,
    models_info=models_info
)

# bproc.renderer.enable_segmentation_output(map_by=["category_id"])
bproc.renderer.set_max_amount_of_samples(16)

# render the whole pipeline
# bproc.renderer.set_output_format(file_format="JPEG", jpg_quality=90)
data = bproc.renderer.render_segmap(output_dir="/home/m/ws/data/fork/", map_by=["class"])
print(np.unique(np.array(data["class_segmaps"])))

# data = bproc.renderer.render()

# write the data to a .hdf5 container
bproc.writer.write_hdf5("/home/m/ws/data/fork/", data, True)

# # Init sampler for sampling locations inside the loaded front3D house
# point_sampler = bproc.sampler.Front3DPointInRoomSampler(loaded_objects)

# # Init bvh tree containing all mesh objects
# bvh_tree = bproc.object.create_bvh_tree_multi_objects([o for o in loaded_objects if isinstance(o, bproc.types.MeshObject)])

# poses = 0
# tries = 0


# def check_name(name):
#     for category_name in ["chair", "sofa", "table", "bed"]:
#         if category_name in name.lower():
#             return True
#     return False


# # filter some objects from the loaded objects, which are later used in calculating an interesting score
# special_objects = [obj.get_cp("category_id") for obj in loaded_objects if check_name(obj.get_name())]

# proximity_checks = {"min": 1.0, "avg": {"min": 2.5, "max": 3.5}, "no_background": True}
# while tries < 10000 and poses < 10:
#     # Sample point inside house
#     height = np.random.uniform(1.4, 1.8)
#     location = point_sampler.sample(height)
#     # Sample rotation (fix around X and Y axis)
#     rotation = np.random.uniform([1.2217, 0, 0], [1.338, 0, np.pi * 2])
#     cam2world_matrix = bproc.math.build_transformation_mat(location, rotation)

#     # Check that obstacles are at least 1 meter away from the camera and have an average distance between 2.5 and 3.5
#     # meters and make sure that no background is visible, finally make sure the view is interesting enough
#     if bproc.camera.scene_coverage_score(cam2world_matrix, special_objects, special_objects_weight=10.0) > 0.8 \
#             and bproc.camera.perform_obstacle_in_view_check(cam2world_matrix, proximity_checks, bvh_tree):
#         bproc.camera.add_camera_pose(cam2world_matrix)
#         poses += 1
#     tries += 1

# # Also render normals
# bproc.renderer.enable_normals_output()
# bproc.renderer.enable_segmentation_output(map_by=["category_id"])

# # render the whole pipeline
# data = bproc.renderer.render()

# # write the data to a .hdf5 container
# bproc.writer.write_hdf5(args.output_dir, data)
