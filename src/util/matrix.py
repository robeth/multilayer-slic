'''
Created on May 29, 2014

@author: fruity
'''
import numpy as np

def unique_rows(x):
    x_unique = np.ascontiguousarray(x).view(np.dtype((np.void, x.dtype.itemsize * x.shape[1])))
    _, idx = np.unique(x_unique, return_index=True)
    x_unique = x[idx]
    return x_unique