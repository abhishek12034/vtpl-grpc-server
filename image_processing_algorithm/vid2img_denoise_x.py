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
from numpy.fft import fft2, ifft2
from scipy.signal.windows import gaussian
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt


class denoise_process:
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

        self.in_param += "\n\t <process_type> = averaging - denoising by averaging"
        self.in_param += "\n\t\t <in_filter_size> = Odd numbers 1 to 15 --> 1, 3, 5, 7, 9, 11, 13, 15 default 7"

        self.in_param += (
            "\n\t <process_type> = gaussian_smoothing - denoising by gaussian smoothing"
        )
        self.in_param += "\n\t\t <in_filter_size> = Odd numbers 1 to 15 --> 1, 3, 5, 7, 9, 11, 13, 15 default 7"

        self.in_param += "\n\t <process_type> = bilateral_filtering - denoising by bilateral filtering"
        self.in_param += "\n\t\t <in_filter_size> = Odd numbers 1 to 15 --> 1, 3, 5, 7, 9, 11, 13, 15 default 7"
        self.in_param += "\n\t\t <in_variation_range> = 1 to 1000 --> default 256"

        self.in_param += (
            "\n\t <process_type> = median_filtering - denoising by median filtering"
        )
        self.in_param += "\n\t\t <in_filter_size> = Odd numbers 1 to 15 --> 1, 3, 5, 7, 9, 11, 13, 15 default 5"

        self.in_param += "\n\t <process_type> = wiener - denoising by wiener filtering"
        self.in_param += "\n\t\t <in_filter_size> = Odd numbers 1 to 15 --> 1, 3, 5, 7, 9, 11, 13, 15 default 7"
        self.in_param += "\n\t\t <wiener_power_val> = 1 to 100 --> default 25"

    def mod_denoise(
        self,
        in_img_path="",
        curve_name="",
        write_plot_fig_file="",
        process_all_flag=False,
        in_img_list=[],
        process_type="",
        in_filter_size=5,
        in_variation_range=256,
        wiener_power_val=25,
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
                if process_type == "averaging":
                    mod_img = np.zeros(
                        (in_img.shape[0], in_img.shape[1], 3), dtype=np.float32
                    )
                    out_img = np.zeros(
                        (in_img.shape[0], in_img.shape[1], 3), dtype=np.uint8
                    )

                    # ✅ OpenCV GaussianBlur requires ksize to be odd and > 0
                    fil_len = int(in_filter_size)
                    if fil_len < 1:
                        fil_len = 1
                    elif fil_len % 2 == 0:
                        fil_len += 1
                    
                    kernel_1 = np.ones((fil_len, fil_len), np.float32) / (
                        fil_len * fil_len
                    )

                    for cch in range(3):
                        mod_img[:, :, cch] = cv.filter2D(
                            src=in_img[:, :, cch], ddepth=cv.CV_32F, kernel=kernel_1
                        )

                    mod_img = np.abs(mod_img)
                    out_img = np.uint8(np.clip(mod_img, 0, 255))

                # gaussian_smoothing
                elif process_type == "gaussian_smoothing":
                    # ✅ OpenCV GaussianBlur requires ksize to be odd and > 0
                    fil_len = int(in_filter_size)
                    if fil_len < 1:
                        fil_len = 1
                    elif fil_len % 2 == 0:
                        fil_len += 1

                    out_img = cv.GaussianBlur(
                        in_img, ksize=(fil_len, fil_len), sigmaX=0
                    )

                # gaussian_smoothing
                elif process_type == "bilateral_filtering":
                    out_img = cv.bilateralFilter(
                        in_img,
                        d=in_filter_size,
                        sigmaColor=in_variation_range,
                        sigmaSpace=in_variation_range,
                    )

                # gaussian_smoothing
                elif process_type == "median_filtering":
                    # ✅ OpenCV medianBlur requires ksize to be odd and > 0
                    fil_len = int(in_filter_size)
                    if fil_len < 1:
                        fil_len = 1
                    elif fil_len % 2 == 0:
                        fil_len += 1
                    out_img = cv.medianBlur(in_img, fil_len)

                # gaussian_smoothing
                elif process_type == "wiener":
                    out_img = np.zeros(
                        (in_img.shape[0], in_img.shape[1], 3), dtype=np.uint8
                    )

                    # ✅ Ensure filter size is odd and > 0
                    fil_len = int(in_filter_size)
                    if fil_len < 1:
                        fil_len = 1
                    elif fil_len % 2 == 0:
                        fil_len += 1

                    kernel = gaussian(fil_len, fil_len / 3).reshape(
                        fil_len, 1
                    )
                    kernel = np.dot(kernel, kernel.transpose())
                    kernel /= np.sum(kernel)

                    for cch in range(3):
                        win_kernel = copy.deepcopy(kernel)
                        win_kernel /= np.sum(win_kernel)
                        fft_img = np.copy(in_img[:, :, cch])
                        fft_img = fft2(fft_img)
                        win_kernel = fft2(win_kernel, s=in_img[:, :, cch].shape)
                        win_kernel = np.conj(win_kernel) / (
                            np.abs(win_kernel) ** 2 + wiener_power_val
                        )
                        fft_img = fft_img * win_kernel
                        fft_img = np.abs(ifft2(fft_img))

                        max_val = np.max(fft_img)
                        scale_val = 255 / max_val if max_val > 0 else 1
                        fft_img = fft_img * scale_val
                        out_img[:, :, cch] = np.uint8(np.clip(fft_img, 0, 255))

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


# In[3]:


# im_cp = denoise_process()


# # In[5]:


# in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]


# # In[7]:


# im_cp.mod_denoise(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "averaging",
#             in_filter_size = 9,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[8]:


# im_cp.mod_denoise(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "gaussian_smoothing",
#             in_filter_size = 9,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[9]:


# im_cp.mod_denoise(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "bilateral_filtering",
#             in_filter_size = 9,
#             in_variation_range = 250,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[10]:


# im_cp.mod_denoise(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "median_filtering",
#             in_filter_size = 5,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[11]:


# im_cp.mod_denoise(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "wiener",
#             in_filter_size = 5,
#             wiener_power_val = 40,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[ ]:
