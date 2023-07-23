import os
import json
import subprocess

# Define the number of iterations you want
scenes_database = json.load(open("C:\\Users\\super\\ws\\data\\front_3d\\3D-FRONT\\3D-FRONT\\scenes_database.json", "r"))

for i in scenes_database.keys():
    # Start the subprocess and pass the index as an argument
    subprocess.run(["python", "C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\cli.py", "run", "C:\\Users\\super\\ws\\sd_lora_segmap_topdown\\blenderproc_fork\\examples\\datasets\\front_3d\\prepare_room_cones_args.py", scenes_database[str(i)] , i, "C:\\Users\\super\\ws\\data\\front_3d\\temp"])
