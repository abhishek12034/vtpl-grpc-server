#!/usr/bin/env python
# coding: utf-8

# In[33]:


import os
import time
from os import walk
import copy
import math
import numpy as np
import cv2 as cv
from vidstab.VidStab import VidStab
import matplotlib.pyplot as plt


class deblurring_process:
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

        self.in_param += (
            "\n\t <process_type> = motion_deblurring - deblurring filter for motion"
        )
        self.in_param += (
            "\n\t\t <in_angle> = 0 to 180 --> deblurring direction default 90"
        )
        self.in_param += "\n\t\t <in_spread_distance> = 1 to 50 default 10"
        self.in_param += "\n\t\t <in_snr> = 1 to 50 default 25"

        self.in_param += (
            "\n\t <process_type> = optical_deblurring - deblurring filter for motion"
        )
        self.in_param += "\n\t\t <in_spread_distance> = 1 to 50 default 10"
        self.in_param += "\n\t\t <in_snr> = 1 to 50 default 25"

    def blur_edge(self, img, d=31):
        h, w = img.shape[:2]
        img_pad = cv.copyMakeBorder(img, d, d, d, d, cv.BORDER_WRAP)
        img_blur = cv.GaussianBlur(img_pad, (2 * d + 1, 2 * d + 1), -1)[d:-d, d:-d]
        y, x = np.indices((h, w))
        dist = np.dstack([x, w - x - 1, y, h - y - 1]).min(-1)
        w = np.minimum(np.float32(dist) / d, 1.0)
        return img * w + img_blur * (1 - w)

    def motion_kernel(self, angle, d, sz=65):
        kern = np.ones((1, d), np.float32)
        c, s = np.cos(angle), np.sin(angle)
        A = np.float32([[c, -s, 0], [s, c, 0]])
        sz2 = sz // 2
        A[:, 2] = (sz2, sz2) - np.dot(A[:, :2], ((d - 1) * 0.5, 0))
        kern = cv.warpAffine(kern, A, (sz, sz), flags=cv.INTER_CUBIC)
        return kern

    def defocus_kernel(self, d, sz=65):
        kern = np.zeros((sz, sz), np.uint8)
        cv.circle(kern, (sz, sz), d, 255, -1, cv.LINE_AA, shift=1)
        kern = np.float32(kern) / 255.0
        return kern

    def mod_deblurring(
        self,
        in_img_path="",
        curve_name="",
        write_plot_fig_file="",
        process_all_flag=False,
        in_img_list=[],
        process_type="",
        in_angle=90,
        in_spread_distance=10,
        in_snr=25,
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

                    # ✅ Ensure crop coordinates are within image bounds
                    h, w = in_img.shape[:2]
                    par_st_row = max(0, min(par_st_row, h-1))
                    par_en_row = max(0, min(par_en_row, h))
                    par_st_col = max(0, min(par_st_col, w-1))
                    par_en_col = max(0, min(par_en_col, w))

                    # Save original image and crop the ROI
                    original_img = in_img.copy()
                    in_img = in_img[par_st_row:par_en_row, par_st_col:par_en_col]
                else:
                    original_img = None

                # motion_deblurring
                if process_type == "motion_deblurring":
                    kernel_size = 100
                    edge_blur_amt = 31
                    deblur_flag = True

                    out_img = copy.deepcopy(in_img)
                    in_img = np.float32(in_img) / 255.0

                    ang = np.deg2rad(in_angle)
                    dist = in_spread_distance
                    noise = 10 ** (-0.1 * in_snr)

                    psf = self.motion_kernel(ang, dist, sz=kernel_size)

                    # ✅ Avoid division by zero
                    psf_sum = psf.sum()
                    if psf_sum > 0:
                        psf /= psf_sum
                    # ✅ Ensure kh, kw don't exceed psf_pad dimensions (handle small images)
                    kh, kw = psf.shape
                    psf_pad = np.zeros_like(in_img[:, :, 0])
                    kh_safe = min(kh, psf_pad.shape[0])
                    kw_safe = min(kw, psf_pad.shape[1])
                    psf_pad[:kh_safe, :kw_safe] = psf[:kh_safe, :kw_safe]
                    
                    PSF = cv.dft(psf_pad, flags=cv.DFT_COMPLEX_OUTPUT, nonzeroRows=kh_safe)

                    if deblur_flag:
                        PSF2 = (PSF**2).sum(-1)
                        iPSF = PSF / (PSF2 + noise)[..., np.newaxis]
                    else:
                        iPSF = PSF

                    for i_plane in range(3):
                        img = self.blur_edge(in_img[:, :, i_plane], d=edge_blur_amt)
                        IMG = cv.dft(img, flags=cv.DFT_COMPLEX_OUTPUT)

                        RES = cv.mulSpectrums(IMG, iPSF, 0)

                        res = cv.idft(RES, flags=cv.DFT_SCALE | cv.DFT_REAL_OUTPUT)
                        res = np.roll(res, -kh // 2, 0)
                        res = np.roll(res, -kw // 2, 1)

                        res *= 255
                        res = np.clip(res, 0, 255)
                        res = res.astype(np.uint8)

                        out_img[:, :, i_plane] = res

                # optical_deblurring
                if process_type == "optical_deblurring":
                    kernel_size = 100
                    edge_blur_amt = 31
                    deblur_flag = True

                    out_img = copy.deepcopy(in_img)
                    in_img = np.float32(in_img) / 255.0

                    ang = np.deg2rad(in_angle)
                    dist = in_spread_distance
                    noise = 10 ** (-0.1 * in_snr)

                    psf = self.defocus_kernel(dist, sz=kernel_size)

                    # ✅ Avoid division by zero
                    psf_sum = psf.sum()
                    if psf_sum > 0:
                        psf /= psf_sum
                    # ✅ Ensure kh, kw don't exceed psf_pad dimensions (handle small images)
                    kh, kw = psf.shape
                    psf_pad = np.zeros_like(in_img[:, :, 0])
                    kh_safe = min(kh, psf_pad.shape[0])
                    kw_safe = min(kw, psf_pad.shape[1])
                    psf_pad[:kh_safe, :kw_safe] = psf[:kh_safe, :kw_safe]
                    
                    PSF = cv.dft(psf_pad, flags=cv.DFT_COMPLEX_OUTPUT, nonzeroRows=kh_safe)

                    if deblur_flag:
                        PSF2 = (PSF**2).sum(-1)
                        iPSF = PSF / (PSF2 + noise)[..., np.newaxis]
                    else:
                        iPSF = PSF

                    for i_plane in range(3):
                        img = self.blur_edge(in_img[:, :, i_plane], d=edge_blur_amt)
                        IMG = cv.dft(img, flags=cv.DFT_COMPLEX_OUTPUT)

                        RES = cv.mulSpectrums(IMG, iPSF, 0)

                        res = cv.idft(RES, flags=cv.DFT_SCALE | cv.DFT_REAL_OUTPUT)
                        res = np.roll(res, -kh // 2, 0)
                        res = np.roll(res, -kw // 2, 1)

                        res *= 255
                        res = np.clip(res, 0, 255)
                        res = res.astype(np.uint8)

                        out_img[:, :, i_plane] = res

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


# In[35]:


# im_cp = deblurring_process()


# In[37]:


# in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]


# In[39]:


# im_cp.mod_deblurring(
#     in_img_path="D:/MyData/Test_Set_01/lp_motion_2/",
#     process_all_flag=True,
#     # in_img_list = in_list,
#     process_type="motion_deblutting",
#     in_angle=135,
#     in_spread_distance=22,
#     in_snr=25,
#     out_img_path="D:/MyData/Test_Set_01/lp_motion_3/",
# )

# print(
#     f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s"
# )


# In[41]:


# im_cp.mod_deblurring(in_img_path = "D:/MyData/Test_Set_01/txt_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "optical_deblurring",
#             in_spread_distance = 19,
#             in_snr = 25,
#             out_img_path = "D:/MyData/Test_Set_01/txt_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[ ]:
