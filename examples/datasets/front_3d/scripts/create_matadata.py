import os
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("data_dir", nargs='?', default="C:\\Users\\super\\ws\\data\\front_3d\\no_text_data_all_bedrooms", help="Path to where the data should be saved")
args = parser.parse_args()

output_path = 'C:\\Users\\super\\ws\\data\\front_3d\\no_text_data_all_bedrooms_correction\\images'
files = os.listdir(args.data_dir)
latest_file_number = 2622

for f in range(latest_file_number):
    meta_data_row = {}
    meta_data_row["file_name"] = str(f) + ".png"
    meta_data_row["text"] = "a sagmentaion map of an orthographic view of a furnished bedroom."    
    with open(os.path.join(output_path, "metadata.jsonl"), "a+") as f:
        json.dump(meta_data_row, f)
        f.writelines('\n')
