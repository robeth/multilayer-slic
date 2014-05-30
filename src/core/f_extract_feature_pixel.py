'''
Modul Ektraksi fitur multilayer:
    1. SLIC untuk setiap layer
    2. Fitur setiap piksel = [ [fitur_layer_1], ..., [fitur_layer_n] label] 
    3. Hapus fitur duplikat
    4. Tulis file fitur
    
@author: fruity
'''

from skimage.color.colorconv import rgb2gray
from skimage.segmentation import slic, mark_boundaries
from skimage.measure import regionprops
from skimage.morphology import label
from constant import attributes, directory_path
import numpy as np

from util import list_to_dict, get_feature_array_scenario_path, get_feature_array_file
from util.image import mark
from util.matrix import unique_rows
from util.file import create_directory, get_files, read_image, read_groundtruth_image

global a
global im_slic
global im_disp

def extract_feature(scenario):
    n_layer = scenario['layer']
    target_directory = get_feature_array_scenario_path(scenario['codename'])
    
    create_directory(target_directory)
    array_px_files = get_files(target_directory)
    
    # Jangan lakukan ekstraksi fitur ulang
    if len(array_px_files) >= 50:
        print "feature "+scenario['codename']+" is already existed. Abort mission"
        return
        
    # Ambil semua file gambar
    image_filenames = get_files(directory_path)
    counter = 0
    for image_filename in image_filenames:
#         print "Extracting %s:%s"%(counter, position_file)
        counter += 1
        a = read_image(image_filename)
        gt = read_groundtruth_image(image_filename)
        
        # konversi menjadi binary image
        gt = gt > 20
        gt = gt.astype(int)
        image_shape = a.shape
        image_row = image_shape[0]
        image_col = image_shape[1]
        image_layer = image_shape[2]
        
        im_slic = []
        im_disp = []
        im_bound = []
        features = []
        
        # Extract superpixel feature for each layer
        for i in range(n_layer):
            im_slic.append(slic(a, compactness=scenario['settings'][i]['compactness'],
                                n_segments=scenario['settings'][i]['segment'],
                                sigma=scenario['settings'][i]['sigma']))
            im_slic[i] = label(im_slic[i], neighbors=8)
            im_disp.append(np.copy(im_slic[i]))
            im_bound.append(mark_boundaries(a, im_slic[i]))
            temp_feature = regionprops(im_slic[i], intensity_image=rgb2gray(a))
            features.append(list_to_dict(temp_feature))
            
        X_indiv = []
        
        for im_row in range(image_row):
            for im_col in range(image_col):
    #         extract position and corresponding labels
                posLabel = gt[im_row, im_col]
                current_labels = []
                
        #         validate labels. 0 label is not allowed. causing not exists error
                valid_position = True
                for i in range(n_layer):
                    current_level_labels = im_slic[i][im_row, im_col] 
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
                
        f = get_feature_array_file(scenario['codename'], image_filename, mode='w')
        
        X_indiv = np.array(X_indiv)
        X_indiv_u = unique_rows(X_indiv)
        np.save(f, X_indiv_u)
        f.close() 
#         print "X_indiv: "+str(X_indiv.shape)


results = []
s = {"layer": 1,
                "settings": [{'compactness':10, 'segment':500, 'sigma':1}],
                "codename" : "solo-c%s-s%s"%(10,500) }
extract_feature(s)
from f_create_model_pixel import create_model
print results.append(create_model(s))

