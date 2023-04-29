import argparse
import os
import json

parser = argparse.ArgumentParser()
parser.add_argument("output_dir", nargs='?', default="/home/m/ws/data/", help="Path to where the data should be saved")
parser.add_argument("data_dir", nargs='?', default="/home/m/ws/3dfront/3D-FRONT/", help="Path to where the data should be saved")
args = parser.parse_args()

files = os.listdir(args.data_dir)

with open(os.path.join(args.output_dir, "scenes.json"), "w") as f:
    json.dump(files, f)
