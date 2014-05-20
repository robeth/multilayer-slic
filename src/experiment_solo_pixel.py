'''
Created on Apr 15, 2014

@author: fruity
'''
from f_create_model_pixel import create_model
from f_extract_feature_pixel import extract_feature
from constant import result_path

filename = "solo_pixel.txt"
cluster_list = range(100, 1001, 100)
compactness_list = range(1, 20,2)
results = []

for clus in cluster_list:
    for comp in compactness_list:
        s = {"layer": 1,
                "settings": [{'compactness':comp, 'segment':clus, 'sigma':1}],
                "codename" : "solo-c%s-s%s"%(comp,clus) }
        extract_feature(s)
        results.append(create_model(s))

all_line = ""
for r in results:
    line = "%s\t%s\t%s\t%s\t%s\t%s\n"%(r['codename'], r['acc'], r['fn'], r['fp'], r['tn'], r['tp'])
    all_line += line
result_file = open(result_path+filename, 'w')
result_file.write(all_line)
result_file.close()