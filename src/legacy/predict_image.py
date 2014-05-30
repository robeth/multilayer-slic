'''
Input: classifier model in category/classifier/[scneario-name]/RF-[category]-[scenario-name].cls
    
Ouput: images output in category/output/[scenario-name]/[image-name].jpg 
    
Random forest applied on all scenarios
@author: fruity
'''
from skimage import data
from skimage.color.colorconv import rgb2gray
from skimage.segmentation import slic, mark_boundaries
from os import listdir, makedirs
from os.path import isfile, join, splitext, exists
from skimage.measure import regionprops
from skimage.morphology import label
import matplotlib.pyplot as plt
from skimage.draw import circle
import numpy as np
from constant import *
from os import listdir
from os.path import isfile, join, splitext
from skimage.io import imsave
from sklearn.externals import joblib

for i in range(len(scenarios)):
    scenario = scenarios[i]
    n_layer = scenario['layer']
    classifier_filename = classifier_path + scenario['codename'] + "/" + 'RF'+"-"+category+"-"+scenario['codename']+ classifier_extension
    classifier = joblib.load(classifier_filename)
    
    output_directory = output_path + scenario['codename'] + "/"
    if not exists(output_directory):
        makedirs(output_directory)
    
    image_files = [ f for f in listdir(directory_path) if isfile(join(directory_path,f)) ]
    for image_file in image_files:
        print image_file
        a = data.imread(directory_path + splitext(image_file)[0] + ".jpg")
        output = np.zeros((a.shape[0], a.shape[1]))
        global features
        
        im_slic = []
        im_disp = []
        features = []
        
        def list_to_dict(list):
            res = {}
            for l_item in list:
                res[l_item.label] = l_item
            return res
        
        for i in range(n_layer):
            im_slic.append(slic(a, compactness=scenario['settings'][i]['compactness'],
                                n_segments=scenario['settings'][i]['segment'],
                                sigma=scenario['settings'][i]['sigma']))
            im_slic[i] = label(im_slic[i], neighbors=8)
            im_disp.append(np.copy(im_slic[i]))
            temp_feature = regionprops(im_slic[i], intensity_image=rgb2gray(a))
            features.append(list_to_dict(temp_feature))
            
        
        def mark(label, value, im_slice, im_display):
            indexes = np.where(im_slice == label)
            for i, v in enumerate(indexes[0]):
                im_display[v, indexes[1][i]] = value
            
        global labels
        labels = {}
        X_indiv = []
        L_indiv = []
        
        for k, feature in features[0].iteritems():
    #         extract position and corresponding labels
            posY, posX = feature['centroid']
            
            current_labels = []
            
    #         validate labels. 0 label is not allowed
            valid_position = True
            for i in range(n_layer):
                current_level_labels = im_slic[i][posY, posX] 
                current_labels.append(current_level_labels)
                if current_level_labels == 0:
                    valid_position = False
                    break
            
            if not valid_position:
                continue
            
    #         concat all layer properties
            x_entry = []
            for i in range(n_layer):
                feat = features[i][current_labels[i]]
                for att in attributes:
                    if att == 'bbox':
                        (min_row, min_col, max_row, max_col) = feat['bbox']
                        x_entry.append(min_row)
                        x_entry.append(min_col)
                        x_entry.append(max_row)
                        x_entry.append(max_col)
                    else:
                        x_entry.append(feat[att])
            X_indiv.append(x_entry)
            L_indiv.append(feature['label'])
        X_indiv = np.array(X_indiv)
        
        def get_feature_columns():
            n_feature = 12
            n_used_feature = 8
            indexes = []
            current = 0
            for i in range(n_layer):
                indexes += range(current,current+n_used_feature)
                current += n_feature
            return indexes
    
        indexes = get_feature_columns()
        X_indiv = X_indiv[:,indexes]
        Y_indiv = classifier.predict(X_indiv)
        
        for i in range(len(L_indiv)):
            if Y_indiv[i] == 1:
                mark(L_indiv[i], 1, im_slic[0], output)
        print output_directory+splitext(image_file)[0] + ".jpg"
        imsave(output_directory+splitext(image_file)[0] + ".jpg", output)