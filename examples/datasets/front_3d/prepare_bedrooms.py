import blenderproc as bproc
from blenderproc.python.types.EntityUtility import delete_multiple
import argparse
import os
import bpy
from blenderproc.python.types.MeshObjectUtility import get_all_mesh_objects
import json

parser = argparse.ArgumentParser()
parser.add_argument("output_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\front_3d\\25_5_livingroom", help="Path to where the data should be saved")
parser.add_argument("data_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT", help="Path to where the data should be saved")
args = parser.parse_args()

bproc.init()
mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping_merged_new_complete.csv"))
models_info = bproc.utility.resolve_resource(os.path.join("front_3D", "model_info.json"))
mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)

matrix_world = bproc.math.build_transformation_mat([0.0, 0.0, 1.8], [0, 0, 0])
bproc.camera.add_camera_pose(matrix_world)

scale = 8
bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.camera.data.type = 'ORTHO'
bpy.context.scene.camera.data.ortho_scale = scale

files = os.listdir(args.data_dir)

already_written_scenes = []
if not os.path.exists(os.path.join(args.output_dir, "existing_scenes.json")):
    # create it
    with open(os.path.join(args.output_dir, "existing_scenes.json"), 'w') as outfile:  
        json.dump({'files': []}, outfile)
else:
    with open(os.path.join(args.output_dir, "existing_scenes.json"), "r") as f:
        _ = json.load(f)
        already_written_scenes = _['files']

def should_include(object_name:str):
    return True
    # if 'bed' in object_name.lower():
    #     return True
    # if 'stool' in object_name.lower():
    #     return True
    # if 'chair' in object_name.lower():
    #     return True
    # if 'table' in object_name.lower():
    #     return True
    # if 'mirror' in object_name.lower():
    #     return True
    # if 'cabinet' in object_name.lower():
    #     return True
    # if 'sofa' in object_name.lower():
    #     return True
    # if 'coach' in object_name.lower():
    #     return True
    # if 'unit' in object_name.lower():
    #     return True
    # if 'chest' in object_name.lower():
    #     return True
    # if 'drawer' in object_name.lower():
    #     return True
    # if 'desk' in object_name.lower():
    #     return True
    # if 'shelf' in object_name.lower():
    #     return True
    # if 'nightstand' in object_name.lower():
    #     return True
    # if 'wardrobe' in object_name.lower():
    #     return True
    # if 'bookcase' in object_name.lower():
    #     return True
    # if 'jewelry' in object_name.lower():
    #     return True
    # return False

for f in files:
    if 'json' in f:
        if f in already_written_scenes:
            continue

        already_written_scenes.append(f)
        with open(os.path.join(args.output_dir, "existing_scenes.json"), "w") as output_file:
            json.dump({'files': already_written_scenes}, output_file)

        # load the front 3D objects
        loaded_objects = bproc.loader.load_front3d(
            json_path=os.path.join(args.data_dir, str(f)),
            future_model_path="C:\\Users\\super\\ws\\data\\front_3d\\3D-FUTURE-model",
            front_3D_texture_path="C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT-texture",
            label_mapping=mapping,
            models_info_path=models_info,
            room_type="livingroom"
        )

        # Dont train on bedrooms without beds, or with too few objects
        bed_exists = False
        for obj in loaded_objects:
            if 'bed' in obj.get_name().lower():
                bed_exists = True
                break
        
        if len(loaded_objects) < 2 or bed_exists==False:
            continue

        # shift the objects to the center
        center = None
        for obj in get_all_mesh_objects():
            if 'floor' in obj.get_name().lower():
                center = sum(obj.get_bound_box()) / 8
                break

        for obj in get_all_mesh_objects():
            obj.set_location(obj.get_location() - center)

        # Look for hdf5 file with highest index
        frame_offset = 0
        for path in os.listdir(args.output_dir):
            if path.endswith(".hdf5"):
                index = path[:-len(".hdf5")]
                if index.isdigit():
                    frame_offset = max(frame_offset, int(index) + 1)

        # TODO: need to remove duplicate namings because objects are not yet merged, e.g. a [bed, bed frame, bed, bed]
        # Add each object name to text description
        # don't add an object more than thrice
        added_objects = {}
        text = 'segmentation map, orthographic view, furnished bedroom, '
        for obj in loaded_objects:
            obj_name = obj.get_name().split('.')[0].lower()
            added_objects[obj_name] = added_objects.get(obj_name, 0) + 1
            if should_include(obj_name) and added_objects.get(obj_name, 0) < 3:
                text += obj_name + ', '

        meta_data_row = {}
        meta_data_row["file_name"] = str(frame_offset) + ".png" 
        meta_data_row["text"] = text

        data = bproc.renderer.render_segmap(output_dir=args.output_dir, map_by=["class"])
        bproc.writer.write_hdf5(args.output_dir, data, True)

        with open(os.path.join(args.output_dir, "metadata.jsonl"), "a+") as f:
            json.dump(meta_data_row, f)
            f.writelines('\n')

        delete_multiple(get_all_mesh_objects(), remove_all_offspring=True)
