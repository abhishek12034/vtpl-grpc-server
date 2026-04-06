#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import time
from os import walk
import copy
import math
import numpy as np
import cv2 as cv
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt


class sharpen_process:
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

        self.in_param += "\n\t <process_type> = laplacian_sharpen - sharpening using laplacian filter"
        self.in_param += "\n\t\t <in_lap_method> = mild / strong --> mild is default for soft sharpen and strong for strong sharpen"

        self.in_param += (
            "\n\t <process_type> = unsharp_mask - sharpening using unsharp mask"
        )
        self.in_param += "\n\t\t <in_sharpen_spread> = 1 to 32.0 --> Spread of the sharpening mask, default 5.0"
        self.in_param += "\n\t\t <in_sharpen_power> = 0 to 2.0 --> Power of the sharpening function, default 0.5"

    def mod_sharpen(
        self,
        in_img_path="",
        curve_name="",
        write_plot_fig_file="",
        process_all_flag=False,
        in_img_list=[],
        process_type="",
        in_lap_method="mild",
        in_sharpen_spread=5.0,
        in_sharpen_power=0.5,
        out_img_path="",
        par_st_row=None,
        par_en_row=None,
        par_st_col=None,
        par_en_col=None,
        par_process_flag=False,
    ):

        t_st = time.time()

        self.last_overall_time = 0
        self.last_processing_time = 0
        self.last_reading_time = 0
        self.last_writing_time = 0
        self.processing_image_cnt = 0

        f_path_list = []
        f_name_list = []

        if process_all_flag:
            for dirpath, dirnames, filenames in walk(in_img_path):
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

        for f_i_cnt in range(len(f_path_list)):
            t_st_read = time.time()

            # in_img is in BGR format
            in_img = cv.imread(f_path_list[f_i_cnt])
            if np.any(in_img):
                self.processing_image_cnt += 1
                t_en_read = time.time()
                self.last_reading_time += t_en_read - t_st_read

                t_st_process = time.time()

                # ✅ Partial Processing Logic
                if par_process_flag:
                    # Safety validation
                    if None in (par_st_row, par_en_row, par_st_col, par_en_col):
                        raise ValueError(
                            "Partial processing enabled but coordinates missing"
                        )

                    if par_en_row <= par_st_row or par_en_col <= par_st_col:
                        raise ValueError("Invalid crop coordinates")

                    # Save original image and crop the ROI
                    original_img = in_img.copy()
                    in_img = in_img[par_st_row:par_en_row, par_st_col:par_en_col]
                else:
                    original_img = None

                # laplacian_sharpen
                if process_type == "laplacian_sharpen":
                    mod_in_img = np.zeros(
                        (in_img.shape[0], in_img.shape[1], 3), dtype=np.float32
                    )
                    out_img = np.zeros(
                        (in_img.shape[0], in_img.shape[1], 3), dtype=np.uint8
                    )

                    if in_lap_method == "mild":
                        lap_mask = np.array(
                            [[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32
                        )
                        for cch in range(3):
                            mod_in_img[:, :, cch] = cv.filter2D(
                                src=in_img[:, :, cch], ddepth=cv.CV_32F, kernel=lap_mask
                            )
                            mod_in_img[:, :, cch] = np.abs(
                                in_img[:, :, cch] - mod_in_img[:, :, cch]
                            )
                    else:
                        lap_mask = np.array(
                            [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float32
                        )
                        for cch in range(3):
                            mod_in_img[:, :, cch] = cv.filter2D(
                                src=in_img[:, :, cch], ddepth=cv.CV_32F, kernel=lap_mask
                            )
                            mod_in_img[:, :, cch] = np.abs(
                                in_img[:, :, cch] + mod_in_img[:, :, cch]
                            )

                    out_img = np.uint8(np.clip(mod_in_img, 0, 255))

                # unsharp_mask
                elif process_type == "unsharp_mask":
                    im_blurred = cv.GaussianBlur(
                        in_img, ksize=(0, 0), sigmaX=in_sharpen_spread
                    )
                    in_img_pow = 1.0 + in_sharpen_power
                    blur_img_pow = -in_sharpen_power
                    const_add = 0

                    out_img = cv.addWeighted(
                        in_img, in_img_pow, im_blurred, blur_img_pow, const_add
                    )

                t_en_process = time.time()
                self.last_processing_time += t_en_process - t_st_process

                # ✅ Paste ROI back before saving
                if par_process_flag and original_img is not None:
                    original_img[par_st_row:par_en_row, par_st_col:par_en_col] = out_img
                    out_img = original_img

                t_st_write = time.time()

                cv.imwrite(os.path.join(out_img_path, f_name_list[f_i_cnt]), out_img)
                t_en_write = time.time()
                self.last_writing_time += t_en_write - t_st_write

        t_en = time.time()
        self.last_overall_time = t_en - t_st


# In[4]:


# im_cp = sharpen_process()


# # In[6]:


# in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]


# # In[8]:


# im_cp.mod_sharpen(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "laplacian_sharpen",
#             in_lap_method = 'mild',
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[12]:


# im_cp.mod_sharpen(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "unsharp_mask",
#             in_sharpen_spread = 5.0,
#             in_sharpen_power = 0.5,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[ ]:
