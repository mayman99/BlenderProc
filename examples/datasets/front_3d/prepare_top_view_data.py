import blenderproc as bproc
from blenderproc.python.types.EntityUtility import delete_multiple
import argparse
import os
import numpy as np
import json
import bpy
from blenderproc.python.types.MeshObjectUtility import get_all_mesh_objects

def object_inside_camera(location: list, scale: int):
    if abs(location[0])<scale/2 and abs(location[1])<scale/2 and abs(location[2])<scale/2:
        return True
    return False

parser = argparse.ArgumentParser()
parser.add_argument("output_dir", nargs='?', default="/home/m/ws/data/reduced_cats/", help="Path to where the data should be saved")
parser.add_argument("data_dir", nargs='?', default="/home/m/ws/3dfront/3D-FRONT/", help="Path to where the data should be saved")
args = parser.parse_args()

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
output_number = 712

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
            future_model_path="../3dfront/3D-FRONT-models/3D-FUTURE-model-part1/3D-FUTURE-model/",
            front_3D_texture_path="../3dfront/3D-FRONT-texture/",
            label_mapping=mapping,
            models_info_path=models_info
        )

        rooms_objects_count = {}
        # {room_type_id: {'obj_name': #count, .... }, .....}
        for obj in loaded_objects:
            obj_name = obj.get_name().lower().split('.')[0]
            if obj.has_cp("room_type_id") and "others" not in obj_name and object_inside_camera(obj.get_location(), scale):
                room_id = obj.get_cp("room_type_id")
                if room_id in rooms_objects_count.keys():
                    if obj_name in rooms_objects_count[room_id].keys():
                        rooms_objects_count[room_id][obj_name] += 1
                    # Obj not found in dict
                    else:
                        rooms_objects_count[room_id][obj_name] = 1
                # Room not found in dict
                else:
                    obj_dict = {}
                    obj_dict[obj_name] = 1
                    rooms_objects_count[room_id] = obj_dict

        # Dont add if objects rendered are less than 10
        objects_rendered = 0
        for room_type_id in rooms_objects_count.keys():
            for obj_name in rooms_objects_count[room_type_id].keys():
                objects_rendered += rooms_objects_count[room_type_id][obj_name]

        if objects_rendered<10:
            delete_multiple(get_all_mesh_objects(), remove_all_offspring=True)
            continue


        rooms_with_numbers = "A flat containing "
        rooms_with_numbers_reduced = "A flat containing "
        for room_type_id in rooms_objects_count.keys():
            rooms_with_numbers += " a " + room_type_id.split("-")[0] + " " + " with "
            rooms_with_numbers_reduced += " a " + room_type_id.split("-")[0] + " " + " and "
            for obj_name in rooms_objects_count[room_type_id].keys():
                # Avoid adding all objects to the text desc of the room.
                if obj_name not in ['ceiling', 'hole', 'void', 'others', 'wall']:
                    if rooms_objects_count[room_type_id][obj_name] == 1:
                        rooms_with_numbers += "a " + obj_name + " "
                    else:
                        rooms_with_numbers += str(rooms_objects_count[room_type_id][obj_name]) + " " + obj_name + "s "
            rooms_with_numbers += ". "
            rooms_with_numbers_reduced += ". "


        meta_data_row = {}
        meta_data_row["file_name"] = str(output_number) + "_class_segmaps.png"
        meta_data_row["text"] = rooms_with_numbers

        meta_data_reduced_row = {}
        meta_data_reduced_row["file_name"] = str(output_number) + "_class_segmaps.png"
        meta_data_reduced_row["text"] = rooms_with_numbers

        bproc.renderer.set_max_amount_of_samples(1)

        # data = bproc.renderer.render_segmap(output_dir=args.output_dir, map_by=["class"])
        bproc.renderer.enable_segmentation_output(map_by=["class"], default_values={'category_id': 0})

        # render the whole pipeline
        data = bproc.renderer.render()

        already_written_scenes.append(f)
        with open(os.path.join(args.output_dir, "metadata.jsonl"), "a+") as f:
            json.dump(meta_data_row, f)
            f.writelines('\n')

        with open(os.path.join(args.output_dir, "metadata_reduced.jsonl"), "a+") as f:
            json.dump(meta_data_row, f)
            f.writelines('\n')

        with open(os.path.join(args.output_dir, "existing_scenes.json"), "w") as output_file:
            json.dump({'files': already_written_scenes}, output_file)

        # write the data to a .hdf5 container
        # Start from 0 always
        bproc.writer.write_hdf5(args.output_dir, data, True)

        delete_multiple(get_all_mesh_objects(), remove_all_offspring=True)
        output_number += 1
