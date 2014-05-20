'''
Input: Centroid position array in category/position/[image-name].nparray
    Format position for @image --> [coordX coordX label Y]
Ouput: Multilayer-superpixel array in category/nparray/[scenario-name]/[image-name].nparray
    Format multilayer-superpixel for @image --> [layer1 layer2 layer 3 ... layer N]
    
Applied on all scenarios

@author: fruity
'''
from skimage import data
from skimage.color.colorconv import rgb2gray
from skimage.segmentation import slic, mark_boundaries
from skimage.measure import regionprops
from skimage.morphology import label
from constant import array_path, attributes, directory_path, groundtruth_path, position_path
import numpy as np
from os import listdir, makedirs
from os.path import isfile, join, splitext, exists

global a
global im_slic
global im_disp

def extract_feature(scenario):
    n_layer = scenario['layer']
    target_directory = array_path + scenario['codename'] + "/"
    if not exists(target_directory):
        print "Extracting feature "+scenario['codename']
        makedirs(target_directory)
    else:
        print "feature "+scenario['codename']+" is already existed. Abort mission"
        return
        
    # Ambil semua file gambar
    position_files = [ f for f in listdir(position_path) if isfile(join(position_path, f)) ]
    counter = 0
    for position_file in position_files:
#         print "Extracting %s:%s"%(counter, position_file)
        counter += 1
        a = data.imread(directory_path + splitext(position_file)[0] + ".jpg")
        gt = data.imread(groundtruth_path + splitext(position_file)[0] + "-gt.jpg", as_grey=True)
        gt = gt > 20
        gt = gt.astype(int)
        
        global fig
        global features
        
        im_slic = []
        im_disp = []
        im_bound = []
        features = []
        
        def list_to_dict(l):
            res = {}
            for l_item in l:
                res[l_item.label] = l_item
            return res
        
        for i in range(n_layer):
            im_slic.append(slic(a, compactness=scenario['settings'][i]['compactness'],
                                n_segments=scenario['settings'][i]['segment'],
                                sigma=scenario['settings'][i]['sigma']))
            im_slic[i] = label(im_slic[i], neighbors=8)
            im_disp.append(np.copy(im_slic[i]))
            im_bound.append(mark_boundaries(a, im_slic[i]))
            temp_feature = regionprops(im_slic[i], intensity_image=rgb2gray(a))
            features.append(list_to_dict(temp_feature))
            
        coordinates = features[0]
        
        def mark(label, value, im_slice, im_display):
            indexes = np.where(im_slice == label)
            for i, v in enumerate(indexes[0]):
                im_display[v, indexes[1][i]] = value
            
        global labels
        labels = {}
        X_indiv = []
        
        for k,coord in coordinates.items():
    #         extract position and corresponding labels
            posY, posX = coord['centroid']
            posLabel = gt[posY, posX]
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
                if posLabel == 1:
                    mark(current_labels[i], 1, im_slic[i], im_disp[i])
            x_entry.append(posLabel)
            X_indiv.append(x_entry)
        f = open(target_directory + splitext(position_file)[0] + ".nparray" , 'w')
        X_indiv = np.array(X_indiv)
        np.save(f, X_indiv)
        f.close() 
#         print "X_indiv: "+str(X_indiv.shape)
