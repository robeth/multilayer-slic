'''
Created on Dec 12, 2013

@author: fruity
'''
category = "Head"
directory_path = "data/"+category+"/"
position_path = directory_path + "position/"
array_path = directory_path + "nparray/"
array_px_path = directory_path + "feature_pixel/"
truth_crf_path = directory_path + "crfarray/"
train_crf_path = directory_path + "train_crfarray/"
classifier_path = directory_path + "classifier/"
classifier_path_px = directory_path + "classifier_pixel/"
groundtruth_path = directory_path + "ground_truth/"
groundtruth_slide_path = directory_path + "truth_sliding/"
train_slide_path = directory_path + "train_sliding/"
output_path = directory_path+"output/"
output_path_px = directory_path+"output_pixel/"
result_path = directory_path +"result/"
output_morph_path = directory_path +"output-morph/"
result_filename = result_path +  "result.txt"
result_filename_px = result_path + "result-px.txt"
array_extension = ".nparray"
crf_extension = ".crfarray"
feature_filename = "all" + array_extension
classifier_extension = ".cls"
classifier_slide_filename = "classifier_slide.cls"
classifier_crf_filename = "classifier_crf.cls"
attributes = ['area', 'major_axis_length', 'minor_axis_length','extent', 'eccentricity', 'mean_intensity', 'orientation', 'perimeter', 'bbox']
raw_attributes = ['centroid', 'label']
ind_min_row=8
ind_min_col=9
ind_max_row=10
ind_max_col=11
test_sample=10
core_feature_indexes = range(8) + range(12, 20)+ range(24,32) + range(36,37)
train_start_index = 0
train_end_index = 25
test_start_index = 25
test_end_index = 50
total_feature=12
total_used_feature=8
layer = { 0: {'compactness':20, 'segment':500},
         1: {'compactness':10, 'segment':300},
         2: {'compactness':5, 'segment':30}
        }

scenarios = [{"layer": 3, 
              "settings":[{'compactness':20, 'segment':500, 'sigma':1}, 
                          {'compactness':10, 'segment':300, 'sigma':1},
                          {'compactness':5, 'segment':30, 'sigma':1}],
              "codename": "base3"
              },
             {"layer": 3, 
              "settings":[{'compactness':20, 'segment':500, 'sigma':1}, 
                          {'compactness':20, 'segment':300, 'sigma':1},
                          {'compactness':20, 'segment':100, 'sigma':1}],
              "codename": "base3-samecompact"
              },
             {"layer": 1, 
              "settings":[{'compactness':20, 'segment':500, 'sigma':1}],
              "codename": "base1"
              }]

def get_core_feature(all_features):
    return all_features[:,core_feature_indexes]