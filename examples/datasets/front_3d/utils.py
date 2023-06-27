

def should_not_include(obj_name):
    if 'cornice' in obj_name or 'wall' in obj_name or 'floor' in obj_name or 'ceiling' in obj_name or 'door' in obj_name or 'window' in obj_name or 'pocket' in obj_name or 'front' in obj_name or 'back' in obj_name or 'baseboard' in obj_name or 'hole' in obj_name or 'slab' in obj_name or 'lamp' in obj_name:
        return True
    return False

def object_inside_camera(location: list, scale: int):
    if abs(location[0])<scale/2 and abs(location[1])<scale/2:
        return True
    return False
