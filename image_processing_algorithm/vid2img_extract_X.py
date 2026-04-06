#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
import time
from os import walk
import copy
import numpy as np
import cv2 as cv
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt


class extract_process:
    def __init__(self):
        self.jpg_quality = [
            int(cv.IMWRITE_JPEG_QUALITY),
            int(os.getenv("JPEG_QUALITY", 100)),
        ]
        self.last_overall_time = 0
        self.last_processing_time = 0
        self.last_reading_time = 0
        self.last_writing_time = 0
        self.last_functional_processing_time = 0
        self.processing_image_cnt = 0

        self.in_out_type = ""
        self.in_param = ""
        self.p_mat = []
        self.th_name = ["OTSU", "triangle", "manual"]
        self.ad_th_name = ["adaptive_mean", "adaptive_gaussian"]
        self.assign_default()

    def assign_default(self):
        self.in_out_type = "cv2"
        self.in_param = "Input-"
        self.in_param += "\n <in_img_path> path of the image folder"
        self.in_param += "\n <process_all_flag> If true the process for all the files"
        self.in_param += "\n <in_img_list> list of the images image folder"
        self.in_param += "\n <process_type> is to set what processing is required"

        self.in_param += "\n\t <process_type> = negative - creates negative image"

        self.in_param += (
            "\n\t <process_type> = threshold - threshold image on a given level"
        )
        self.in_param += (
            "\n\t\t <threshold_option >= 'OTSU', 'triangle', 'manual'--> threshold type"
        )
        self.in_param += "\n\t\t <threshold_level> = >= 0 to 1 --> applicable only to 'manual'; 0 means all white and 1 means all black"

        self.in_param += "\n\t <process_type> = adaptive_threshold - threshold image using different techniques and controls"
        self.in_param += "\n\t\t <adaptive_threshold_option> >= 'adaptive_mean', 'adaptive_gaussian' --> threshold type"
        self.in_param += "\n\t\t <ad_th_box_len> = 1 to 11 --> default 3, this will determine the size of the mask "
        self.in_param += "\n\t\t <ad_th_edge_reducer> = 1 to 11 --> default 3, this will control the edge density"

        self.in_param += "\n\t <process_type> = Laplace - Laplace edge detection"
        self.in_param += (
            "\n\t\t <in_kernal_size> = 3, 5, 7, 9, 11 --> size of the kernal"
        )

        self.in_param += "\n\t <process_type> = Prewitt - Prewitt edge detection"

        self.in_param += "\n\t <process_type> = Sobel - Sobel edge detection"
        self.in_param += "\n\t\t <in_kernal_size> = 1, 3, 5, 7 --> size of the kernal"

        self.in_param += "\n\t <process_type> = Scharr - Scharr edge detection"

        self.in_param += "\n\t <process_type> = Canny - Canny edge detection"
        self.in_param += "\n\t\t <in_rejection_upper_level> = 0 to 1 --> 0 means less rejection and 1 means more rejection"
        self.in_param += "\n\t\t <in_inclusion_lower_level> = 0 to 1 --> 0 means more inclusion and 1 means less inclusion"
        self.in_param += "\n\t\t <in_rejection_upper_level> should be less '<' than <in_inclusion_lower_level>"

        self.in_param += "\n\t <process_type> = linear_filter - linear_filter operation"
        self.in_param += "\n\t\t <in_kernal_1> = LIKE [1,0,-1] OR LIKE [[1],[0],[-1]] --> kernal array"
        self.in_param += "\n\t\t <in_filter_display_mode> = 'Absolute', 'Exact_Value' --> Absolute is default, Exact_Value will be grey"

        self.in_param += (
            "\n\t <process_type> = bilinear_filter - bi linear_filter operation"
        )
        self.in_param += "\n\t\t <in_kernal_1> = LIKE [1,0,-1] OR LIKE [[1],[0],[-1]] --> kernal array"
        self.in_param += "\n\t\t <in_kernal_2> = LIKE [1,0,-1] OR LIKE [[1],[0],[-1]] --> kernal array"

        self.in_param += (
            "\n\t <process_type> = channel_selector - color channel selection"
        )
        self.in_param += "\n\t\t <in_color_intensity_selection> = 'Auto', 'Manual' --> Auto is default, Manual needs in_manual_color_level"
        self.in_param += "\n\t\t <in_manual_color_level> = 0 - 1 --> default is 0.2, will only be active if in_color_intensity_selection = Manual"
        self.in_param += (
            "\n\t\t <in_mid_color_val> = 0 - 360 --> Hue value in 360 degree"
        )
        self.in_param += "\n\t\t <in_spread_color> = 0 - 1 --> spread of the hue 0 means 0, 1 means 360, default 0.3"

        self.in_param += (
            "\n\t <process_type> = channel_demux - color channel demultiplexer"
        )
        self.in_param += "\n\t\t <in_select_dual_pt_rc_list> selected points e.g.'[[293, 262], [234, 436]]' --> [row, col]. Max 2pt. repeat if 1pt"
        self.in_param += "\n\t\t <in_bg_rc_pt> = '[151, 647]' --> [row, col] background color point which will be placed in replacement"
        self.in_param += "\n\t\t <in_filter_pass_true_block_false_flag> --> True if has to selected, False if has to be removed"
        self.in_param += "\n\t\t <in_filter_power> = 0 - 1 --> 0 means minimum demux power of filter 1 means maximum power, 0.5 is default"

        self.in_param += "\n\t <process_type> = fourier -periodic noise cleaner"
        self.in_param += "\n\t\t <in_period_closeness> = 0 - 1 --> 0 means remove more frequent noise 1 means less frequent, 0.5 is default"
        self.in_param += "\n\t\t <in_clarity_strength> = 0 - 1 --> 1 means more sharper and 0 means more blur, 0.5 is default"

    def mod_extract(
        self,
        in_img_path="",
        curve_name="",
        write_plot_fig_file="",
        process_all_flag=False,
        in_img_list=[],
        process_type="",
        threshold_option="",
        threshold_level=0.5,
        adaptive_threshold_option="",
        ad_th_box_len=3,
        ad_th_edge_reducer=3,
        in_kernal_size=3,
        in_rejection_upper_level=0.25,
        in_inclusion_lower_level=0.75,
        in_kernal_1=[1, 0, -1],
        in_kernal_2=[[1], [0], [-1]],
        in_filter_display_mode="Absolute",
        in_color_intensity_selection="Auto",
        in_manual_color_level=0.2,
        in_mid_color_val=15,
        in_spread_color=0.2,
        in_select_dual_pt_rc_list=[[293, 262], [234, 436]],
        in_bg_rc_pt=[151, 647],
        in_filter_pass_true_block_false_flag=True,
        in_filter_power=0.5,
        in_period_closeness=0.5,
        in_clarity_strength=0.5,
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

                # negative
                if process_type == "negative":
                    out_img = copy.deepcopy(in_img)
                    out_img = 255 - out_img

                # threshold
                elif process_type == "threshold":
                    out_img = copy.deepcopy(in_img)
                    for cch in range(3):
                        if threshold_option == "manual":
                            threshold_val = int(threshold_level * 255 + 0.499)
                            out_img[:, :, cch][
                                out_img[:, :, cch] >= threshold_val
                            ] = 255
                            out_img[:, :, cch][out_img[:, :, cch] < threshold_val] = 0
                        elif threshold_option == "OTSU":
                            ret_th_val, out_img[:, :, cch] = cv.threshold(
                                in_img[:, :, cch],
                                thresh=0,
                                maxval=255,
                                type=cv.THRESH_OTSU,
                            )
                        elif threshold_option == "triangle":
                            ret_th_val, out_img[:, :, cch] = cv.threshold(
                                in_img[:, :, cch],
                                thresh=0,
                                maxval=255,
                                type=cv.THRESH_TRIANGLE,
                            )

                # adaptive_threshold     'adaptive_mean', 'adaptive_gaussian'
                elif process_type == "adaptive_threshold":
                    if adaptive_threshold_option in self.ad_th_name:
                        out_img = copy.deepcopy(in_img)

                        if adaptive_threshold_option == "adaptive_mean":
                            in_adaptiveMethod = cv.ADAPTIVE_THRESH_MEAN_C
                        elif adaptive_threshold_option == "adaptive_gaussian":
                            in_adaptiveMethod = cv.ADAPTIVE_THRESH_GAUSSIAN_C
                        else:
                            in_adaptiveMethod = cv.ADAPTIVE_THRESH_MEAN_C

                        for cch in range(3):
                            out_img[:, :, cch] = cv.adaptiveThreshold(
                                src=in_img[:, :, cch],
                                maxValue=255,
                                adaptiveMethod=in_adaptiveMethod,
                                thresholdType=cv.THRESH_BINARY,
                                blockSize=ad_th_box_len,
                                C=ad_th_edge_reducer,
                            )

                # Laplace
                elif process_type == "Laplace":
                    out_img = copy.deepcopy(in_img)
                    out_img = out_img.astype(np.float32)

                    for cch in range(3):
                        out_img[:, :, cch] = cv.Laplacian(
                            src=in_img[:, :, cch],
                            ddepth=cv.CV_32F,
                            ksize=in_kernal_size,
                            borderType=cv.BORDER_REPLICATE,
                        )

                        out_img[:, :, cch] = out_img[:, :, cch] * -1
                        out_img[:, :, cch][out_img[:, :, cch] < 0] = 0

                        max_val = out_img.max()
                        max_val = 1 if max_val < 1 else max_val
                        mul_factor = 255 / max_val

                        out_img[:, :, cch] = out_img[:, :, cch] * mul_factor

                    out_img = out_img.astype(np.uint8)

                # Prewitt
                elif process_type == "Prewitt":
                    kernel_1 = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])
                    kernel_2 = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])

                    out_img = copy.deepcopy(in_img)
                    for cch in range(3):
                        grad_x = cv.filter2D(
                            src=in_img[:, :, cch], ddepth=cv.CV_32F, kernel=kernel_1
                        )
                        grad_y = cv.filter2D(
                            src=in_img[:, :, cch], ddepth=cv.CV_32F, kernel=kernel_2
                        )

                        grad_x = grad_x * grad_x
                        grad_y = grad_y * grad_y

                        grad_x_y = grad_x + grad_y
                        grad_x_y = np.power(grad_x_y, 0.5)

                        max_val_x_y = grad_x_y.max()
                        max_val_x_y = 1 if max_val_x_y < 1 else max_val_x_y
                        mul_factor_x_y = 255 / max_val_x_y
                        grad_x_y = grad_x_y * mul_factor_x_y

                        out_img[:, :, cch] = grad_x_y

                    out_img = out_img.astype(np.uint8)

                # Sobel
                elif process_type == "Sobel":
                    out_img = copy.deepcopy(in_img)
                    for cch in range(3):
                        grad_x = cv.Sobel(
                            src=in_img[:, :, cch],
                            ddepth=cv.CV_32F,
                            dx=1,
                            dy=0,
                            ksize=in_kernal_size,
                            borderType=cv.BORDER_REPLICATE,
                        )
                        grad_y = cv.Sobel(
                            src=in_img[:, :, cch],
                            ddepth=cv.CV_32F,
                            dx=0,
                            dy=1,
                            ksize=in_kernal_size,
                            borderType=cv.BORDER_REPLICATE,
                        )

                        grad_x = grad_x * grad_x
                        grad_y = grad_y * grad_y

                        grad_x_y = grad_x + grad_y
                        grad_x_y = np.power(grad_x_y, 0.5)

                        max_val_x_y = grad_x_y.max()
                        max_val_x_y = 1 if max_val_x_y < 1 else max_val_x_y
                        mul_factor_x_y = 255 / max_val_x_y
                        grad_x_y = grad_x_y * mul_factor_x_y

                        out_img[:, :, cch] = grad_x_y

                    out_img = out_img.astype(np.uint8)

                # Scharr
                elif process_type == "Scharr":
                    out_img = copy.deepcopy(in_img)
                    for cch in range(3):
                        grad_x = cv.Scharr(
                            src=in_img[:, :, cch],
                            ddepth=cv.CV_32F,
                            dx=1,
                            dy=0,
                            borderType=cv.BORDER_REPLICATE,
                        )
                        grad_y = cv.Scharr(
                            src=in_img[:, :, cch],
                            ddepth=cv.CV_32F,
                            dx=0,
                            dy=1,
                            borderType=cv.BORDER_REPLICATE,
                        )

                        grad_x = grad_x * grad_x
                        grad_y = grad_y * grad_y

                        grad_x_y = grad_x + grad_y
                        grad_x_y = np.power(grad_x_y, 0.5)

                        max_val_x_y = grad_x_y.max()
                        max_val_x_y = 1 if max_val_x_y < 1 else max_val_x_y
                        mul_factor_x_y = 255 / max_val_x_y
                        grad_x_y = grad_x_y * mul_factor_x_y

                        out_img[:, :, cch] = grad_x_y

                    out_img = out_img.astype(np.uint8)

                # Canny
                elif process_type == "Canny":
                    out_img = copy.deepcopy(in_img)

                    rejection_th = in_rejection_upper_level * 255
                    inclusion_th = in_inclusion_lower_level * 255

                    for cch in range(3):
                        out_img[:, :, cch] = cv.Canny(
                            image=in_img[:, :, cch],
                            threshold1=rejection_th,
                            threshold2=inclusion_th,
                            apertureSize=3,
                            L2gradient=False,
                        )

                    out_img = out_img.astype(np.uint8)

                # Linear Filter
                elif process_type == "linear_filter":
                    kernel_1 = np.array(in_kernal_1)

                    out_img = copy.deepcopy(in_img)
                    out_img = out_img.astype(np.float32)

                    for cch in range(3):
                        out_img[:, :, cch] = cv.filter2D(
                            in_img[:, :, cch], ddepth=cv.CV_32F, kernel=kernel_1
                        )

                        if in_filter_display_mode == "Absolute":
                            min_val = out_img[:, :, cch].min()
                            out_img[:, :, cch] -= min_val
                        else:
                            out_img[:, :, cch] = np.absolute(out_img[:, :, cch])

                        max_val_x_y = out_img[:, :, cch].max()
                        max_val_x_y = 1 if max_val_x_y < 1 else max_val_x_y
                        mul_factor_x_y = 255 / max_val_x_y
                        out_img[:, :, cch] = out_img[:, :, cch] * mul_factor_x_y

                    out_img = out_img.astype(np.uint8)

                # Bilinear Filter
                elif process_type == "bilinear_filter":
                    kernel_1 = np.array(in_kernal_1)
                    kernel_2 = np.array(in_kernal_2)

                    out_img = copy.deepcopy(in_img)
                    for cch in range(3):
                        grad_x = cv.filter2D(
                            src=in_img[:, :, cch], ddepth=cv.CV_32F, kernel=kernel_1
                        )
                        grad_y = cv.filter2D(
                            src=in_img[:, :, cch], ddepth=cv.CV_32F, kernel=kernel_2
                        )

                        grad_x = grad_x * grad_x
                        grad_y = grad_y * grad_y

                        grad_x_y = grad_x + grad_y
                        grad_x_y = np.power(grad_x_y, 0.5)

                        max_val_x_y = grad_x_y.max()
                        max_val_x_y = 1 if max_val_x_y < 1 else max_val_x_y
                        mul_factor_x_y = 255 / max_val_x_y
                        grad_x_y = grad_x_y * mul_factor_x_y

                        out_img[:, :, cch] = grad_x_y

                    out_img = out_img.astype(np.uint8)

                # Channel selector
                elif process_type == "channel_selector":
                    mid_hue_val = int(in_mid_color_val / 2)
                    spread_hue = in_spread_color * 180
                    spread_hue = 180 if spread_hue > 180 else spread_hue
                    spread_by_2 = int(spread_hue / 2)

                    if mid_hue_val - spread_by_2 < 0:
                        check_type = 1
                        min_hue_val = mid_hue_val + spread_by_2
                        max_hue_val = (mid_hue_val - spread_by_2 + 180) % 180
                    elif mid_hue_val + spread_by_2 > 180:
                        check_type = 1
                        min_hue_val = mid_hue_val + spread_by_2 - 180
                        max_hue_val = mid_hue_val - spread_by_2
                    else:
                        check_type = 2
                        min_hue_val = int(mid_hue_val - spread_by_2)
                        max_hue_val = int(mid_hue_val + spread_by_2)

                    hsv_img = cv.cvtColor(in_img, cv.COLOR_BGR2HSV)

                    if in_color_intensity_selection == "Auto":
                        otsu_val, temp_mat = cv.threshold(
                            hsv_img[..., 1], thresh=0, maxval=255, type=cv.THRESH_OTSU
                        )
                        traingle_val, temp_mat = cv.threshold(
                            hsv_img[..., 1],
                            thresh=0,
                            maxval=255,
                            type=cv.THRESH_TRIANGLE,
                        )
                        mid_th_val = int((otsu_val + traingle_val) / 2)
                    else:
                        mid_th_val = in_manual_color_level * 255

                    hsv_img[..., 1][hsv_img[..., 1] >= mid_th_val] = 255

                    hsv_img[..., 2][hsv_img[..., 1] < mid_th_val] = 0
                    hsv_img[..., 2][hsv_img[..., 1] >= mid_th_val] = 255

                    hsv_img_1 = copy.deepcopy(hsv_img)
                    if check_type == 1:
                        hsv_img[..., 2][hsv_img[..., 0] > min_hue_val] = 0
                        hsv_img_1[..., 2][hsv_img[..., 0] <= max_hue_val] = 0
                        hsv_img[..., 2] = np.maximum(hsv_img[..., 2], hsv_img_1[..., 2])
                    else:
                        hsv_img[..., 2][hsv_img[..., 0] <= min_hue_val] = 0
                        hsv_img_1[..., 2][hsv_img[..., 0] > max_hue_val] = 0
                        hsv_img[..., 2] = np.minimum(hsv_img[..., 2], hsv_img_1[..., 2])

                    out_img = cv.cvtColor(hsv_img, cv.COLOR_HSV2BGR)

                # Channel demultiplexer
                elif process_type == "channel_demux":
                    match_steep_val = 3
                    match_th = 1 - pow(
                        (1 - pow(in_filter_power, match_steep_val)),
                        (1 / match_steep_val),
                    )

                    hsv_img = cv.cvtColor(in_img, cv.COLOR_BGR2HSV)
                    str_hsv_img = copy.deepcopy(hsv_img)

                    temp_hsv_img = copy.deepcopy(hsv_img)
                    temp_hsv_img = temp_hsv_img.astype(np.float32)
                    wtg_hsv_img = copy.deepcopy(temp_hsv_img)

                    # Use original (full) image for sampling coordinates if ROI is enabled
                    sampling_hsv_img = (
                        cv.cvtColor(original_img, cv.COLOR_BGR2HSV)
                        if par_process_flag and original_img is not None
                        else hsv_img
                    )

                    select_hsv_list = []
                    for i_cnt in range(len(in_select_dual_pt_rc_list)):
                        hsv_val = sampling_hsv_img[
                            in_select_dual_pt_rc_list[i_cnt][0],
                            in_select_dual_pt_rc_list[i_cnt][1],
                        ]
                        select_hsv_list.append(hsv_val)

                    bg_hsv_val = sampling_hsv_img[
                        in_bg_rc_pt[0],
                        in_bg_rc_pt[1],
                    ]

                    hue_imp_ref_list = []
                    stiff_amt = 10
                    shift_amt = 1.5
                    # =ROUND((100/(1+(POWER(stiff_amt, (((((B1/100)-0.5)*10)+shift_amt)*-1))))), 2)
                    for i_cnt in range(256):
                        norm_i_cnt = i_cnt / 2.56
                        val_1 = ((((norm_i_cnt / 100) - 0.5) * 10) + shift_amt) * (-1)
                        val_2 = (100 / (1 + pow(stiff_amt, val_1))) / 100
                        hue_imp_ref_list.append(val_2)

                    mapper = lambda in_s_val: hue_imp_ref_list[in_s_val]
                    s_map_fync = np.vectorize(mapper)
                    wtg_hsv_img[:, :, 2] = s_map_fync(hsv_img[:, :, 2])

                    h_frac = (1 / 180) * 0.9
                    s_frac = (1 / 255) * 0.1
                    v_frac = (1 / 255) * 0.9

                    wtg_hsv_img[:, :, 0] = (
                        (
                            np.minimum(
                                np.minimum(
                                    (
                                        np.maximum(
                                            temp_hsv_img[:, :, 0], select_hsv_list[0][0]
                                        )
                                        - np.minimum(
                                            temp_hsv_img[:, :, 0], select_hsv_list[0][0]
                                        )
                                    ),
                                    (
                                        np.minimum(
                                            temp_hsv_img[:, :, 0], select_hsv_list[0][0]
                                        )
                                        - np.maximum(
                                            temp_hsv_img[:, :, 0], select_hsv_list[0][0]
                                        )
                                        + 180
                                    ),
                                ),
                                np.minimum(
                                    (
                                        np.maximum(
                                            temp_hsv_img[:, :, 0], select_hsv_list[1][0]
                                        )
                                        - np.minimum(
                                            temp_hsv_img[:, :, 0], select_hsv_list[1][0]
                                        )
                                    ),
                                    (
                                        np.minimum(
                                            temp_hsv_img[:, :, 0], select_hsv_list[1][0]
                                        )
                                        - np.maximum(
                                            temp_hsv_img[:, :, 0], select_hsv_list[1][0]
                                        )
                                        + 180
                                    ),
                                ),
                            )
                            * h_frac
                            * wtg_hsv_img[:, :, 2]
                        )
                        + (
                            np.minimum(
                                np.absolute(
                                    temp_hsv_img[:, :, 2] - select_hsv_list[0][2]
                                ),
                                np.absolute(
                                    temp_hsv_img[:, :, 2] - select_hsv_list[1][2]
                                ),
                            )
                            * v_frac
                            * (1 - wtg_hsv_img[:, :, 2])
                        )
                        + (
                            np.minimum(
                                np.absolute(
                                    temp_hsv_img[:, :, 1] - select_hsv_list[0][1]
                                ),
                                np.absolute(
                                    temp_hsv_img[:, :, 1] - select_hsv_list[1][1]
                                ),
                            )
                            * s_frac
                            * wtg_hsv_img[:, :, 2]
                        )
                    )

                    if in_filter_pass_true_block_false_flag:
                        str_hsv_img[:, :, 0] = np.where(
                            wtg_hsv_img[:, :, 0] > match_th,
                            bg_hsv_val[0],
                            str_hsv_img[:, :, 0],
                        )

                        str_hsv_img[:, :, 1] = np.where(
                            wtg_hsv_img[:, :, 0] > match_th,
                            bg_hsv_val[1],
                            str_hsv_img[:, :, 1],
                        )

                        str_hsv_img[:, :, 2] = np.where(
                            wtg_hsv_img[:, :, 0] > match_th,
                            bg_hsv_val[2],
                            str_hsv_img[:, :, 2],
                        )
                    else:
                        str_hsv_img[:, :, 0] = np.where(
                            wtg_hsv_img[:, :, 0] < match_th,
                            bg_hsv_val[0],
                            str_hsv_img[:, :, 0],
                        )

                        str_hsv_img[:, :, 1] = np.where(
                            wtg_hsv_img[:, :, 0] < match_th,
                            bg_hsv_val[1],
                            str_hsv_img[:, :, 1],
                        )

                        str_hsv_img[:, :, 2] = np.where(
                            wtg_hsv_img[:, :, 0] < match_th,
                            bg_hsv_val[2],
                            str_hsv_img[:, :, 2],
                        )

                    out_img = cv.cvtColor(str_hsv_img, cv.COLOR_HSV2BGR)

                # Fourier Filter
                elif process_type == "fourier":
                    out_img = copy.deepcopy(in_img)
                    for p_cnt in range(3):
                        in_img_plane = in_img[:, :, p_cnt]

                        dft = cv.dft(
                            np.float32(in_img_plane), flags=cv.DFT_COMPLEX_OUTPUT
                        )
                        dft_shift = np.fft.fftshift(dft)

                        ini_mag_spec = 20 * np.log(
                            cv.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
                        )

                        ini_mag_norm_val = 255 / ini_mag_spec.max()

                        plot_ini_mag_spec = copy.deepcopy(ini_mag_spec)
                        plot_ini_mag_spec *= ini_mag_norm_val
                        plot_ini_mag_spec = plot_ini_mag_spec.astype(np.uint8)

                        otsu_th, t_mat = cv.threshold(
                            plot_ini_mag_spec, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU
                        )
                        otsu_th *= 1 + ((in_clarity_strength - 0.5) * 1.1)

                        im_row, im_col = in_img_plane.shape
                        im_c_row, im_c_col = im_row // 2, im_col // 2

                        obstruction_period = 20 * in_period_closeness + 2
                        m_gap = int(min(im_row, im_col) / obstruction_period)

                        # create a mask first, center square is 1, remaining all zeros
                        mask = np.ones((im_row, im_col, 2), np.uint8)

                        mask[:, :, 0] = np.where(
                            plot_ini_mag_spec[:, :] > otsu_th, 0, 1
                        )
                        mask[:, :, 1] = np.where(
                            plot_ini_mag_spec[:, :] > otsu_th, 0, 1
                        )
                        mask[
                            im_c_row - m_gap : im_c_row + m_gap,
                            im_c_col - m_gap : im_c_col + m_gap,
                        ] = 1

                        # apply mask and inverse DFT
                        fshift = dft_shift * mask
                        f_ishift = np.fft.ifftshift(fshift)
                        img_back = cv.idft(f_ishift)
                        img_back = cv.magnitude(img_back[:, :, 0], img_back[:, :, 1])

                        back_img_norm_val = 255 / img_back.max()
                        img_back *= back_img_norm_val
                        img_back = img_back.astype(np.uint8)

                        out_img[:, :, p_cnt] = img_back

                        mod_mag_spec_print_flag = False
                        if mod_mag_spec_print_flag:
                            mod_magnitude_spectrum = 20 * np.log(
                                cv.magnitude(fshift[:, :, 0], fshift[:, :, 1])
                            )
                            mod_mag_norm_val = 255 / mod_magnitude_spectrum.max()
                            plot_mod_magnitude_spectrum = copy.deepcopy(
                                mod_magnitude_spectrum
                            )
                            plot_mod_magnitude_spectrum *= mod_mag_norm_val
                            plot_mod_magnitude_spectrum = (
                                plot_mod_magnitude_spectrum.astype(np.uint8)
                            )

                            mask *= 255

                            cv.imshow("zOriginal Image", in_img_plane)
                            cv.imshow("zFourier Image", plot_ini_mag_spec)
                            cv.imshow("zINew Image", img_back)
                            cv.imshow("zImask 1", mask[:, :, 0])
                            cv.imshow("zImask 2", mask[:, :, 1])
                            cv.waitKey()

                t_en_process = time.time()
                self.last_processing_time += t_en_process - t_st_process

                # ✅ Paste ROI back before saving
                if par_process_flag and original_img is not None:
                    original_img[par_st_row:par_en_row, par_st_col:par_en_col] = out_img
                    out_img = original_img

                t_st_write = time.time()

                cv.imwrite(
                    os.path.join(out_img_path, f_name_list[f_i_cnt]),
                    out_img,
                    self.jpg_quality,
                )
                t_en_write = time.time()
                self.last_writing_time += t_en_write - t_st_write

        t_en = time.time()
        self.last_overall_time = t_en - t_st


