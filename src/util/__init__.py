from constant import array_px_path, total_feature, total_used_feature
from os.path import splitext
def list_to_dict(list):
        dict = {}
        for list_item in list:
            dict[list_item.label] = list_item
        return dict
    
def get_feature_array_file(scenario_name, image_filename, mode='w'):
    return open(get_feature_array_scenario_path(scenario_name) + splitext(image_filename)[0] + ".nparray" , mode)

def get_feature_array_scenario_path(scenario_name):
    return array_px_path + scenario_name + "/"

def get_feature_columns(n_layer):
    indexes = []
    current = 0
    for i in range(n_layer):
        indexes += range(current,current+total_used_feature)
        current += total_feature
    return indexes

def get_total_columns(n_layer):
    return total_feature * n_layer + 1