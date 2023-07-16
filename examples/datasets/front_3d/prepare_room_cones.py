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
parser.add_argument("output_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\pointy_cone", help="Path to where the data should be saved")
parser.add_argument("data_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT", help="Path to where the data should be saved")
parser.add_argument("scale_room", nargs='?', default=True, help="Path to where the data should be saved")
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

selected_room_type = 'Bedroom'
if selected_room_type == 'all':
    scale = 12
else:
    scale = math.sqrt(room_types_avg_sizes[selected_room_type]) + 2

bproc.init()
mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping_merged_new_complete.csv"))
models_info = bproc.utility.resolve_resource(os.path.join("front_3D", "model_info.json"))
mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)

matrix_world = bproc.math.build_transformation_mat([0.0, 0.0, 1.8], [0, 0, 0])
bproc.camera.add_camera_pose(matrix_world)

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

# load pointy cone object
pointy_cone = load_obj(filepath="C:\\Users\\super\\ws\\data\\pointy_cone\\cube_cone.obj")[0]

def write_objects_csv(objects, scale, image_size, csv_file_path, image_index, normalize:bool=True):
    """
    write the objects orintations data to the csv file
    in the format:
    file_name, y_rotation
    """
    with open(csv_file_path, 'a+') as f:
        objects_count = len(objects)
        f.write("{},{},".format(image_index, objects_count))
        for idx, obj in enumerate(objects):
            rot = int(obj.get_rotation_euler()[2] * 180/math.pi)
            category_id = obj.get_cp("category_id")
            if normalize:
                xmin, ymin, xmax, ymax = get_bb(obj.get_bound_box(), 1.0, scale)
            else:
                xmin, ymin, xmax, ymax = get_bb(obj.get_bound_box(), image_size, scale)
            obj_data = "{},{},{},{},{},{}".format(category_id, xmin, ymin, xmax, ymax, rot)
            if idx != objects_count-1:
                obj_data += ","
            f.write(obj_data)
        f.write("\n")

def get_bb(bb, image_size, scale):
    """
    get bounding box in pixel corrdinates from cartesian coordinates
    """
    def cartesian_to_pixel(x, y):
        # shift to the fourth quardrent and invert the Y-axis
        x += scale/2
        y -= scale/2
        y = abs(y)

        x = x * (image_size/scale)
        y = y * (image_size/scale)
        return x, y

    # The bounding box has 8 points, choose the 4 points where the y is not negative
    # get the 4 points where y is not negative
    points = []
    for j in range(len(bb)):
        point = bb[j]
        if point[2] >= 0:
            points.append((point[0], point[1]))

    # print("bound box: ", bb)
    # print("points: ", points)

    # convert to pixel coordinates
    points = [cartesian_to_pixel(x, y) for x, y in points]

    # get the top left and bottom right points
    x_min, y_min = min(points, key=lambda x: x[0])[0], min(points, key=lambda x: x[1])[1]
    x_max, y_max = max(points, key=lambda x: x[0])[0], max(points, key=lambda x: x[1])[1]

    return x_min, y_min, x_max, y_max

def main():
    for f in files:
        if 'json' in f:
            if f in already_written_scenes:
                continue
            
            cones = []
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
                room_type=selected_room_type.lower()
            )
            # calculate the median of all the floor objects
            # and shift the objects to the center
            center = [0, 0, 0]
            floors_count = 0
            scale = 12
            for obj in loaded_objects:
                if obj.get_name().split('.')[0].lower() == 'floor':
                    floors_count += 1
                    bb = obj.get_bound_box()
                    center += sum(bb) / 8
                    # find the length of the longest side of the bounding box
                    if args.scale_room:
                        max_side = max([np.linalg.norm(bb[0] - bb[1]), np.linalg.norm(bb[0] - bb[2]), np.linalg.norm(bb[0] - bb[4])])
                        scale = max_side + 0.5
                        bpy.context.scene.camera.data.ortho_scale = scale
            center = center / floors_count

            # shfit objects to the center
            # replace each loaded mesh object with a pointy cone with the same location and rotation and category
            objects_names_count = {}
            text = 'segmentation map, orthographic view, with camera scale of ' + str(round(scale, 0)) + ' furnished apartment, ' + selected_room_type + ', '
            objects_count = 0
            for obj in loaded_objects:
                obj_name = obj.get_name().split('.')[0].lower()
                if should_delete(obj_name):
                    obj.delete()
                    continue
                obj.set_location(obj.get_location() - center)
                loc_ = obj.get_location()


                if not should_not_include(obj_name) and abs(loc_[0])<scale and abs(loc_[1])<scale and objects_names_count.get(obj_name, 0) < 1:
                    # delete objects that are the center
                    objects_count += 1
                    if objects_names_count.get(obj_name, 0) < 1:
                        if obj.has_cp("from_file"):
                            objects_names_count[obj_name] = 1
                        text += obj_name + ', '
                    room_id_ = None
                    if obj.has_cp("room_id"):
                        room_id_ = obj.get_cp("room_id")
                    rot_ = obj.get_rotation_euler()
                    cat_id_ = obj.get_cp("category_id")
                    obj.delete()
                    pointy_cone_ = pointy_cone.duplicate()
                    cones.append(pointy_cone_)
                    pointy_cone_.set_cp("coarse_grained_class", cat_id_)
                    pointy_cone_.set_cp("category_id", cat_id_)
                    pointy_cone_.set_cp("room_id", room_id_)
                    pointy_cone_.set_location(loc_)
                    pointy_cone_.set_rotation_euler(rot_)
                    pointy_cone_.set_scale([0.15, 0.15, 0.15])

            # dont save images with less than 2 objects or more than 10 objects
            if objects_count < 2 or objects_count > 10:
                return

            # delete the original pointy cone object
            pointy_cone.delete()

            for obj in get_all_mesh_objects():
                if obj.get_location()[0] == 0 and obj.get_location()[1] == 0:
                    obj.delete()
                    continue
            
            # Look for hdf5 file with highest index
            frame_offset = 0
            for path in os.listdir(args.output_dir):
                if path.endswith(".hdf5"):
                    index = path[:-len(".hdf5")]
                    if index.isdigit():
                        frame_offset = max(frame_offset, int(index) + 1)

            meta_data_row = {}
            meta_data_row["file_name"] = str(frame_offset) + ".png" 
            meta_data_row["text"] = text
            for obj in get_all_mesh_objects():
                obj_name = obj.get_name()
                if 'shadow' in obj_name or 'glass' in obj_name:
                    obj.delete()

            data = bproc.renderer.render_segmap(output_dir=args.output_dir, map_by=["class"])
            bproc.writer.write_hdf5(args.output_dir, data, True)

            write_objects_csv(cones, scale, 512, os.path.join(args.output_dir, "PointyConesDataset.txt"), frame_offset, normalize=False)

            with open(os.path.join(args.output_dir, "metadata.jsonl"), "a+") as f:
                json.dump(meta_data_row, f)
                f.writelines('\n')

            break

if __name__ == '__main__':
    main()
