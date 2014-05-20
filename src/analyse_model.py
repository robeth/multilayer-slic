from constant import *
from sklearn.externals import joblib
import matplotlib.pyplot as plt
from os import listdir, makedirs
from os.path import isdir, join


scenario_names = [f for f in listdir(classifier_path_px) if isdir(join(classifier_path_px, f)) ]
all_line = ""
for scenario_name in scenario_names:
    classifier = joblib.load(classifier_path_px + scenario_name + "/" + 'RF'+"-"+category+"-"+scenario_name+ classifier_extension)
    line = scenario_name +"\t"
    for rf_feat in classifier.feature_importances_:
        line += str(rf_feat)+"\t"
    all_line += line + "\n"

print all_line
filename = "rf_feature_pixel.txt"    
result_file = open(result_path+filename, 'w')
result_file.write(all_line)
result_file.close()