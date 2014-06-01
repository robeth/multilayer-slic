import numpy as np
from skimage.io import imsave
from util.file import get_files, read_image
from os.path import basename
 
gt_raw_dir = "data/groundtruth/Ellipse-Raw/"
gt_ano_dir = "data/groundtruth/Ellipse-Ano/"
combined_dir = "data/groundtruth/combined/"
comb_head_dir = combined_dir + "comb_head/"
comb_abdo_dir = combined_dir + "comb_abdo/"
head_anno_filename = "head_points.txt"
head_anno_path = combined_dir + head_anno_filename

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
            new_pair = (gt_raw_dir + raw_filename, gt_ano_dir + similar_filename)
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
        imsave(combined_dir + basename(pair[0]), combined_image)
    
def ROUTINE_delnonpair(delete=False):
    pairs = get_pair(raw_filenames, ano_filenames)
    # del_raw
    for raw_filename in raw_filenames:
        raw_filename = gt_raw_dir + raw_filename
        pair_result = find_in_pair(raw_filename, pairs, 0)
        if (pair_result is None) or (pair_result[1] is None):
            print "Delete Raw:" + raw_filename
    print "----"
    for ano_filename in ano_filenames:
        ano_filename = gt_ano_dir + ano_filename
        pair_result = find_in_pair(ano_filename, pairs, 1)
        if pair_result is None:
            print "Delete Ano:" + ano_filename
            
def ROUTINE_split_head_abdo():
    for combined_filename in combined_filenames:
        combined_image = read_image(combined_dir + combined_filename, dir="")
        image_shape = combined_image.shape
        head_image = combined_image[:, 0:int(image_shape[1] / 2)]
        abdo_image = combined_image[:, int(image_shape[1] / 2):]
        imsave(comb_head_dir + combined_filename, head_image)
        imsave(comb_abdo_dir + combined_filename, abdo_image)

def annotate_ellipse(input_image, filename, output_filename, tag, params=None, save=True, draw_ellipse=False, mode=1):
    global in_image
    global in_filename
    
    in_image = input_image
    in_filename = filename
    display_image = np.copy(input_image)
    
    if draw_ellipse:
        from skimage.draw import ellipse_perimeter
        r_index, c_index = ellipse_perimeter(params[0], params[1],
                                             params[2], params[3],
                                             params[4])
        display_image[r_index, c_index] = np.array([0, 0, 200])
    
    import matplotlib.pyplot as plt
    global fig
    global plt
    
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 4, forward=True)
    plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)
    pltcop = ax.imshow(display_image)
    ax.set_xticks(())
    ax.set_yticks(())
    
    global click_counter
    global is_select_axis
    global points
    global semi_minor
    global ellipse_params
    
    click_counter = 0
    points = [[0, 0], [0, 0]]
    is_select_axis = True
    semi_minor = 5
    ellipse_params = [0,0,0,0,0]
    
        
    def redraw():
        global points
        global ellipse_params
        global in_image
        global plt
        global fig
        
        display_image = np.copy(in_image)
        
        from skimage.draw import line
        r_index, c_index = line(points[0][0], points[0][1], points[1][0], points[1][1])
        display_image[r_index, c_index] = np.array([200, 0, 0])
        
        if ellipse_params is not None:
            r_index, c_index = ellipse_perimeter(ellipse_params[0], ellipse_params[1],
                                                 ellipse_params[2], ellipse_params[3],
                                                 ellipse_params[4])
            display_image[r_index, c_index] = np.array([0, 0, 200])
        
        pltcop.set_data(display_image)
        fig.canvas.draw()
    
    def click(event):
        global click_counter
        global points
        global is_select_axis
        global semi_minor
        global ellipse_params
        print "you pressed button: %s" % (str(event.button))
        
        def find_length(y1, y2, x1, x2):
            from math import sqrt, pow
            return sqrt(pow(y1 - y2, 2) + pow(x1 - x2, 2))
        def find_center(y1, y2, x1, x2):
            return [(y1 + y2) / 2, (x1 + x2) / 2]
        def find_rad(y1, y2, x1, x2):
            from math import radians
            if x1 == x2: print "EQUALS"; return radians(90)
            else:
                return float(y1 - y2) / float(x1 - x2)
                
        if event.button == 3:
            is_select_axis = not is_select_axis
        
        elif event.button == 1:
            if(event.xdata is None): return
            
            x = int(event.xdata)
            y = int(event.ydata)
            if is_select_axis:
                points[click_counter] = [y, x]
                click_counter += 1
                if click_counter >= len(points):
                    click_counter = 0  
            
            center_y, center_x = find_center(points[0][0], points[1][0], points[0][1], points[1][1])
            if not is_select_axis:
                semi_minor = find_length(center_y, y, center_x, x)
            semi_major = find_length(points[0][0], points[1][0], points[0][1], points[1][1])/2
            from math import atan
            radi = atan(find_rad(points[0][0], points[1][0], points[0][1], points[1][1]))
            ellipse_params = [int(center_y), int(center_x), int(semi_minor), int(semi_major), radi]
            redraw()
    
    def on_key(event):
        global points
        global ellipse_params
        global in_filename
        if event.key == "enter":
            print points
            if save:
                f = open(combined_dir + output_filename , 'a')
                f.write(in_filename + ",")
                for e_param in ellipse_params:
                    f.write(str(e_param) + ",")
                f.write(tag + "\n")
                f.close()
            plt.close('all')
                
    cid = fig.canvas.mpl_connect('button_press_event', click)
    cid = fig.canvas.mpl_connect('key_press_event', on_key)

    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()
    
