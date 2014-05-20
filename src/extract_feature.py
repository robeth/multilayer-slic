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
import matplotlib.pyplot as plt
import numpy as np
from constant import *
from os import listdir, makedirs
from os.path import isfile, join, splitext, exists
from math import ceil

global a
global im_slic
global im_disp

for i in range(len(scenarios)):
    scenario = scenarios[i]
    n_layer = scenario['layer']
    target_directory = array_path + scenario['codename'] + "/"
    if not exists(target_directory):
        makedirs(target_directory)
        
    # Ambil semua file gambar
    position_files = [ f for f in listdir(position_path) if isfile(join(position_path, f)) ]
    counter = 0
    for position_file in position_files:
        print "Extractig %s:%s"%(counter, position_file)
        counter += 1
        a = data.imread(directory_path + splitext(position_file)[0] + ".jpg")
        coordinates = np.load(position_path + position_file)
        
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
            
        
        def mark(label, value, im_slice, im_display):
            indexes = np.where(im_slice == label)
            for i, v in enumerate(indexes[0]):
                im_display[v, indexes[1][i]] = value
            
        global labels
        labels = {}
        X_indiv = []
        
        for coord in coordinates:
    #         extract position and corresponding labels
            posY = coord[0]
            posX = coord[1]
            posLabel = coord[3]
            
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
        print "X_indiv: "+str(X_indiv.shape)
        
    #     column_count = min(4, n_layer)
    #     row_count = int(ceil(float(n_layer)/column_count))
    #     fig, ax = plt.subplots(row_count, column_count)
    #     fig.set_size_inches(8, 4, forward=True)
    #     plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)
    #     
    #     current_column = 0
    #     current_row = 0
    #     for i in range(n_layer):
    #         if row_count == 1:
    #             ax[current_column].imshow(im_disp[i])
    #             ax[current_column].set_title("Layer " + str(i))
    #         else:
    #             ax[current_row][current_column].imshow(im_disp[i])
    #             ax[current_row][current_column].set_title("Layer " + str(i))
    #         current_column += 1
    #         if current_column >= column_count:
    #             current_column = 0
    #             current_row += 1
             
    #     def on_key(event):
    # #         Only consider click event on SLIC 1 image
    #         global plt
    #         if event.key == "enter":
    #             plt.close('all')
    #     
    #     cid = fig.canvas.mpl_connect('key_press_event', on_key)
    #     
    #     if row_count > 1:
    #         for arr in ax:
    #             for a in arr:
    #                 a.set_xticks(())
    #                 a.set_yticks(())
    #     else:
    #         for arr in ax:
    #             arr.set_xticks(())
    #             arr.set_yticks(())
    #             
    #     mng = plt.get_current_fig_manager()
    #     mng.resize(*mng.window.maxsize())
    #     plt.show()
