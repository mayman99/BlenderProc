import blenderproc as bproc
from blenderproc.python.types.EntityUtility import delete_multiple
import argparse
import os
import bpy
from blenderproc.python.types.MeshObjectUtility import get_all_mesh_objects
from blenderproc.python.camera.CameraValidation import visible_objects
import json
import math
from utils import should_not_include, object_inside_camera

parser = argparse.ArgumentParser()
parser.add_argument("scene_path", nargs='?')
parser.add_argument("frame_offset", nargs='?')
parser.add_argument("output_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\front_3d\\temp", help="Path to where the data should be saved")
args = parser.parse_args()

room_types_avg_sizes = {'Library': 11.058077211854293, 'MasterBedroom': 15.945724690235737, \
                        'Kitchen': 7.013370185203281, 'SecondBedroom': 11.987564798341676,\
                        'Balcony': 5.033716810973039, 'Bathroom': 4.4497765280226815, \
                        'LivingDiningRoom': 34.204618838796314, 'OtherRoom': 4.120163896665871,\
                        'LivingRoom': 28.83047019311502, 'MasterBathroom': 4.724099616858237,\
                        'Bedroom': 15.266718454658184, 'DiningRoom': 19.202701324568537,\
                        'Hallway': 5.357986688851916, 'SecondBathroom': 3.894988235294119,\
                        'Aisle': 4.523870292887024, 'Corridor': 7.595404814004379,\
                        'Terrace': 9.271739130434781, 'LaundryRoom': 4.486932852011839,\
                        'KidsRoom': 11.871834040251438, 'CloakRoom': 5.143795484432288,\
                        'StorageRoom': 3.258676470588234, 'ElderlyRoom': 12.446796536796539,\
                        'EquipmentRoom': 0.9801515151515157, 'Lounge': 14.915833333333333,\
                        'Stairwell': 13.31433734939759, 'NannyRoom': 6.691999999999999,\
                        'BedRoom': 14.276741053759888, 'OtherSpace': 3.046666666666667,\
                        'BathRoom': 3.4706666666666672, 'Courtyard': 32.45112462807143, 'Auditorium': 43.57375,\
                        'non': [], 'Garage': 22.076666666666668}

frame_offset = args.frame_offset
selected_room_type = 'Bedroom'
if selected_room_type == 'all':
    scale = 12
else:
    scale = math.sqrt(room_types_avg_sizes[selected_room_type]) + 2

bproc.init()
mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping_merged_new_complete.csv"))
models_info = bproc.utility.resolve_resource(os.path.join("front_3D", "model_info.json"))
mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)

bpy.context.scene.render.resolution_x = 512
bpy.context.scene.render.resolution_y = 512
bpy.context.scene.camera.data.type = 'ORTHO'
bpy.context.scene.camera.data.ortho_scale = scale

def main():
    print(args)
    # load the front 3D objects
    loaded_objects = bproc.loader.load_front3d(
        json_path=args.scene_path,
        future_model_path="C:\\Users\\super\\ws\\data\\front_3d\\3D-FUTURE-model",
        front_3D_texture_path="C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT-texture",
        label_mapping=mapping,
        models_info_path=models_info,
        room_type=selected_room_type.lower()
    )

    # calculate the median of all the floor objects
    # and shift the objects to the center
    center = [0, 0, 1.8]
    floors_count = 0
    for obj in loaded_objects:
        if 'floor' in obj.get_name().lower():
            floors_count += 1
            center += sum(obj.get_bound_box()) / 8
    if floors_count<1:
        return
    center = center / floors_count

    matrix_world = bproc.math.build_transformation_mat(center, [0, 0, 0])
    bproc.camera.add_camera_pose(matrix_world)

    # Build training text data for blip-2 model
    # The data contains each objcet name in the scene, location and rotation
    # The data is saved in a json file
    training_data = {}
    training_data[str(frame_offset)] = []
    # Add each object name to text description
    objects_count = {}
    text = 'segmentation map, orthographic view, furnished apartment, ' + selected_room_type + ', '
    for obj in loaded_objects:
        if object_inside_camera(obj.get_location(), scale):
            obj_name = obj.get_name().split('.')[0].lower()
            if not should_not_include(obj_name) and objects_count.get(obj_name, 0) < 1:
                if obj.has_cp("from_file"):
                    objects_count[obj_name] = 1
                text += obj_name + ', '
                training_data[str(frame_offset)].append({
                    'name': obj.get_name(),
                    'location': obj.get_location().tolist(),
                    'rotation': obj.get_rotation_euler()[2]
                })
    
    # Dont add the scene if there are less than 3 real objects
    if len(training_data[str(frame_offset)]) < 2:
        return

    meta_data_row = {}
    meta_data_row["file_name"] = str(frame_offset) + ".png" 
    meta_data_row["text"] = text

    data = bproc.renderer.render_segmap(output_dir=args.output_dir, map_by=["class"])
    bproc.writer.write_hdf5(args.output_dir, data, True)

    with open(os.path.join(args.output_dir, "metadata.jsonl"), "a+") as f:
        json.dump(meta_data_row, f)
        f.writelines('\n')

    # append the training data to a json file
    with open(os.path.join(args.output_dir, "training_data.json"), 'a+') as outfile: 
        json.dump(training_data, outfile)
        outfile.writelines('\n')

    delete_multiple(get_all_mesh_objects(), remove_all_offspring=True)
    bpy.ops.outliner.orphans_purge()

if __name__ == '__main__':
    main()