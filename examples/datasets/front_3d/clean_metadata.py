import os
import json

to_be_deleted = [
"81.png", 
"450.png",
"670.png",
"706.png",
"719.png",
"860.png",
"974.png",
"978.png",
"1019.png",
"1234.png",
"1261.png",
"1288.png",
"1390.png",
"1446.png",
"1611.png",
"1636.png",
"1880.png",
"2056.png",
"2245.png",
"2252.png",
"2372.png",
"2383.png",
"1073.png",
"2552.png",
"2651.png",
"2750.png",
"2754.png",
"2778.png",
"735.png",
"1263.png",
"1286.png",
"2773.png",
"1218.png",
"1524.png",
"2254.png",
"2468.png",
"1153.png",
"1826.png",
"2199.png",
"1945.png",
"1444.png",
"1497.png",
"2186.png",
"461.png",
"1633.png",
"392.png",
"2327.png",
"4.png",
"1827.png",
"2197.png",
"412.png",
"1941.png",
"148.png",
"2285.png",
"2230.png",
"1523.png",
"1310.png",
"2213.png",
"1765.png",
"1726.png",
"2256.png",
"303.png",
"1148.png",
"960.png",
"1307.png",
"2352.png"
]
images_path = 'C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\images\\'
images = os.listdir(images_path)
print(images)
metadata_list = []
new_metadata_list = []

with open("C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\images\\metadata.jsonl", "r") as f:
    metadata_list = list(f)

for idx, json_str in enumerate(metadata_list):
    result = json.loads(json_str)
    if str(result["file_name"]) in images:
        print(result["file_name"])
        new_metadata_list.append(json_str)

with open("C:\\Users\\super\\ws\\data\\front_3d\\temp_scaled\\metadata_new.jsonl", "w") as f:
    for item in new_metadata_list:
        result = json.loads(item)
        json.dump(result, f)
        f.writelines('\n')
