import numpy as np
from skimage.io import imsave
from util.file import get_files, read_image
from os.path import basename
 
gt_dir = "data/groundtruth/"
gt_raw_dir = gt_dir + "Ellipse-Raw/"
gt_ano_dir = gt_dir + "Ellipse-Ano/"
combined_dir = gt_dir + "combined/"
comb_head_dir = combined_dir + "comb_head/"
comb_abdo_dir = combined_dir + "comb_abdo/"
head_anno_filename = "head_points.txt"
head_anno_path = gt_dir + head_anno_filename
line_mark_filename = "line_mark.txt"
line_mark_path = gt_dir + line_mark_filename

gt_raw_line_dir = gt_dir + "Line-Raw/"
gt_ano_line_dir = gt_dir + "Line-Ano/"
combined_line_dir = gt_dir + "combined-line/"
comb_femur_dir = combined_line_dir + "comb-femur/"
comb_humerus_dir = combined_line_dir + "comb-humerus/"
femur_anno_filename = "femur-result.txt"
humerus_anno_filename = "humerus-result.txt"
femur_anno_filepath = gt_dir + femur_anno_filename
humerus_anno_filepath = gt_dir + humerus_anno_filename

head_chosen_filename = "head_chosen.txt"
abdo_chosen_filename = "abdo_chosen.txt"
femur_chosen_filename = "femur_chosen.txt"
humerus_chosen_filename = "humerus_chosen.txt"
head_chosen_path = gt_dir+head_chosen_filename
abdo_chosen_path = gt_dir+abdo_chosen_filename
femur_chosen_path = gt_dir + femur_chosen_filename
humerus_chosen_path = gt_dir + humerus_chosen_filename

final_path = gt_dir + "chosen/"
head_final_path = final_path+ "head-chosen/"
abdo_final_path = final_path+ "abdo-chosen/"
femur_final_path = final_path + "femur-chosen/"
humerus_final_path = final_path + "humerus-chosen/"


ellipse_raw_filenames = get_files(gt_raw_dir)
ellipse_ano_filenames = get_files(gt_ano_dir)
ellipse_combined_filenames = get_files(combined_dir)

line_raw_filenames = get_files(gt_raw_line_dir)
line_ano_filenames = get_files(gt_ano_line_dir)
line_combined_filenames = get_files(combined_line_dir)

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

def get_pair(raw_filenames, ano_filenames, raw_parent_dir, ano_parent_dir):
    pair = []
    for raw_filename in raw_filenames:
        similar_filename = find_similar(raw_filename, ano_filenames)
        if similar_filename is not None:
            new_pair = (raw_parent_dir + raw_filename, ano_parent_dir + similar_filename)
            pair.append(new_pair)
    return pair

def find_in_pair(query, pairs, index):
    for pair in pairs:
        if query == pair[index]:
            return pair
    return None

def ROUTINE_create_head_stack_images():
    pairs = get_pair(ellipse_raw_filenames, ellipse_ano_filenames, gt_raw_dir, gt_ano_dir)
    for pair in pairs:
        combined_image = stack_image(pair[0], pair[1])
        imsave(combined_dir + basename(pair[0]), combined_image)
        
def ROUTINE_create_line_stack_images():
    pairs = get_pair(line_raw_filenames, line_ano_filenames, gt_raw_line_dir, gt_ano_line_dir)
    for pair in pairs:
        combined_image = stack_image(pair[0], pair[1])
        imsave(combined_line_dir + basename(pair[0]), combined_image)
    
def ROUTINE_head_delnonpair(delete=False):
    pairs = get_pair(ellipse_raw_filenames, ellipse_ano_filenames, gt_raw_dir, gt_ano_dir)
    # del_raw
    for raw_filename in ellipse_raw_filenames:
        raw_filename = gt_raw_dir + raw_filename
        pair_result = find_in_pair(raw_filename, pairs, 0)
        if (pair_result is None) or (pair_result[1] is None):
            print "Delete Raw:" + raw_filename
    print "----"
    for ano_filename in ellipse_ano_filenames:
        ano_filename = gt_ano_dir + ano_filename
        pair_result = find_in_pair(ano_filename, pairs, 1)
        if pair_result is None:
            print "Delete Ano:" + ano_filename
            
def ROUTINE_split_head_abdo():
    for combined_filename in ellipse_combined_filenames:
        combined_image = read_image(combined_dir + combined_filename, dir="")
        image_shape = combined_image.shape
        head_image = combined_image[:, 0:int(image_shape[1] / 2)]
        abdo_image = combined_image[:, int(image_shape[1] / 2):]
        imsave(comb_head_dir + combined_filename, head_image)
        imsave(comb_abdo_dir + combined_filename, abdo_image)

def annotate_ellipse(input_image, filename, output_filename, tag, params=None, save=True):
    from skimage.draw import ellipse_perimeter
    import matplotlib.pyplot as plt
    global in_image
    global in_filename
    
    in_image = input_image
    in_filename = filename
    display_image = np.copy(input_image)
    
    if params:
        r_index, c_index = ellipse_perimeter(params[0], params[1],
                                                 params[2], params[3],
                                                 float(params[4]))
        display_image[r_index, c_index] = np.array([0, 0, 200])
    
    
    
    
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
    ellipse_params = [0, 0, 0, 0, 0]
    
        
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
        
        def find_length(y1, y2, x1, x2):
            from math import sqrt, pow
            return sqrt(pow(y1 - y2, 2) + pow(x1 - x2, 2))
        def find_center(y1, y2, x1, x2):
            return [(y1 + y2) / 2, (x1 + x2) / 2]
        def find_rad(y1, y2, x1, x2):
            from math import radians
            if x1 == x2: return radians(90)
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
            semi_major = find_length(points[0][0], points[1][0], points[0][1], points[1][1]) / 2
            from math import atan
            radi = atan(find_rad(points[0][0], points[1][0], points[0][1], points[1][1]))
            ellipse_params = [int(center_y), int(center_x), int(semi_minor), int(semi_major), radi]
            redraw()
    
    def on_key(event):
        global points
        global ellipse_params
        global in_filename
        if event.key == "enter" or event.key == "shift":
            if save:
                f = open(combined_dir + output_filename , 'a')
                f.write(in_filename + ",")
                for e_param in ellipse_params:
                    f.write(str(e_param) + ",")
                f.write(tag + "\n")
                f.close()
                print "%s:%s" % (in_filename, str(ellipse_params))
            plt.close('all')
    
    if params:
        cid = fig.canvas.mpl_connect('button_press_event', click)
        cid = fig.canvas.mpl_connect('key_press_event', on_key)

    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()

def annotate_line(input_image, filename, output_filename, tag, params=None, save=True):
    from skimage.draw import line
    import matplotlib.pyplot as plt
    global in_image
    global in_filename
    global fig
    global plt
    
    in_image = input_image
    in_filename = filename
    display_image = np.copy(input_image)
    
    if params:
        r_index, c_index = line(params[0], params[1],
                                                 params[2], params[3])
        display_image[r_index, c_index] = np.array([0, 0, 200])
    
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
        
    def redraw():
        global points
        global in_image
        global plt
        global fig
        
        display_image = np.copy(in_image)
        
        r_index, c_index = line(points[0][0], points[0][1], points[1][0], points[1][1])
        display_image[r_index, c_index] = np.array([200, 0, 0])
        
        pltcop.set_data(display_image)
        fig.canvas.draw()
    
    def click(event):
        global click_counter
        global points
        
        def find_length(y1, y2, x1, x2):
            from math import sqrt, pow
            return sqrt(pow(y1 - y2, 2) + pow(x1 - x2, 2))
                
        if event.button == 1:
            if(event.xdata is None): return
            
            x = int(event.xdata)
            y = int(event.ydata)
            points[click_counter] = [y, x]
            click_counter += 1
            if click_counter >= len(points):
                click_counter = 0  
            redraw()
    
    def on_key(event):
        global points
        global ellipse_params
        global in_filename
        if event.key == "enter" or event.key == "shift":
            if save:
                f = open(gt_dir + output_filename , 'a')
                entry = ("%s,%s,%s,%s,%s,%s\n")%(in_filename, points[0][0], points[0][1], points[1][0], points[1][1], tag)
                f.write(entry)
                f.close()
                print entry
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
    annotate_ellipse(image, None, None, None, params, False)

