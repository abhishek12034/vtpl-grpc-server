#!/usr/bin/env python
# coding: utf-8

# In[31]:


import os
import time
from os import walk
import copy
import numpy as np
import cv2 as cv
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

class annotate_process:
    def __init__(self):
        self.last_overall_time = 0
        self.last_processing_time = 0
        self.last_reading_time = 0
        self.last_writing_time = 0
        self.last_functional_processing_time = 0
        self.processing_image_cnt = 0
        
        self.in_out_type = ""
        self.in_param = ""
        self.assign_default()

    def assign_default(self):
        self.in_out_type = "cv2"
        self.in_param = "Input-"
        self.in_param += "\n <in_img_path> path of the image folder"
        self.in_param += "\n <process_all_flag> If true the process for all the files"
        self.in_param += "\n <in_img_list> list of the images image folder"
        self.in_param += "\n <process_type> is to set what processing is required"

        self.in_param += "\n\t <process_type> = annotate - to set the spline for exposure"
        self.in_param += "\n\t\t <black_image_path> = >= '/allshare/annotation_on_black.png' --> black image path"
        self.in_param += "\n\t\t <white_image_path> = >= '/allshare/annotation_on_white.png' --> white image path"

    def extract_alpha_and_value_mat_from_black_white_imgages(self, black_img, white_img):
        black = black_img.astype(np.float32)
        white = white_img.astype(np.float32)
    
        height = min(black.shape[0], white.shape[0])
        width = min(black.shape[1], white.shape[1])
    
        black = black[:height, :width]
        white = white[:height, :width]
    
        alpha_mat = (white - black) / 255.0
    
        denominator = 255.0 - white + black
        denominator = np.clip(denominator, 1e-5, None)  # avoid divide-by-zero
    
        value_mat = (255.0 * black) / denominator
    
        return alpha_mat, value_mat
        
    def mod_annotate(self, in_img_path = "",
                            process_all_flag = False, 
                            in_img_list = [], 
                            process_type = "", 
                   
                            black_image_path = "",
                            white_image_path = "",
                                                
                            out_img_path = ""):
        t_st = time.time()
        
        self.last_overall_time = 0
        self.last_processing_time = 0
        self.last_reading_time = 0
        self.last_writing_time = 0
        self.processing_image_cnt = 0
        
        f_path_list = []
        f_name_list = []
        
        if process_all_flag:            
            for (dirpath, dirnames, filenames) in walk(in_img_path):
                f_name_list.extend(filenames)
                break
            
            for i_cnt in range(len(f_name_list)):
                f_path_list.append(os.path.join(in_img_path, f_name_list[i_cnt]))
        else:
            if type(in_img_list) == str:
                f_path_list.append(os.path.join(in_img_path, in_img_list))
                f_name_list.append(in_img_list)
            elif type(in_img_list) == list:
                for i_cnt in range(len(in_img_list)):
                    f_path_list.append(os.path.join(in_img_path, in_img_list[i_cnt]))
                    f_name_list.append(in_img_list[i_cnt])

        black_img = cv.imread(black_image_path)
        white_img = cv.imread(white_image_path)

        if black_img is None:
            raise ValueError(f"Could not read black image from path: {black_image_path}")
        if white_img is None:
            raise ValueError(f"Could not read white image from path: {white_image_path}")

        alpha_mat, value_mat = self.extract_alpha_and_value_mat_from_black_white_imgages(black_img, white_img)

        if process_type == "annotate_with_bw":
            for f_i_cnt in range(len(f_path_list)):
                t_st_read = time.time()
    
                #in_img is in BGR format
                in_img = cv.imread(f_path_list[f_i_cnt])
                if np.any(in_img):
                    self.processing_image_cnt += 1
                    t_en_read = time.time()
                    self.last_reading_time += (t_en_read -  t_st_read)
    
                    t_st_process = time.time()
                    
                    out_img = copy.deepcopy(in_img)

                    height = min(black_img.shape[0], in_img.shape[0])
                    width = min(black_img.shape[1], in_img.shape[1])

                    in_img_part = in_img[:height, :width].astype(np.float32)
                    value_part = value_mat[:height, :width]
                    alpha_part = alpha_mat[:height, :width]
                
                    blended_mat = np.clip(in_img_part * alpha_part + value_part * (1.0 - alpha_part), 0, 255).astype(np.uint8)
                
                    out_img[:height, :width] = blended_mat
                    
                    t_en_process = time.time()
                    self.last_processing_time += (t_en_process - t_st_process)
    
                    t_st_write = time.time()
                    
                    cv.imwrite(os.path.join(out_img_path, f_name_list[f_i_cnt]), out_img)
                    t_en_write = time.time()
                    self.last_writing_time += (t_en_write -  t_st_write)

        t_en = time.time()
        self.last_overall_time = (t_en - t_st)


# # In[33]:


# im_cp = annotate_process()

# # In[ ]:


# in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]

# # In[39]:


# im_cp.mod_annotate(in_img_path = "D:/MyData/Test_Set_01/vid_1/",  
#             process_all_flag = True,
#             process_type = "annotate_with_bw",
#             # black_image_path = "D:/MyData/Test_Set_01/input_bw_img/black.png",
#             # white_image_path = "D:/MyData/Test_Set_01/input_bw_img/white.png",
#             black_image_path = "D:/MyData/Test_Set_01/input_bw_img/black-medium.png",
#             white_image_path = "D:/MyData/Test_Set_01/input_bw_img/white-medium.png",
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s") 

# # In[ ]:



