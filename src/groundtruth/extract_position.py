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
from os import listdir
from os.path import isfile, join, splitext

gt_dir = "data/groundtruth/"
pos_dir = gt_dir + "position/"
head_pos_dir = pos_dir + "head/"
abdo_pos_dir = pos_dir + "abdo/"
femur_pos_dir = pos_dir + "femur/"
humerus_pos_dir = pos_dir + "humerus/"

chosen_dir = gt_dir + "chosen/"
head_chosen_dir = chosen_dir+ "head-chosen/"
abdo_chosen_dir = chosen_dir+ "abdo-chosen/"
femur_chosen_dir = chosen_dir + "femur-chosen/"
humerus_chosen_dir = chosen_dir + "humerus-chosen/"

def extract_position(mode="head"):
    if mode=="head":
        data_dir = head_chosen_dir
        position_dir = head_pos_dir
    elif mode =="femur":
        data_dir = femur_chosen_dir
        position_dir = femur_pos_dir
    elif mode == "humerus":
        data_dir = humerus_chosen_dir
        position_dir = humerus_pos_dir
    elif mode == "abdo":
        data_dir = abdo_chosen_dir
        position_dir = abdo_pos_dir
        
    global a
    global im_slic
    global im_disp
    image_files = [ f for f in listdir(data_dir) if isfile(join(data_dir,f)) ]
    for image_file in image_files:
        position_filepath = join(position_dir, image_file)
        if isfile(position_filepath):
            print "%s position already exits"%(image_file)
            continue
        
        print "Extracting position data of %s"%(image_file)
        a = data.imread(join(data_dir, image_file))
        # Import image, SLIC, Feature extraction, & GUI interface
        im_slic = slic(a, compactness=20, n_segments=1000, sigma=0.5)
        im_slic = label(im_slic, neighbors=8)
        im_disp = np.copy(im_slic)
        im_bound = mark_boundaries(a, im_slic)
        
        # Drawing module
        global fig
        global pltcop
        global features
        
        fig, ax = plt.subplots(1,3)
        fig.set_size_inches(8,4, forward=True)
        plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)
        
        ax[0].imshow(a)
        ax[0].set_title("Input")
        pltcop0 = ax[1].imshow(im_bound)
        ax[1].set_title("SLIC 1")
        pltcop = ax[2].imshow(im_disp)
        ax[2].set_title("Preview 1")
        
        
        temp = regionprops(im_slic, intensity_image=rgb2gray(a))
        
        for reg_prop in temp:
            centerY, centerX = reg_prop['centroid']
            rr, cc = circle(centerY,centerX, 1)
            im_bound[rr, cc] = np.array([0, 1, 0])
        pltcop0.set_data(im_bound)
             
        
        def list_to_dict(list):
            res = {}
            for l_item in list:
                res[l_item.label] = l_item
            return res
        
        features = list_to_dict(temp)
        
        global labels
        labels = {}
            
        def tostr(x, y):
            return str(int(x))+","+str(int(y))
            
        def mark(label, value, im_slice, im_display, pltcopa):
            global fig
            indexes = np.where(im_slice == label)
            for i,v in enumerate(indexes[0]):
                im_display[v,indexes[1][i]] = value
            pltcopa.set_data(im_display)
            fig.canvas.draw()
            
        def click(event):
    #         Only consider click event on SLIC 1 image
            if event.inaxes.get_title() != "SLIC 1":
                return
            
            global labels
            global im_slic
            global im_disp
            global pltcop
            
            x = int(event.xdata)
            y = int(event.ydata)
            label = im_slic[y, x]
            
            if label == 0:
                return
            
            if event.button == 1:
                if not (label in labels):
                    labels[label] = True
                    mark(label, 1, im_slic, im_disp, pltcop)
                else:
                    del labels[label]
                    mark(label, label, im_slic, im_disp, pltcop)
            print str(len(labels))
        
        def on_key(event):
            global labels
            global features
            X_indiv = []
            if event.key == "enter":
                print "All superpixel:"+str(len(features))
                print "True superpixel:"+str(len(labels))
                for k,v in labels.items():
                    if k == 0:
                        continue
                    line = []
                    feat = features[k]
                    centroY, centroX = feat['centroid']
                    line.append(centroY)
                    line.append(centroX)
                    line.append(feat['label'])
                    line.append(1)
                    X_indiv.append(line)
                counter = 0
                for key_label,feat in features.iteritems():
                    if not key_label in labels:
                        if key_label == 0:
                            continue
                        x_entry = []
                        centroY, centroX = feat['centroid']
                        x_entry.append(centroY)
                        x_entry.append(centroX)
                        x_entry.append(feat['label'])
                        x_entry.append(0)
                        X_indiv.append(x_entry)
                        counter += 1
                print "False superpiksel:"+str(counter)       
                print "True superpiksel: "+str(len(labels))
                print "X entries:"+str(len(X_indiv))
                print "Entry attributes:" + str(len(X_indiv[0]))
                
                f = open(position_filepath , 'w')
                X_indiv = np.array(X_indiv)
                np.save(f, X_indiv)
                f.close()
                plt.close('all')
                    
        cid = fig.canvas.mpl_connect('button_press_event', click)
        cid = fig.canvas.mpl_connect('key_press_event', on_key)
        
        for arr in ax:
            arr.set_xticks(())
            arr.set_yticks(())
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()
        
extract_position(mode="humerus")