def ROUTINE_check_head_anno():
    params_dictionary = read_anno_result(head_anno_path)
    head_filenames = get_files(comb_head_dir)
    for head_filename in head_filenames:
        head_image = read_image(head_filename, dir=comb_head_dir)
        head_image = get_anno_image(head_image)
        validate_ellipse_anno(head_image, head_filename, params_dictionary[head_filename])

def mark_line(input_image, filename):
    global in_image
    global in_filename
    global fig
    global pltcop
    global display_image
    
    in_image = input_image
    in_filename = filename
    
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 4, forward=True)
    plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)
    pltcop = ax.imshow(input_image)
    ax.set_xticks(())
    ax.set_yticks(())
    
    global is_hc
    is_hc = False
    
    def redraw():
        global in_image
        global display_image
        global pltcop
        global fig
        global is_hc
        
        display_image = np.copy(in_image)
        
        if is_hc:
            from skimage.draw import circle
            r_index, c_index = circle(100, 100, 25)
            display_image[r_index, c_index] = np.array([200, 0, 0])
        pltcop.set_data(display_image)
        fig.canvas.draw()
        
    def click(event):
        global is_hc
                
        if event.button == 3 or event.button == 1:
            is_hc = not is_hc
        redraw()
    
    def on_key(event):
        global in_filename
        global is_hc
        if event.key == "enter" or event.key == "shift":
            f = open(line_mark_path , 'a')
            f.write(in_filename + "," + str(is_hc) + "\n")
            f.close()
            plt.close('all')
    
    cid = fig.canvas.mpl_connect('button_press_event', click)
    cid = fig.canvas.mpl_connect('key_press_event', on_key)

    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()

def ROUTINE_mark_line():
    line_pairs = get_pair(line_raw_filenames, line_ano_filenames , gt_raw_line_dir, gt_ano_line_dir)
    for line_pair in line_pairs:
        full_line_image = stack_image(line_pair[0], line_pair[1])
        from os.path import basename
        print line_pair
        mark_line(full_line_image, basename(line_pair[0]))
        
def read_line_config():
    config_file = open(line_mark_path, "r")
    lines = config_file.readlines()
    config_dictionary = {}
    for line in lines:
        parts = line.split(",")
        parts[1] = parts[1].replace("\n", "")
        config_dictionary[parts[0]] = parts[1] == "True"
    return config_dictionary

def read_chosen_config(chosen_file_path):
    chose_file = open(chosen_file_path, 'r')
    lines = chose_file.readlines()
    dictionary = {}
    for line in lines:
        line = line.replace("\n","")
        line = line.split(",")
        dictionary[line[0]] = line[1] == "1"
    return dictionary

def ROUTINE_split_femur_humerus():
    config_dictionary = read_line_config()
    for combined_filename in line_combined_filenames:
        combined_image = read_image(combined_line_dir + combined_filename, dir="")
        image_shape = combined_image.shape
        image1 = combined_image[:, 0:int(image_shape[1] / 2)]
        image2 = combined_image[:, int(image_shape[1] / 2):]
        if config_dictionary[combined_filename]:
            imsave(comb_femur_dir + combined_filename, image2)
            imsave(comb_humerus_dir + combined_filename, image1)
        else:
            imsave(comb_femur_dir + combined_filename, image1)
            imsave(comb_humerus_dir + combined_filename, image2)
            
def SUBROUTINE_annotate_line(directory, output_filename, tag):
    filenames = get_files(directory)
    for filename in filenames:
        line_image = read_image(filename, dir=directory)
        line_image = get_anno_image(line_image)
        annotate_line(line_image, filename, output_filename, tag)

def ROUTINE_annotate_femur():
    SUBROUTINE_annotate_line(comb_femur_dir, femur_anno_filename, "femur")
    
def ROUTINE_annotate_humerus():
    SUBROUTINE_annotate_line(comb_humerus_dir, humerus_anno_filename, "humerus")
    
def prepare_chosen_file(output_filepath, image_directory):
    filenames = get_files(image_directory)
    out_file = open(output_filepath, 'w')
    for filename in filenames:
        out_file.write(image_directory+filename+",1\n")
    out_file.close()
        