def annotate_head(input_image, filename):
    annotate_ellipse(input_image, filename, "head_points.txt", "head")
    
def get_anno_image(input_image):
    return input_image[int(input_image.shape[0] / 2):, :]

def get_raw_image(input_image):
    return input_image[0:int(input_image.shape[0] / 2), :]

def ROUTINE_annotate_head():
    head_filenames = get_files(comb_head_dir)
    for head_filename in head_filenames:
        head_sample = read_image(head_filename, dir=comb_head_dir)
        head_sample = get_anno_image(head_sample)
        annotate_head(head_sample, head_filename)

def read_anno_result(anno_path):
    anno_file = open(anno_path, "r")
    lines = anno_file.readlines()
    anno_dictionary = {}
    for line in lines:
        parts = line.split(",")
        contents = []
        for i in range(1, len(parts)):
            if parts[i].isdigit():
                parts[i] = int(parts[i])
            contents.append(parts[i])
        anno_dictionary[parts[0]] = contents
        print anno_dictionary[parts[0]]
    return anno_dictionary

def validate_ellipse_anno(image, filename, params):
    annotate_ellipse(image, filename, "head_points.txt", "head", params, True, True)

def ROUTINE_check_head_anno():
    params_dictionary = read_anno_result(head_anno_path)
    head_filenames = get_files(comb_head_dir)
    for head_filename in head_filenames:
        head_image = read_image(head_filename, dir=comb_head_dir)
        head_image = get_anno_image(head_image)
        validate_ellipse_anno(head_image, head_filename, params_helper(params_dictionary[head_filename]))

def params_helper(params):
    return get_ellipse_params(params[0], params[1], params[2], params[3], params[4], params[5], params[6], params[7])
        
def get_ellipse_params(y1, x1, y2, x2, y3, x3, y4, x4):
    from shapely.geometry import LineString
    from math import radians, degrees, atan
    line1 = LineString([(x1, y1), (x2, y2)])
    line2 = LineString([(x3, y3), (x4, y4)])
    
    minor = major = None
    rad = degrees(90)
    
    if line1.length > line2.length:
        major = line1
        minor = line2
    else:
        major = line2
        minor = line1
        
    intersection_point = line1.intersection(line2)
    major_point1_x, major_point1_y = major.coords[0]
    major_point2_x, major_point2_y = major.coords[1]
    
    if major_point1_x != major_point2_y:
        tan_value = (major_point1_y - major_point2_y) / (major_point1_x - major_point2_x)
        rad = atan(tan_value)
        
    ellipse_params = [int(intersection_point.y), int(intersection_point.x), int(minor.length / 2), int(major.length / 2), rad]
    print ellipse_params
    return ellipse_params

# ROUTINE_create_stack_images()
# ROUTINE_split_head_abdo()
# ROUTINE_annotate_head()
ROUTINE_check_head_anno()
