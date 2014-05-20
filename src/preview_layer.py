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

scenarios_dummy = [{"layer": 3, 
              "settings":[{'compactness':20, 'segment':1000, 'sigma':0.5}, 
                          {'compactness':15, 'segment':1000, 'sigma':0.5},
                          {'compactness':10, 'segment':1000, 'sigma':0.5}],
              "codename": "base3"
              }]

for i in range(len(scenarios_dummy)):
    scenario = scenarios_dummy[i]
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
            
        column_count = min(4, n_layer)
        row_count = int(ceil(float(n_layer)/column_count))
        fig, ax = plt.subplots(row_count, column_count)
        fig.set_size_inches(8, 4, forward=True)
        plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)
         
        current_column = 0
        current_row = 0
        for i in range(n_layer):
            if row_count == 1:
                ax[current_column].imshow(im_bound[i])
                ax[current_column].set_title("S:%s - C:%s "%(scenario['settings'][i]['segment'],scenario['settings'][i]['compactness']))
            else:
                ax[current_row][current_column].imshow(im_bound[i])
                ax[current_row][current_column].set_title("S:%s - C:%s "%(scenario['settings'][i]['segment'],scenario['settings'][i]['compactness']))
            current_column += 1
            if current_column >= column_count:
                current_column = 0
                current_row += 1
             
        def on_key(event):
    #         Only consider click event on SLIC 1 image
            global plt
            if event.key == "enter":
                plt.close('all')
         
        cid = fig.canvas.mpl_connect('key_press_event', on_key)
         
        if row_count > 1:
            for arr in ax:
                for a in arr:
                    a.set_xticks(())
                    a.set_yticks(())
        else:
            for arr in ax:
                arr.set_xticks(())
                arr.set_yticks(())
                 
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()
