'''
Created on Apr 15, 2014

@author: fruity
'''
from core.f_create_model_pixel import create_model
from core.f_extract_feature_pixel import extract_feature
from constant import result_path, category

filename = "double_pixel-goodgood.txt"
cluster_list = range(100, 1001, 100)
compactness_list = range(1, 20,2)

cases ={"Femur":{ "hit-spec":{
                              "1st":[[13,19,13,9,19],[900, 500, 600, 1000, 900]],
                              "2nd":[[1,1,1,3,19],[100, 900, 500, 700, 1000]]
                              },
                 "hit-acc":{
                              "1st":[[13,19,13,9,19],[900, 500, 600, 1000, 900]],
                              "2nd":[[1,1,19,9,13],[300, 800, 1000, 1000, 900]]
                              },
                 }, 
        "Head": { "hit-acc_or_spec":{
                              "1st":[[1,1,1,3,3],[100, 500, 1000, 200, 800]],
                              "2nd":[[19,15,7,19,11],[500, 1000, 1000, 700, 900]]
                              },
                 }}
results = []
current_case = cases[category]

for agenda_name, agenda_content in current_case.items():
    first_layer = agenda_content["1st"]
    second_layer = agenda_content["2nd"]
    trial = len(first_layer[0])
    
    for first_index in range(trial):
        for second_index in range(trial):
            s = {"layer": 2,
                    "settings": [{'compactness':first_layer[0][first_index], 'segment':first_layer[1][first_index], 'sigma':1},
                                 {'compactness':second_layer[0][second_index], 'segment':second_layer[1][second_index], 'sigma':1}],
                    "codename" : "%s-c%s-s%s_w_c%s-s%s"%(agenda_name,first_layer[0][first_index],first_layer[1][first_index], second_layer[0][second_index], second_layer[1][second_index]) }
            print "%s-%s --> %s"%(first_index, second_index, s['codename'])
            extract_feature(s)
            results.append(create_model(s))
  
all_line = ""
for r in results:
    line = "%s\t%s\t%s\t%s\t%s\t%s\n"%(r['codename'], r['acc'], r['fn'], r['fp'], r['tn'], r['tp'])
    all_line += line
result_file = open(result_path+filename, 'w')
result_file.write(all_line)
result_file.close()