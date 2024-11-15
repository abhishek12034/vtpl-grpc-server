#!/usr/bin/env python
# coding: utf-8

# In[51]:


import os
import time
from os import walk
import copy
import math
import numpy as np
import cv2 as cv
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt


class edit_process:
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

        self.in_param += "\n\t <process_type> = crop - creates cropped image"
        self.in_param += "\n\t\t <in_st_row> = top position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_en_row> = bottom position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_st_col> = left position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_en_col> = right position --> range 0 - max_row"

        self.in_param += (
            "\n\t <process_type> = flip - flip image horizontally or vertically"
        )
        self.in_param += "\n\t\t <in_flip_hori_true_vert_false> = Flag True/False --> True is horizontal, False Vertical"

        self.in_param += "\n\t <process_type> = rotate - rotate image"
        self.in_param += (
            "\n\t\t <in_rotate_deg> = Angle in degree --> -180 degree to +180 degree"
        )

        self.in_param += "\n\t <process_type> = rezise - creates cropped image"
        self.in_param += "\n\t\t <in_st_row> = top position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_en_row> = bottom position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_st_col> = left position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_en_col> = right position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_keep_same_selection_size> True/False --> If True then keep same as selection otherwise "
        self.in_param += "\n\t\t                               if False then selects the best possible resize image"

        self.in_param += "\n\t <process_type> = smart_rezise - creates cropped image"
        self.in_param += (
            "\n\t\t <model_folder_path> = path where edit model files are present"
        )
        self.in_param += "\n\t\t <in_st_row> = top position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_en_row> = bottom position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_st_col> = left position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_en_col> = right position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_scale_fact> 0 - 20 --> Sclae the image in that range. 1 is same, < 1 downscale > 1 upscale"

        self.in_param += "\n\t <process_type> = perspective - creates cropped image"
        self.in_param += "\n\t\t <in_select_rc_arr> True/False --> 4 set of [row, columns] of 4 selected corners of the quadrilateral "
        self.in_param += "\n\t\t                               as an example [[200, 0], [300, 0], [0, 512], [512, 512]]"

        self.in_param += (
            "\n\t <process_type> = undistort - undistorts to correct an image"
        )
        self.in_param += "\n\t\t <in_distortion_power> value between -1 to +1 --> 0 means same, 0 to 1 is for barrel distortion and "
        self.in_param += (
            "\n\t\t                               0 to -1 is for pin-cushion distortion"
        )

        self.in_param += "\n\t <process_type> = correct_aspect_ratio - correct aspect ration of an image"
        self.in_param += "\n\t\t <in_aspect_ratio_times> value between 0.01 to 10 --> 1 means same --> 1 to 10 to reduce rows "
        self.in_param += (
            "\n\t\t                               1 to 0.01 to reduce columns"
        )

        self.in_param += "\n\t <process_type> = correct_fisheye - correct fiseye distortion of an image"
        self.in_param += "\n\t\t <in_distortion_power> value between 0 to 1 --> 0 means same, 1 means maximum correction in fisheye"

    def dist_from_ori(self, point):
        return math.sqrt(point[0] ** 2 + point[1] ** 2)

    def ang_from_ori(self, pivot, point):
        dx = point[0] - pivot[0]
        dy = point[1] - pivot[1]
        return math.atan2(dy, dx)

    def mod_edit(
        self,
        in_img_path="",
        model_folder_path="",
        process_all_flag=False,
        in_img_list=[],
        process_type="",
        in_st_row=0,
        in_en_row=1,
        in_st_col=0,
        in_en_col=1,
        in_flip_hori_true_vert_false=True,
        in_rotate_deg=0.0,
        in_keep_same_selection_size=False,
        in_scale_fact=1.0,
        in_select_rc_arr=[[0, 0], [1, 0], [1, 1], [0, 1]],
        in_distortion_power=0.0,
        in_aspect_ratio_times=1.0,
        out_img_path="",
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

                # crop
                if process_type == "crop":
                    out_img = copy.deepcopy(
                        in_img[
                            in_st_row : (in_en_row + 1), in_st_col : (in_en_col + 1), :
                        ]
                    )

                # flip
                elif process_type == "flip":
                    if in_flip_hori_true_vert_false:
                        out_img = copy.deepcopy(cv.flip(in_img, 1))
                    else:
                        out_img = copy.deepcopy(cv.flip(in_img, 0))

                # rotate
                elif process_type == "rotate":
                    (im_row, im_col) = in_img.shape[:2]
                    cen_row = im_row / 2
                    cen_col = im_col / 2

                    rot_mat = cv.getRotationMatrix2D(
                        (cen_col, cen_row), in_rotate_deg, 1.0
                    )

                    abs_cos = abs(rot_mat[0, 0])
                    abs_sin = abs(rot_mat[0, 1])

                    bound_col = int(im_row * abs_sin + im_col * abs_cos + 0.5) + 1
                    bound_row = int(im_row * abs_cos + im_col * abs_sin + 0.5) + 1

                    rot_mat[0, 2] += (
                        (im_row * abs_sin + im_col * abs_cos) / 2 - cen_col + 1
                    )
                    rot_mat[1, 2] += (im_row * abs_cos + im_col * abs_sin) / 2 - cen_row

                    out_img = cv.warpAffine(in_img, rot_mat, (bound_col, bound_row))

                # resize
                elif process_type == "resize":
                    sub_st_row = in_st_row
                    sub_en_row = in_en_row
                    sub_st_col = in_st_col
                    sub_en_col = in_en_col

                    sub_row = sub_en_row - sub_st_row + 1
                    sub_col = sub_en_col - sub_st_col + 1

                    (im_row, im_col) = in_img.shape[:2]

                    sub_ht = sub_en_row - sub_st_row
                    sub_wd = sub_en_col - sub_st_col

                    in_sub_cen_row = (in_st_row + in_en_row) / 2
                    in_sub_cen_col = (in_st_col + in_en_col) / 2

                    in_sub_cen_row_int = int(in_sub_cen_row)
                    in_sub_cen_col_int = int(in_sub_cen_col)

                    rat_ht = im_row / sub_ht
                    rat_wd = im_col / sub_wd

                    out_im_row = im_row
                    out_im_col = im_col

                    if not in_keep_same_selection_size:
                        if rat_ht <= rat_wd:
                            sub_half_col = int(((im_col / rat_ht) / 2) + 0.5)
                            sub_col = int((im_col / rat_ht) + 0.5)

                            if (in_sub_cen_col_int - sub_half_col >= 0) and (
                                in_sub_cen_col_int + sub_half_col < im_col
                            ):
                                sub_st_col = in_sub_cen_col_int - sub_half_col
                                sub_en_col = sub_st_col + sub_col
                            elif in_sub_cen_col_int - sub_half_col >= 0:
                                sub_en_col = im_col - 1
                                sub_st_col = sub_en_col - sub_col
                            elif in_sub_cen_col_int + sub_half_col < im_col:
                                sub_st_col = 0
                                sub_en_col = sub_st_col + sub_col
                            else:
                                sub_st_col = 0
                                sub_en_col = sub_st_col + sub_col
                        else:
                            sub_half_row = int(((im_row / rat_wd) / 2) + 0.5)
                            sub_row = int((im_row / rat_wd) + 0.5)

                            if (in_sub_cen_row_int - sub_half_row >= 0) and (
                                in_sub_cen_row_int + sub_half_row < im_row
                            ):
                                sub_st_row = in_sub_cen_row_int - sub_half_row
                                sub_en_row = sub_st_row + sub_row
                            elif in_sub_cen_row_int - sub_half_row >= 0:
                                sub_en_row = im_row - 1
                                sub_st_row = sub_en_row - sub_row
                            elif in_sub_cen_row_int + sub_half_row < im_row:
                                sub_st_row = 0
                                sub_en_row = sub_st_row + sub_row
                            else:
                                sub_st_row = 0
                                sub_en_row = sub_st_row + sub_row

                    else:
                        if rat_ht <= rat_wd:
                            out_im_col = int((im_row / sub_row) * sub_col + 0.5)
                        else:
                            out_im_row = int((im_col / sub_col) * sub_row + 0.5)

                    out_img = cv.resize(
                        in_img[
                            sub_st_row : (sub_en_row + 1),
                            sub_st_col : (sub_en_col + 1),
                            :,
                        ],
                        (out_im_col, out_im_row),
                        interpolation=cv.INTER_LANCZOS4,
                    )

                # smart_resize
                elif process_type == "smart_resize":
                    (im_row, im_col) = in_img.shape[:2]

                    sub_ht = in_en_row - in_st_row + 1
                    sub_wd = in_en_col - in_st_col + 1

                    tar_ht = sub_ht * in_scale_fact
                    tar_wd = sub_wd * in_scale_fact

                    rat_ht = im_row / tar_ht
                    rat_wd = im_col / tar_wd

                    int_conv_flag = False
                    if rat_ht < rat_wd:
                        if rat_ht > 1:
                            tar_ht = im_row
                            tar_wd = int(tar_wd * rat_ht + 0.5)
                            int_conv_flag = True
                    else:
                        if rat_wd > 1:
                            tar_wd = im_col
                            tar_ht = int(tar_ht * rat_wd + 0.5)
                            int_conv_flag = True

                    if not int_conv_flag:
                        tar_ht = int(tar_ht + 0.5)
                        tar_wd = int(tar_wd + 0.5)

                    tar_rat_ht = tar_ht / sub_ht
                    tar_rat_wd = tar_wd / sub_wd

                    tar_rat = max(tar_rat_ht, tar_rat_wd)

                    out_im_row = tar_ht
                    out_im_col = tar_wd

                    part_img = in_img[
                        in_st_row : (in_en_row + 1), in_st_col : (in_en_col + 1), :
                    ]

                    sup_res = cv.dnn_superres.DnnSuperResImpl_create()

                    if tar_rat <= 1:
                        print("Testing at 1 ")
                        out_img = cv.resize(
                            part_img,
                            (out_im_col, out_im_row),
                            interpolation=cv.INTER_NEAREST,
                        )
                    elif tar_rat <= 2:
                        print("Testing at 2 ")

                        model_path = os.path.join(
                            model_folder_path, "sup_res_ESPCN_x2.pb"
                        )
                        sup_res.readModel(model_path)
                        sup_res.setModel("espcn", 2)
                        up_res_img = sup_res.upsample(part_img)
                        out_img = cv.resize(
                            up_res_img,
                            (out_im_col, out_im_row),
                            interpolation=cv.INTER_NEAREST,
                        )
                    elif tar_rat <= 3:
                        print("Testing at 3 ")

                        model_path = os.path.join(
                            model_folder_path, "sup_res_ESPCN_x3.pb"
                        )
                        sup_res.readModel(model_path)
                        sup_res.setModel("espcn", 3)
                        up_res_img = sup_res.upsample(part_img)
                        out_img = cv.resize(
                            up_res_img,
                            (out_im_col, out_im_row),
                            interpolation=cv.INTER_NEAREST,
                        )
                    elif tar_rat <= 4:
                        print("Testing at 4 ")

                        model_path = os.path.join(
                            model_folder_path, "sup_res_ESPCN_x4.pb"
                        )
                        print("Model pATH")
                        print(model_path)
                        sup_res.readModel(model_path)
                        sup_res.setModel("espcn", 4)
                        up_res_img = sup_res.upsample(part_img)
                        out_img = cv.resize(
                            up_res_img,
                            (out_im_col, out_im_row),
                            interpolation=cv.INTER_NEAREST,
                        )
                    else:
                        print("Testing 4-1")
                        model_path = os.path.join(
                            model_folder_path, "sup_res_ESPCN_x4.pb"
                        )
                        sup_res.readModel(model_path)
                        sup_res.setModel("espcn", 4)
                        up_res_img = sup_res.upsample(part_img)
                        out_img = cv.resize(
                            up_res_img,
                            (out_im_col, out_im_row),
                            interpolation=cv.INTER_CUBIC,
                        )

                # perspective
                elif process_type == "perspective":
                    trans_in_cr_arr = (np.array(in_select_rc_arr)[:, [1, 0]]).tolist()

                    top_left_pt = min(trans_in_cr_arr, key=self.dist_from_ori)
                    rem_pts = [p for p in trans_in_cr_arr if p != top_left_pt]
                    clockwise_pts = sorted(
                        rem_pts, key=lambda p: self.ang_from_ori(top_left_pt, p)
                    )

                    trans_select_cr_arr = [top_left_pt] + clockwise_pts

                    (im_row, im_col) = in_img.shape[:2]

                    set_tar_cr_arr = [
                        [0, 0],
                        [im_col, 0],
                        [im_col, im_row],
                        [0, im_row],
                    ]

                    sel_cr_arr = np.array(trans_select_cr_arr, dtype="float32")
                    tar_cr_arr = np.array(set_tar_cr_arr, dtype="float32")

                    trans_mat = cv.getPerspectiveTransform(
                        sel_cr_arr, tar_cr_arr, solveMethod=cv.DECOMP_LU
                    )

                    out_img = cv.warpPerspective(in_img, trans_mat, (im_col, im_row))

                # undistort
                elif process_type == "undistort":
                    h, w = in_img.shape[:2]

                    out_img = np.zeros_like(in_img)

                    cx, cy = w // 2, h // 2

                    y_indices, x_indices = np.indices((h, w))

                    dx = (x_indices - cx) / float(cx)
                    dy = (y_indices - cy) / float(cy)

                    r2 = dx**2 + dy**2
                    factor = 1 + in_distortion_power * r2
                    factor = np.where(factor != 0, factor, 1)

                    dx /= factor
                    dy /= factor

                    x = np.clip(np.round(cx + dx * cx).astype(int), 0, w - 1)
                    y = np.clip(np.round(cy + dy * cy).astype(int), 0, h - 1)

                    out_img[y_indices, x_indices] = in_img[y, x]

                # correct_aspect_ratio
                elif process_type == "correct_aspect_ratio":
                    (im_row, im_col) = in_img.shape[:2]

                    if in_aspect_ratio_times > 1:
                        out_im_row = int(im_row / in_aspect_ratio_times + 0.5)
                        out_im_col = im_col
                        out_img = cv.resize(
                            in_img,
                            (out_im_col, out_im_row),
                            interpolation=cv.INTER_NEAREST,
                        )
                    elif in_aspect_ratio_times < 1 and in_aspect_ratio_times >= 0.01:
                        out_im_row = im_row
                        out_im_col = int(im_col * in_aspect_ratio_times + 0.5)
                        out_img = cv.resize(
                            in_img,
                            (out_im_col, out_im_row),
                            interpolation=cv.INTER_NEAREST,
                        )
                    else:
                        out_img = copy.deepcopy(in_img)

                # correct_fisheye
                elif process_type == "correct_fisheye":
                    pi = math.pi
                    two_pi = 2 * pi
                    three_pi_by_two = 1.5 * pi
                    pi_by_two = 0.5 * pi

                    h, w = in_img.shape[:2]

                    cx, cy = w // 2, h // 2

                    out_img = np.zeros_like(in_img)

                    y, x = np.indices((h, w))

                    dx = x - cx
                    dy = y - cy

                    theta = np.arctan2(dy, dx) % two_pi

                    radius = np.sqrt(dx**2 + dy**2)

                    corner_ang = math.atan(cy / cx)
                    pi_minus_corner_ang = pi - corner_ang
                    pi_plus_corner_ang = pi + corner_ang
                    tow_pi_minus_corner_ang = two_pi - corner_ang

                    fact = np.zeros_like(radius)

                    mask1 = (theta <= corner_ang) | (theta > tow_pi_minus_corner_ang)
                    mask2 = (theta > corner_ang) & (theta <= pi_minus_corner_ang)
                    mask3 = (theta > pi_minus_corner_ang) & (
                        theta <= pi_plus_corner_ang
                    )
                    mask4 = (theta > pi_plus_corner_ang) & (
                        theta <= tow_pi_minus_corner_ang
                    )

                    fact[mask1] = (radius[mask1] * np.abs(np.cos(theta[mask1]))) / cx
                    fact[mask2] = (radius[mask2] * np.abs(np.sin(theta[mask2]))) / cy
                    fact[mask3] = (radius[mask3] * np.abs(np.cos(theta[mask3]))) / cx
                    fact[mask4] = (radius[mask4] * np.abs(np.sin(theta[mask4]))) / cy

                    mod_fact = 1 + (fact - 1) * in_distortion_power

                    x_tar = (dx * mod_fact + cx).astype(int)
                    y_tar = (dy * mod_fact + cy).astype(int)

                    x_tar = np.clip(x_tar, 0, w - 1)
                    y_tar = np.clip(y_tar, 0, h - 1)

                    out_img[y, x] = in_img[y_tar, x_tar]

                t_en_process = time.time()
                self.last_processing_time += t_en_process - t_st_process

                t_st_write = time.time()

                cv.imwrite(os.path.join(out_img_path, f_name_list[f_i_cnt]), out_img)
                t_en_write = time.time()
                self.last_writing_time += t_en_write - t_st_write

        t_en = time.time()
        self.last_overall_time = t_en - t_st


# # In[53]:


# im_cp = edit_process()


# # In[55]:


# in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]


# # In[7]:


# im_cp.mod_edit(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "crop",
#             in_st_row = 10,
#             in_en_row = 100,
#             in_st_col = 20,
#             in_en_col = 200,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[9]:


# im_cp.mod_edit(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "flip",
#             in_flip_hori_true_vert_false = True,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[11]:


# im_cp.mod_edit(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "rotate",
#             in_rotate_deg = -45.0,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[13]:


# im_cp.mod_edit(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "resize",
#             in_st_row = 100,
#             in_en_row = 300,
#             in_st_col = 200,
#             in_en_col = 500,
#             in_keep_same_selection_size = True,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[57]:


# im_cp.mod_edit(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             model_folder_path = "C:/Users/vadmin/Documents/MyData/edit_model_bank",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "smart_resize",
#             in_st_row = 100,
#             in_en_row = 400,
#             in_st_col = 100,
#             in_en_col = 500,
#             in_scale_fact = 4.0,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[17]:


# im_cp.mod_edit(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "perspective",
#             in_select_rc_arr = [[200, 0], [300, 0], [0, 512], [512, 512]],
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[21]:


# im_cp.mod_edit(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "undistort",
#             in_distortion_power = 0.1,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[23]:


# im_cp.mod_edit(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "correct_aspect_ratio",
#             in_aspect_ratio_times = 2,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[25]:


# im_cp.mod_edit(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "correct_fisheye",
#             in_distortion_power = 0.11,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[ ]:
