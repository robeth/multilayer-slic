'''
Created on May 29, 2014

@author: fruity
'''
import numpy as np

def mark(label, value, im_slice, im_display):
        indexes = np.where(im_slice == label)
        for i, v in enumerate(indexes[0]):
            im_display[v, indexes[1][i]] = value
