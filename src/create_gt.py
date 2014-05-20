'''
@author: fruity
'''

from skimage import data
from skimage.color.colorconv import rgb2gray
from skimage.segmentation import slic, mark_boundaries
from skimage.measure import regionprops
from skimage.morphology import label
import matplotlib.pyplot as plt
from skimage.draw import circle
import numpy as np
from constant import *
from os import listdir
from os.path import isfile, join, splitext
from skimage.io import imsave

position_files = [ f for f in listdir(position_path) if isfile(join(position_path, f)) ]
counter = 0
for position_file in position_files:
    print "Process-%s:%s"%(counter, position_file)
    counter += 1
    a = data.imread(directory_path + splitext(position_file)[0] + ".jpg")
    output = np.zeros((a.shape[0], a.shape[1]))
    coordinates = np.load(position_path + position_file)
    # Import image, SLIC, Feature extraction, & GUI interface
    im_slic = slic(a, compactness=layer[0]['compactness'], n_segments=layer[0]['segment'], sigma=1)
    im_slic = label(im_slic, neighbors=8)
    temp = regionprops(im_slic, intensity_image=rgb2gray(a))
    
    def list_to_dict(l):
        res = {}
        for l_item in l:
            res[l_item.label] = l_item
        return res
    
    features = list_to_dict(temp)
    
        
    def mark(label, value, im_slice, im_display):
        indexes = np.where(im_slice == label)
        for i,v in enumerate(indexes[0]):
            im_display[v,indexes[1][i]] = value
        
    for coord in coordinates:
#         extract position and corresponding labels
        posY = coord[0]
        posX = coord[1]
        posLabel = coord[3]
        curLabel = im_slic[posY, posX]
        if posLabel == 1:
            mark(curLabel, 1, im_slic, output)
    imsave(groundtruth_path+splitext(position_file)[0] + "-gt.jpg", output)
        