# In[6]:


# im_cp = extract_process()


# # In[8]:


# in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]


# # In[10]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "negative",
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[12]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "threshold",
#             threshold_option = 'OTSU',
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[14]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "threshold",
#             threshold_option = 'triangle',
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[16]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "threshold",
#             threshold_option = 'manual',
#             threshold_level = 0.5,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[18]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "adaptive_threshold",
#             adaptive_threshold_option = 'adaptive_mean',
#             ad_th_box_len = 3,
#             ad_th_edge_reducer = 3,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[20]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "adaptive_threshold",
#             adaptive_threshold_option = 'adaptive_gaussian',
#             ad_th_box_len = 7,
#             ad_th_edge_reducer = 3,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[22]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "Laplace",
#             in_kernal_size = 7,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[24]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "Prewitt",
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[26]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "Sobel",
#             in_kernal_size = 3,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[28]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "Scharr",
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[30]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "Canny",
#             in_rejection_upper_level = 0.3,
#             in_inclusion_lower_level = 0.7,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[32]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "linear_filter",
#             in_kernal_1 = [1,0,-1],
#             in_filter_display_mode = 'Absolute',
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[34]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "linear_filter",
#             in_kernal_1 = [1,0,-1],
#             in_filter_display_mode = 'Exact_Value',
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[36]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "bilinear_filter",
#             in_kernal_1 = [1,0,-1],
#             in_kernal_2 = [[1],[0],[-1]],
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[38]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "channel_selector",
#             in_color_intensity_selection = 'Auto',
#             in_mid_color_val = 15,
#             in_spread_color = 0.3,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[40]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "channel_selector",
#             in_color_intensity_selection = 'Manual',
#             in_manual_color_level = 0.3,
#             in_mid_color_val = 135,
#             in_spread_color = 0.3,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[42]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "channel_demux",
#             in_select_dual_pt_rc_list = [[293, 262], [234, 436]],
#             in_bg_rc_pt = [151, 647],
#             in_filter_pass_true_block_false_flag = False,
#             in_filter_power = 0.5,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[44]:


# im_cp.mod_extract(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "fourier",
#             in_period_closeness = 0.5,
#             in_clarity_strength = 0.5,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[ ]:
