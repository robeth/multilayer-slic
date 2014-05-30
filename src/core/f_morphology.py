'''
@author: fruity
'''
from skimage import data
from skimage.measure import regionprops
from skimage.morphology import label, opening, closing, disk
from constant import directory_path, output_morph_path
import numpy as np
from os import listdir, makedirs
from os.path import isfile, join, splitext, exists
import matplotlib.pyplot as plt
from skimage.util import img_as_ubyte
from skimage.filter import threshold_otsu
from skimage.color import rgb2gray
def morphology(filepath):
    I = img_as_ubyte(data.imread(filepath, as_grey=True))
    
    SE15 = disk(20)
    O = opening(I, SE15)
    
    S = I - O
     
    SE1 = disk(1)
    C = closing(S, SE1)
    
    return I, C

def plot_comparison(original, thresholded, filtered, maxed, fname):
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(ncols=4)
    ax1.imshow(original, cmap=plt.cm.gray)
    ax1.set_title('Original')
    ax1.axis('off')
    ax2.imshow(thresholded, cmap=plt.cm.gray)
    ax2.set_title("Thresholded")
    ax2.axis('off')
    ax3.imshow(filtered, cmap=plt.cm.gray)
    ax3.set_title("Filtered")
    ax3.axis('off')
    ax4.imshow(maxed, cmap=plt.cm.gray)
    ax4.set_title("Max Area")
    ax4.axis('off')
    plt.savefig(output_morph_path+fname)

def filter_area(input_image):
    input = np.copy(input_image)
    L = label(input)
    prop = regionprops(L)
    
    max_area = 0
    max_label = -1
    
    for p in prop:
        if p['minor_axis_length'] < 5 or p['major_axis_length'] < 5:
            input[L == p['label']] = 0
        if p['area'] > max_area:
            max_area = p['area']
            max_label = p['label']
    max_image = np.copy(input)
    
    if max_label != 1:
        for p in prop:
            if p['label'] != max_label:
                max_image[L == p['label']] = 0
    return input, max_image
    
    
image_files = [ f for f in listdir(directory_path) if isfile(join(directory_path, f)) ]
for image_file in image_files:
    initial, C = morphology(directory_path+image_file)
    T = C > 0.4 * 255
    F, M = filter_area(T)
    plot_comparison(initial, T, F, M, "m_"+image_file)

