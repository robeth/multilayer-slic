'''
Created on May 29, 2014

@author: fruity
'''
from skimage import data
from os import listdir, makedirs
from os.path import isfile, join, splitext, exists
from constant import directory_path, groundtruth_path

def read_image(file_path, dir=directory_path, grey=False):
    return data.imread(dir+file_path, as_grey=grey)

def read_groundtruth_image(filename):
    return read_image(groundtruth_path+splitext(filename)[0]+"-gt.jpg", dir="",grey=True)

def get_files(directory_path):
    return [ f for f in listdir(directory_path) if isfile(join(directory_path,f)) ]

def create_directory(directory_path):
    if not exists(directory_path):
        makedirs(directory_path)