def ROUTINE_prepare_chosen():
    prepare_chosen_file(head_chosen_path, comb_head_dir)
    prepare_chosen_file(abdo_chosen_path, comb_abdo_dir)
    prepare_chosen_file(femur_chosen_path, comb_femur_dir)
    prepare_chosen_file(humerus_chosen_path, comb_humerus_dir)

def write_chosen_dictionary(dictionary, output_filepath):
    output_file = open(output_filepath, 'w')
    for key, value in dictionary.items():
        if value:
            value = "1"
        else:
            value ="0"
        output_file.write(key+","+value+"\n")
    output_file.close()

def choose_file(input_image, file_path, dictionary, output_file_path, counter):
    global in_image
    global in_filepath
    global fig
    global pltcop
    global display_image
    global output_filepath
    global filepath
    
    in_image = input_image
    in_filepath = file_path
    output_filepath = output_file_path
    filepath = file_path
    
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 4, forward=True)
    plt.subplots_adjust(0.05, 0.05, 0.95, 0.95, 0.05, 0.05)
    pltcop = ax.imshow(input_image)
    ax.set_xticks(())
    ax.set_yticks(())
    
    global is_chosen
    is_chosen = dictionary[file_path]
    
    
    def redraw():
        global in_image
        global display_image
        global pltcop
        global fig
        global is_chosen
        
        display_image = np.copy(in_image)
        
        if not is_chosen:
            from skimage.draw import circle
            r_index, c_index = circle(100, 100, 40)
            display_image[r_index, c_index] = np.array([200, 0, 0])
        pltcop.set_data(display_image)
        fig.canvas.draw()
        
    def click(event):
        global is_chosen
        if event.button == 3 or event.button == 1:
            is_chosen = not is_chosen
        redraw()
    
    def on_key(event):
        global in_filename
        global is_chosen
        global output_filepath
        global filepath
        
        if event.key == "enter":
            dictionary[filepath] = is_chosen
            write_chosen_dictionary(dictionary, output_filepath)
        elif event.key == "shift":
            dictionary[filepath] = is_chosen
            write_chosen_dictionary(dictionary, output_filepath)
            plt.close('all')
    
    cid = fig.canvas.mpl_connect('button_press_event', click)
    cid = fig.canvas.mpl_connect('key_press_event', on_key)
    
    redraw()
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.suptitle(str(counter) + file_path)
    plt.show()
    
def del_folder_content(directory):
    filenames = get_files(directory)
    from os.path import isfile, join
    from os import unlink
    for filename in filenames:
        filepath = join(directory, filename)
        if isfile(filepath):
            unlink(filepath)
    
def export_chosen_data(input_folder, target_folder, config_filepath):
    del_folder_content(target_folder)
    config_dictionary = read_chosen_config(config_filepath)
    for image_filepath, chosen_status in config_dictionary.items():
        if chosen_status:
            upper_image = get_raw_image(read_image(image_filepath, dir=""))
            imsave(target_folder+basename(image_filepath), upper_image)
    
def ROUTINE_choose(mode = "head"):
    chosen_path = ""
    if mode == "head":
        chosen_path = head_chosen_path
    elif mode == "abdo":
        chosen_path = abdo_chosen_path
    elif mode == "femur":
        chosen_path = femur_chosen_path
    elif mode == "humerus":
        chosen_path = humerus_chosen_path
        
    dictionary = read_chosen_config(chosen_path)
    counter = 1
    for filepath, value in dictionary.items():
        image = read_image(filepath, dir="")
        choose_file(image, filepath, dictionary, chosen_path, counter)
        counter += 1
        
def ROUTINE_export(dataset="head"):
    if dataset == "head":
        export_chosen_data(comb_head_dir, head_final_path, head_chosen_path)
    elif dataset == "abdo":
        export_chosen_data(comb_abdo_dir, abdo_final_path, abdo_chosen_path)
    elif dataset == "femur":
        export_chosen_data(comb_femur_dir, femur_final_path, femur_chosen_path)
    elif dataset == "humerus":
        export_chosen_data(comb_humerus_dir, humerus_final_path, humerus_chosen_path)
# ROUTINE_mark_line()
# ROUTINE_create_line_stack_images()
# read_line_config()
# ROUTINE_split_femur_humerus()
# ROUTINE_annotate_humerus()
# ROUTINE_choose_head()
# ROUTINE_export("humerus")
# ROUTINE_choose(mode="humerus")
