import numpy as np
from skimage.io import imsave
from util.file import get_files, read_image
from os.path import basename
 
gt_raw_dir = "data/groundtruth/Ellipse-Raw/"
gt_ano_dir = "data/groundtruth/Ellipse-Ano/"
combined_dir = "data/groundtruth/combined/"
comb_head_dir = combined_dir + "comb_head/"
comb_abdo_dir = combined_dir + "comb_abdo/"

raw_filenames = get_files(gt_raw_dir)
ano_filenames = get_files(gt_ano_dir)
combined_filenames = get_files(combined_dir)

def get_identifier(filename):
    return filename[0:-5]

def find_similar(raw_filename, ano_filenames):
    key = get_identifier(raw_filename)
    for ano_filename in ano_filenames:
        if key == get_identifier(ano_filename):
            return ano_filename
    return None

def stack_image(im_path1, im_path2):
    im1 = read_image(im_path1, dir="")
    im2 = read_image(im_path2, dir="")
    new_shape = (im1.shape[0] + im2.shape[0], 
                 max(im1.shape[1], im2.shape[1]),
                 3)
    comb_im = np.zeros(new_shape, dtype=im1.dtype)
    comb_im[0:im1.shape[0], 0:im1.shape[1]] = im1[:]
    comb_im[im1.shape[0]:, 0:im2.shape[1]] = im2[:]
    return comb_im

def get_pair(raw_filenames, ano_filenames):
    pair = []
    for raw_filename in raw_filenames:
        similar_filename = find_similar(raw_filename, ano_filenames)
        if similar_filename is not None:
            new_pair = (gt_raw_dir+raw_filename, gt_ano_dir+similar_filename)
            pair.append(new_pair)
    return pair

def find_in_pair(query, pairs, index):
    for pair in pairs:
        if query == pair[index]:
            return pair
    return None

def ROUTINE_create_stack_images():
    pairs = get_pair(raw_filenames, ano_filenames)
    for pair in pairs:
        combined_image = stack_image(pair[0], pair[1])
        imsave(combined_dir+basename(pair[0]), combined_image)
    
def ROUTINE_delnonpair(delete=False):
    pairs = get_pair(raw_filenames, ano_filenames)
    #del_raw
    for raw_filename in raw_filenames:
        raw_filename = gt_raw_dir + raw_filename
        pair_result = find_in_pair(raw_filename, pairs, 0)
        if (pair_result is None) or (pair_result[1] is None):
            print "Delete Raw:"+raw_filename
    print "----"
    for ano_filename in ano_filenames:
        ano_filename = gt_ano_dir + ano_filename
        pair_result = find_in_pair(ano_filename, pairs, 1)
        if pair_result is None:
            print "Delete Ano:"+ano_filename
            
def ROUTINE_split_head_abdo():
    for combined_filename in combined_filenames:
        combined_image = read_image(combined_dir+combined_filename, dir="")
        image_shape = combined_image.shape
        head_image = combined_image[:, 0:int(image_shape[1]/2)]
        abdo_image = combined_image[:, int(image_shape[1]/2):]
        imsave(comb_head_dir+combined_filename, head_image)
        imsave(comb_abdo_dir+combined_filename, abdo_image)

def annotate_ellipse(input_image, filename, output_filename, tag):
    global in_image
    global in_filename
    
    in_image = input_image
    in_filename = filename
    display_image = np.copy(input_image)
    
    import matplotlib.pyplot as plt
    global fig
    global plt
    
    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(8,4, forward=True)
    plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)
    pltcop = ax.imshow(display_image)
    ax.set_xticks(())
    ax.set_yticks(())
    
    global click_counter
    global points
    
    click_counter = 0
    points = [[0,0],[0,0],[0,0],[0,0]]
    
    def mark_line(points):
        global in_image
        global plt
        global fig
        
        display_image = np.copy(in_image)
        
        from skimage.draw import line
        r_index, c_index = line(points[0][0], points[0][1], points[1][0], points[1][1])
        display_image[r_index, c_index] = np.array([200,0,0])
        
        r_index, c_index = line(points[2][0], points[2][1], points[3][0], points[3][1])
        display_image[r_index, c_index] = np.array([0,200,0])
        
        pltcop.set_data(display_image)
        fig.canvas.draw()
    
    def click(event):
        global click_counter
        global points
        
        if(event.xdata is None): return
        x = int(event.xdata)
        y = int(event.ydata)
        points[click_counter] = [y, x]
        click_counter += 1
        if click_counter >= len(points):
            click_counter = 0
        mark_line(points)
    
    def on_key(event):
        global points
        global in_filename
        if event.key == "enter":
            print points
            f = open(combined_dir + output_filename , 'a')
            f.write(in_filename+",")
            for point in points:
                f.write(str(point[0])+","+str(point[1])+",")
            f.write(tag+"\n")
            f.close()
            plt.close('all')
                
    cid = fig.canvas.mpl_connect('button_press_event', click)
    cid = fig.canvas.mpl_connect('key_press_event', on_key)

    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()
    
def annotate_head(input_image, filename):
    annotate_ellipse(input_image, filename, "head_points.txt", "head")

def ROUTINE_annotate_head():
    head_filenames = ["TGL 4 DESEMBER 2012_3_3.JPG"]#get_files(comb_head_dir)
    for head_filename in head_filenames:
        head_sample = read_image(head_filename, dir=comb_head_dir)
        head_sample = head_sample[int(head_sample.shape[0]/2):,:]
        annotate_head(head_sample, head_filename)
    

# ROUTINE_create_stack_images()
# ROUTINE_split_head_abdo()
ROUTINE_annotate_head()