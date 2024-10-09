#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import time
from os import walk
import copy
import numpy as np
import cv2 as cv
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt


class adjust_process:
    def __init__(self):
        self.last_overall_time = 0
        self.last_processing_time = 0
        self.last_reading_time = 0
        self.last_writing_time = 0
        self.last_functional_processing_time = 0
        self.processing_image_cnt = 0
        self.cubic_spline_1 = None
        self.curve_map_np_arr_1 = np.arange(256)
        self.level_map_np_arr_1 = np.arange(256)
        self.con_strt_map_np_arr_1 = np.arange(256)

        self.in_out_type = ""
        self.in_param = ""
        self.p_mat = []
        self.cl_name = [
            "black",
            "gray",
            "white",
            "red",
            "green",
            "blue",
            "yellow",
            "cyan",
            "magenta",
            "orange",
            "purple",
        ]
        self.assign_default()

    def assign_default(self):
        self.in_out_type = "cv2"
        self.in_param = "Input-"
        self.in_param += "\n <in_img_path> path of the image folder"
        self.in_param += "\n <process_all_flag> If true the process for all the files"
        self.in_param += "\n <in_img_list> list of the images image folder"
        self.in_param += "\n <process_type> is to set what processing is required"

        self.in_param += "\n\t <process_type> = exposure_control_set_spline - to set the spline for exposure"
        self.in_param += (
            "\n\t\t <exposure_times> = >= -10.0 to +10.0 --> 0 means same same."
        )

        self.in_param += "\n\t <process_type> = curve_set_spline - to set spline"
        self.in_param += (
            "\n\t\t <curve_x_list> = [0.0, 100.0, 150.0, 255.0] --> x point list value"
        )
        self.in_param += (
            "\n\t\t <curve_y_list> = [0.0, 50.0, 200.0, 255.0] --> y point list value"
        )

        self.in_param += (
            "\n\t <process_type> = level_control_set_lines - to set the straight lines"
        )
        self.in_param += "\n\t\t <in_level_st> = >= 0 to 1.0 --> 0.0 is default."
        self.in_param += "\n\t\t <in_level_mid> = >= 0 to 1.0 --> 0.5 is default."
        self.in_param += "\n\t\t <in_level_en> = >= 0 to 1.0 --> 1.0 is default."
        self.in_param += "\n\t\t <out_level_st> = >= 0 to 1.0 --> 0.0 is default."
        self.in_param += "\n\t\t <out_level_en> = >= 0 to 1.0 --> 1.0 is default."

        self.in_param += "\n\t <process_type> = write_curve_map_arr_image - to set the spline for exposure"
        self.in_param += "\n\t\t <write_plot_fig_file> = >= file name with path to write the plot file."
        self.in_param += (
            "\n\t\t <curve_name> = >= curve_map_np_arr_1 name of the curve to plot."
        )

        self.in_param += "\n\t <process_type> = contrast_change - to change contrast"
        self.in_param += (
            "\n\t\t <contrast_change_factor> = >= 0 to +255 --> 1 means same."
        )

        self.in_param += (
            "\n\t <process_type> = brightness_change - to change brightness"
        )
        self.in_param += (
            "\n\t\t <brightness_amount_change >= -1.0 to +1.0 --> 0 means same same."
        )

        self.in_param += "\n\t <process_type> = brightness_contrast_change - to change brightness and contrast"
        self.in_param += (
            "\n\t\t <brightness_amount_change >= -1.0 to +1.0 --> 0 means same same."
        )
        self.in_param += (
            "\n\t\t <contrast_change_factor> = >= 0 to +255 --> 1 means same."
        )

        self.in_param += (
            "\n\t <process_type> = exposure_control - to change contrast, brightness"
        )
        self.in_param += (
            "\n\t\t <exposure_times> = >= -10.0 to +10.0 --> 0 means same same."
        )
        self.in_param += (
            "\n\t\t <set_exposure_curve_flag> = True if has to set else False."
        )

        self.in_param += "\n\t <process_type> = hue_change - to change hue"
        self.in_param += (
            "\n\t\t <hue_degree_change> = >= -inf to +inf --> 360 rotation means same."
        )

        self.in_param += (
            "\n\t <process_type> = saturation_change - to change saturation"
        )
        self.in_param += (
            "\n\t\t <saturation_times_change> = >= 0 to 255 --> 1 means same same."
        )

        self.in_param += (
            "\n\t <process_type> = intensity_value_change - to change intensity value"
        )
        self.in_param += (
            "\n\t\t <intensity_value_amount_change >= -1 to +1 --> 0 means same same."
        )

        self.in_param += "\n\t <process_type> = hue_sat_val_change - to change hue, saturation and value"
        self.in_param += (
            "\n\t\t <hue_degree_change> = >= -inf to +inf --> 360 rotation means same."
        )
        self.in_param += (
            "\n\t\t <saturation_times_change> = >= 0 to 255 --> 1 means same same."
        )
        self.in_param += (
            "\n\t\t <intensity_value_amount_change >= -1 to +1 --> 0 means same same."
        )

        self.in_param += "\n\t <process_type> = curve - to change intensity value"
        self.in_param += "\n\t\t <curve_set_spline_flag> = True to set the spline"
        self.in_param += (
            "\n\t\t <curve_x_list> = [0.0, 100.0, 150.0, 255.0] --> x point list value"
        )
        self.in_param += (
            "\n\t\t <curve_y_list> = [0.0, 50.0, 200.0, 255.0] --> y point list value"
        )
        self.in_param += (
            "\n\t\t <curve_color_ch_red> = True if red to be processed else False"
        )
        self.in_param += (
            "\n\t\t <curve_color_ch_green> = True if green to be processed else False"
        )
        self.in_param += (
            "\n\t\t <curve_color_ch_blue> = True if blue to be processed else False"
        )

        self.in_param += (
            "\n\t <process_type> = level_control - to change input or output level"
        )
        self.in_param += (
            "\n\t\t <level_control_set_lines_flag> = True to set the level lines"
        )
        self.in_param += "\n\t\t <in_level_st> = >= 0 to 1.0 --> 0.0 is default."
        self.in_param += "\n\t\t <in_level_mid> = >= 0 to 1.0 --> 0.5 is default."
        self.in_param += "\n\t\t <in_level_en> = >= 0 to 1.0 --> 1.0 is default."
        self.in_param += "\n\t\t <out_level_st> = >= 0 to 1.0 --> 0.0 is default."
        self.in_param += "\n\t\t <out_level_en> = >= 0 to 1.0 --> 1.0 is default."

        self.in_param += "\n\t <process_type> = histogram_equalization - to perform histogram equalization"
        self.in_param += "\n\t\t <histogram_calc_on_full_img_flag> = >= True for full image otherwise give row col value."
        self.in_param += "\n\t\t <in_st_row> = >= 0 to max_row -1  --> 0 means top."
        self.in_param += "\n\t\t <in_en_row> = >= 0 to max_row -1  --> 0 means top."
        self.in_param += "\n\t\t <in_st_col> = >= 0 to max_col -1  --> 0 means left."
        self.in_param += "\n\t\t <in_en_col> = >= 0 to max_col -1  --> 0 means left."

        self.in_param += "\n\t <process_type> = CLAHE - for contrast limiting adaptive histogram equalization"
        self.in_param += "\n\t\t <in_clip_limit> = >= 0 to 100  --> 0 means top."
        self.in_param += "\n\t\t <grid_row> = >= 0 to 100  --> 0 means small."
        self.in_param += "\n\t\t <grid_col> = >= 0 to 100  --> 0 means small."

        self.in_param += "\n\t <process_type> = contrast_stretch - to stretch contrast around histogram"
        self.in_param += "\n\t\t <in_con_stretch_amt> = >= 0 to 1  --> 0 means same."

    def resolve_num_to_array(self, in_val):
        o_mat = []

        if in_val == 1:
            o_mat = [1, 0, 0, 0]
        elif in_val == 2:
            o_mat = [0, 1, 0, 0]
        elif in_val == 3:
            o_mat = [0, 0, 1, 0]
        else:
            o_mat = [0, 0, 0, 0]

        return o_mat

    def cubic_spline_interpolate_points(self, in_x_list, in_y_list):
        x_list = []
        y_list = []

        mul_fact = 255
        x_min_diff = 0.00999 * mul_fact
        interpolate_pt = [0.999, 0.001]

        if (len(in_x_list) == len(in_y_list)) and (len(in_x_list) > 1):
            ini_found_flag = False
            for i_cnt in range(len(in_x_list)):
                if (
                    in_x_list[i_cnt] >= 0.0
                    and in_x_list[i_cnt] <= (1.0 * mul_fact)
                    and in_y_list[i_cnt] >= 0.0
                    and in_y_list[i_cnt] <= (1.0 * mul_fact)
                ):
                    x_list.append(in_x_list[i_cnt])
                    y_list.append(in_y_list[i_cnt])

                    base_i_cnt = i_cnt
                    ini_found_flag = True
                    break

            if ini_found_flag:
                for i_cnt in range(base_i_cnt, len(in_x_list) - 1):
                    if in_x_list[i_cnt + 1] >= in_x_list[base_i_cnt] + x_min_diff:
                        if (
                            in_x_list[i_cnt + 1] >= 0.0
                            and in_x_list[i_cnt + 1] <= (1.0 * mul_fact)
                            and in_y_list[i_cnt + 1] >= 0.0
                            and in_y_list[i_cnt + 1] <= (1.0 * mul_fact)
                        ):
                            x_list.append(in_x_list[i_cnt + 1])
                            y_list.append(in_y_list[i_cnt + 1])
                            base_i_cnt = i_cnt + 1
        else:
            x_list = [0.0, 1.0]
            x_list = [x * mul_fact for x in x_list]

            y_list = [0.0, 1.0]
            y_list = [x * mul_fact for x in y_list]

        if len(x_list) < 2:
            x_list = [0.0, 1.0]
            x_list = [x * mul_fact for x in x_list]

            y_list = [0.0, 1.0]
            y_list = [x * mul_fact for x in y_list]

        mod_x_list = []
        mod_y_list = []
        mod_x_list.append(x_list[0])
        mod_y_list.append(y_list[0])

        for i_cnt in range(len(x_list) - 1):
            for k_cnt in range(len(interpolate_pt)):
                mod_x_list.append(
                    (
                        (x_list[i_cnt] * interpolate_pt[k_cnt])
                        + (x_list[i_cnt + 1] * (1.0 - interpolate_pt[k_cnt]))
                    )
                )
                mod_y_list.append(
                    (
                        (y_list[i_cnt] * interpolate_pt[k_cnt])
                        + (y_list[i_cnt + 1] * (1.0 - interpolate_pt[k_cnt]))
                    )
                )

        mod_x_list.append(x_list[-1])
        mod_y_list.append(y_list[-1])

        return mod_x_list, mod_y_list

    # straight line segment construction
    def line_segment_interpolate_points(self, in_x_list, in_y_list):
        x_list = []
        y_list = []

        mul_fact = 255
        x_min_diff = 0.00999 * mul_fact

        if (len(in_x_list) == len(in_y_list)) and (len(in_x_list) > 1):
            ini_found_flag = False
            for i_cnt in range(len(in_x_list)):
                if (
                    in_x_list[i_cnt] >= 0.0
                    and in_x_list[i_cnt] <= (1.0 * mul_fact)
                    and in_y_list[i_cnt] >= 0.0
                    and in_y_list[i_cnt] <= (1.0 * mul_fact)
                ):
                    x_list.append(in_x_list[i_cnt])
                    y_list.append(in_y_list[i_cnt])

                    base_i_cnt = i_cnt
                    ini_found_flag = True
                    break

            if ini_found_flag:
                for i_cnt in range(base_i_cnt, len(in_x_list) - 1):
                    if in_x_list[i_cnt + 1] >= in_x_list[base_i_cnt]:
                        if (
                            in_x_list[i_cnt + 1] >= 0.0
                            and in_x_list[i_cnt + 1] <= (1.0 * mul_fact)
                            and in_y_list[i_cnt + 1] >= 0.0
                            and in_y_list[i_cnt + 1] <= (1.0 * mul_fact)
                        ):
                            x_list.append(in_x_list[i_cnt + 1])
                            y_list.append(in_y_list[i_cnt + 1])
                            base_i_cnt = i_cnt + 1
        else:
            x_list = [0.0, 1.0]
            x_list = [x * mul_fact for x in x_list]

            y_list = [0.0, 1.0]
            y_list = [x * mul_fact for x in y_list]

        if len(x_list) < 2:
            x_list = [0.0, 1.0]
            x_list = [x * mul_fact for x in x_list]

            y_list = [0.0, 1.0]
            y_list = [x * mul_fact for x in y_list]

        return x_list, y_list

    def get_mat_from_sub_process_num(self, in_sub_process_num):
        self.p_mat = []

        val = in_sub_process_num
        r_val = int(int(val) / 100)
        g_val = int(int(val - (r_val * 100)) / 10)
        b_val = int(val) - (r_val * 100) - (g_val * 10)

        c_mat = self.resolve_num_to_array(r_val)
        self.p_mat.extend(c_mat)
        c_mat = self.resolve_num_to_array(g_val)
        self.p_mat.extend(c_mat)
        c_mat = self.resolve_num_to_array(b_val)
        self.p_mat.extend(c_mat)

    def mod_adjust(
        self,
        in_img_path="",
        curve_name="",
        write_plot_fig_file="",
        process_all_flag=False,
        in_img_list=[],
        process_type="",
        contrast_change_factor=1.0,
        brightness_amount_change=0.0,
        exposure_times=0.0,
        set_exposure_curve_flag=True,
        hue_degree_change=0,
        saturation_times_change=1.0,
        intensity_value_amount_change=0.0,
        curve_x_list=[0.0, 1.0],
        curve_y_list=[0.0, 1.0],
        curve_set_spline_flag=True,
        curve_color_ch_red=True,
        curve_color_ch_green=True,
        curve_color_ch_blue=True,
        in_level_st=0.0,
        in_level_mid=0.5,
        in_level_en=1.0,
        out_level_st=0.0,
        out_level_en=1.0,
        level_control_set_lines_flag=True,
        histogram_calc_on_full_img_flag=True,
        in_st_row=0,
        in_en_row=1,
        in_st_col=0,
        in_en_col=0,
        in_clip_limit=1.0,
        grid_row=1,
        grid_col=1,
        in_con_stretch_amt=0.0,
        sub_process_mid="",
        out_img_path="",
        in_mat=[],
    ):

        t_st = time.time()

        self.last_overall_time = 0
        self.last_processing_time = 0
        self.last_reading_time = 0
        self.last_writing_time = 0
        self.processing_image_cnt = 0

        f_path_list = []
        f_name_list = []

        # exposure_control_set_spline
        if process_type == "exposure_control_set_spline":
            t_st = time.time()

            exp_fact = (
                -10.0
                if exposure_times < -10.0
                else 10.0 if exposure_times > 10.0 else exposure_times
            )

            exp_curve_x_list = np.array([0.0, 1.0])
            exp_curve_y_list = np.array([0.0, 1.0])

            if exp_fact < 0.0:
                exp_curve_y_list[1] = 1.0 - (-exp_fact / 10.0)
                if exp_curve_y_list[1] < 0.001:
                    exp_curve_y_list[1] = 0.001
            elif exp_fact > 0.0:
                exp_curve_x_list[1] = 1.0 - (exp_fact / 10.0)
                if exp_curve_x_list[1] < 0.001:
                    exp_curve_x_list[1] = 0.001

            exp_curve_x_list = exp_curve_x_list * 255
            exp_curve_y_list = exp_curve_y_list * 255

            mod_x, mod_y = self.cubic_spline_interpolate_points(
                exp_curve_x_list, exp_curve_y_list
            )
            self.cubic_spline_1 = CubicSpline(mod_x, mod_y)

            self.curve_map_np_arr_1 = np.arange(256)
            self.curve_map_np_arr_1 = np.clip(
                self.cubic_spline_1(self.curve_map_np_arr_1), 0, 255
            )

            t_en = time.time()
            self.last_functional_processing_time = t_en - t_st

        # curve_set_spline
        elif process_type == "curve_set_spline":
            t_st = time.time()

            mod_x, mod_y = self.cubic_spline_interpolate_points(
                curve_x_list, curve_y_list
            )
            self.cubic_spline_1 = CubicSpline(mod_x, mod_y)

            self.curve_map_np_arr_1 = np.arange(256)
            self.curve_map_np_arr_1 = np.clip(
                self.cubic_spline_1(self.curve_map_np_arr_1), 0, 255
            )

            t_en = time.time()
            self.last_functional_processing_time = t_en - t_st

        # curve_set_spline
        elif process_type == "level_control_set_lines":
            t_st = time.time()
            mul_fact = 255.0

            in_level_st = (
                0.0 if in_level_st < 0.0 else 1.0 if in_level_st > 1.0 else in_level_st
            )
            in_level_en = (
                0.0 if in_level_en < 0.0 else 1.0 if in_level_en > 1.0 else in_level_en
            )
            in_level_st = in_level_en if in_level_st > in_level_en else in_level_st
            in_level_mid = (
                in_level_st
                if in_level_mid < in_level_st
                else in_level_en if in_level_mid > in_level_en else in_level_mid
            )

            out_level_st = (
                0.0
                if out_level_st < 0.0
                else 1.0 if out_level_st > 1.0 else out_level_st
            )
            out_level_en = (
                0.0
                if out_level_en < 0.0
                else 1.0 if out_level_en > 1.0 else out_level_en
            )
            out_level_st = out_level_en if out_level_st > out_level_en else out_level_st

            mid_seg_1 = in_level_mid - in_level_st
            mid_seg_2 = in_level_en - in_level_mid

            total_seg = mid_seg_1 + mid_seg_2
            total_seg = 0.01 if total_seg < 0.001 else total_seg

            pt_1x = in_level_st * mul_fact
            pt_2x = (
                ((in_level_st * mid_seg_2) + (in_level_en * mid_seg_1)) / total_seg
            ) * mul_fact
            pt_3x = in_level_en * mul_fact

            pt_1y = out_level_st * mul_fact
            pt_2y = ((out_level_st * 0.5) + (out_level_en * 0.5)) * mul_fact
            pt_3y = out_level_en * mul_fact

            level_curve_x_list = np.array([pt_1x, pt_2x, pt_3x])
            level_curve_y_list = np.array([pt_1y, pt_2y, pt_3y])

            if pt_1x > 0.0:
                level_curve_x_list = np.insert(level_curve_x_list, 0, 0.0)
                level_curve_y_list = np.insert(level_curve_y_list, 0, 0.0)

                level_curve_x_list = np.insert(level_curve_x_list, 1, pt_1x)
                level_curve_y_list = np.insert(level_curve_y_list, 1, 0.0)

            if pt_3x < 255.0:
                level_curve_x_list = np.insert(
                    level_curve_x_list, len(level_curve_x_list), 255.0
                )
                level_curve_y_list = np.insert(
                    level_curve_y_list, len(level_curve_y_list), 255.0
                )

                level_curve_x_list = np.insert(level_curve_x_list, -1, pt_3x)
                level_curve_y_list = np.insert(level_curve_y_list, -1, 255.0)

            mod_x = level_curve_x_list
            mod_y = level_curve_y_list

            st_line_seg_curve = []

            st_x = 0
            for k_cnt in range(1, len(mod_x)):
                en_x = int(mod_x[k_cnt] + 0.499) + 1

                for i_cnt in range(st_x, en_x):
                    st_line_seg_curve.append(
                        int(np.interp(i_cnt, mod_x, mod_y) + 0.499)
                    )

                st_x = en_x

            self.level_map_np_arr_1 = np.array(st_line_seg_curve)
            self.level_map_np_arr_1 = np.clip(self.level_map_np_arr_1, 0, 255)

            t_en = time.time()
            self.last_functional_processing_time = t_en - t_st

        # write_curve_map_arr_image
        elif process_type == "write_curve_map_arr_image":
            t_st = time.time()

            fig, ax = plt.subplots(figsize=(5, 5))

            x_np_arr = np.arange(0, 256, 1, dtype=int)

            if curve_name == "curve_map_np_arr_1":
                ax.plot(x_np_arr, self.curve_map_np_arr_1)
            elif curve_name == "level_map_np_arr_1":
                ax.plot(x_np_arr, self.level_map_np_arr_1)
            elif curve_name == "con_strt_map_np_arr_1":
                ax.plot(x_np_arr, self.con_strt_map_np_arr_1)
            else:
                ax.plot(x_np_arr, x_np_arr)

            ax.set_xlim(-5, 260)
            ax.set_ylim(-5, 260)

            plt.savefig(write_plot_fig_file)

            t_en = time.time()
            self.last_functional_processing_time = t_en - t_st

        # process image related processing
        else:
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
                        f_path_list.append(
                            os.path.join(in_img_path, in_img_list[i_cnt])
                        )
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

                    # contrast_change
                    if process_type == "contrast_change":
                        con_change_fact = np.clip(contrast_change_factor, 0, 255)
                        out_img = cv.convertScaleAbs(in_img, alpha=con_change_fact)

                    # brightness_change
                    elif process_type == "brightness_change":
                        brightness_amt_ch = (
                            np.clip(brightness_amount_change, -1.0, 1.0) * 255
                        )
                        out_img = cv.convertScaleAbs(in_img, beta=brightness_amt_ch)

                    # brightness_contrast_change
                    if process_type == "brightness_contrast_change":
                        brightness_amt_ch = (
                            np.clip(brightness_amount_change, -1.0, 1.0) * 255
                        )
                        con_change_fact = np.clip(contrast_change_factor, 0, 255)
                        out_img = cv.convertScaleAbs(
                            in_img, alpha=con_change_fact, beta=brightness_amt_ch
                        )

                    # exposure_control
                    elif process_type == "exposure_control":
                        if set_exposure_curve_flag:
                            exp_fact = (
                                -10.0
                                if exposure_times < -10.0
                                else 10.0 if exposure_times > 10.0 else exposure_times
                            )

                            exp_curve_x_list = np.array([0.0, 1.0])
                            exp_curve_y_list = np.array([0.0, 1.0])

                            if exp_fact < 0.0:
                                exp_curve_y_list[1] = 1.0 - (-exp_fact / 10.0)
                                if exp_curve_y_list[1] < 0.001:
                                    exp_curve_y_list[1] = 0.001
                            elif exp_fact > 0.0:
                                exp_curve_x_list[1] = 1.0 - (exp_fact / 10.0)
                                if exp_curve_x_list[1] < 0.001:
                                    exp_curve_x_list[1] = 0.001

                            exp_curve_x_list = exp_curve_x_list * 255
                            exp_curve_y_list = exp_curve_y_list * 255

                            mod_x, mod_y = self.cubic_spline_interpolate_points(
                                exp_curve_x_list, exp_curve_y_list
                            )
                            self.cubic_spline_1 = CubicSpline(mod_x, mod_y)

                            self.curve_map_np_arr_1 = np.arange(256)
                            self.curve_map_np_arr_1 = np.clip(
                                self.cubic_spline_1(self.curve_map_np_arr_1), 0, 255
                            )

                        out_img = copy.deepcopy(in_img)

                        out_img[..., 2] = self.curve_map_np_arr_1[out_img[..., 2]]
                        out_img[..., 1] = self.curve_map_np_arr_1[out_img[..., 1]]
                        out_img[..., 0] = self.curve_map_np_arr_1[out_img[..., 0]]

                    # hue_change
                    elif process_type == "hue_change":
                        hsv_img = cv.cvtColor(in_img, cv.COLOR_BGR2HSV)
                        hsv_int_16 = hsv_img.astype(np.int16)

                        h_deg_ch = round((hue_degree_change) / 2)

                        hsv_int_16[..., 0] = np.clip(
                            ((hsv_int_16[..., 0] + h_deg_ch) % 180), 0, 255
                        )
                        hsv_uint_8 = hsv_int_16.astype(np.uint8)

                        out_img = cv.cvtColor(hsv_uint_8, cv.COLOR_HSV2BGR)

                    # saturation_change
                    elif process_type == "saturation_change":
                        hsv_img = cv.cvtColor(in_img, cv.COLOR_BGR2HSV)
                        hsv_int_16 = hsv_img.astype(np.int16)

                        s_times_ch = np.clip(saturation_times_change, 0.0, 255.0)

                        hsv_int_16[..., 1] = np.clip(
                            (hsv_int_16[..., 1] * s_times_ch), 0, 255
                        )
                        hsv_uint_8 = hsv_int_16.astype(np.uint8)

                        out_img = cv.cvtColor(hsv_uint_8, cv.COLOR_HSV2BGR)

                    # intensity_value_change
                    elif process_type == "intensity_value_change":
                        hsv_img = cv.cvtColor(in_img, cv.COLOR_BGR2HSV)
                        hsv_int_16 = hsv_img.astype(np.int16)

                        v_amt_ch = (
                            np.clip(intensity_value_amount_change, -1.0, 1.0) * 255
                        )

                        hsv_int_16[..., 2] = np.clip(
                            (hsv_int_16[..., 2] + v_amt_ch), 0, 255
                        )
                        hsv_uint_8 = hsv_int_16.astype(np.uint8)

                        out_img = cv.cvtColor(hsv_uint_8, cv.COLOR_HSV2BGR)

                    elif process_type == "hue_sat_val_change":
                        hsv_img = cv.cvtColor(in_img, cv.COLOR_BGR2HSV)
                        hsv_int_16 = hsv_img.astype(np.int16)

                        h_deg_ch = round((hue_degree_change) / 2)
                        s_times_ch = np.clip(saturation_times_change, 0.0, 255.0)
                        v_amt_ch = (
                            np.clip(intensity_value_amount_change, -1.0, 1.0) * 255
                        )

                        hsv_int_16[..., 0] = np.clip(
                            ((hsv_int_16[..., 0] + h_deg_ch) % 180), 0, 255
                        )
                        hsv_int_16[..., 1] = np.clip(
                            (hsv_int_16[..., 1] * s_times_ch), 0, 255
                        )
                        hsv_int_16[..., 2] = np.clip(
                            (hsv_int_16[..., 2] + v_amt_ch), 0, 255
                        )

                        hsv_uint_8 = hsv_int_16.astype(np.uint8)

                        out_img = cv.cvtColor(hsv_uint_8, cv.COLOR_HSV2BGR)

                    elif process_type == "curve":
                        if curve_set_spline_flag:
                            mod_x, mod_y = self.cubic_spline_interpolate_points(
                                curve_x_list, curve_y_list
                            )
                            self.cubic_spline_1 = CubicSpline(mod_x, mod_y)

                            self.curve_map_np_arr_1 = np.arange(256)
                            self.curve_map_np_arr_1 = np.clip(
                                self.cubic_spline_1(self.curve_map_np_arr_1), 0, 255
                            )

                        out_img = copy.deepcopy(in_img)

                        if curve_color_ch_red:
                            out_img[..., 2] = self.curve_map_np_arr_1[out_img[..., 2]]

                        if curve_color_ch_green:
                            out_img[..., 1] = self.curve_map_np_arr_1[out_img[..., 1]]

                        if curve_color_ch_blue:
                            out_img[..., 0] = self.curve_map_np_arr_1[out_img[..., 0]]

                    # level_control
                    elif process_type == "level_control":
                        if level_control_set_lines_flag:
                            mul_fact = 255.0

                            in_level_st = (
                                0.0
                                if in_level_st < 0.0
                                else 1.0 if in_level_st > 1.0 else in_level_st
                            )
                            in_level_en = (
                                0.0
                                if in_level_en < 0.0
                                else 1.0 if in_level_en > 1.0 else in_level_en
                            )
                            in_level_st = (
                                in_level_en
                                if in_level_st > in_level_en
                                else in_level_st
                            )
                            in_level_mid = (
                                in_level_st
                                if in_level_mid < in_level_st
                                else (
                                    in_level_en
                                    if in_level_mid > in_level_en
                                    else in_level_mid
                                )
                            )

                            out_level_st = (
                                0.0
                                if out_level_st < 0.0
                                else 1.0 if out_level_st > 1.0 else out_level_st
                            )
                            out_level_en = (
                                0.0
                                if out_level_en < 0.0
                                else 1.0 if out_level_en > 1.0 else out_level_en
                            )
                            out_level_st = (
                                out_level_en
                                if out_level_st > out_level_en
                                else out_level_st
                            )

                            mid_seg_1 = in_level_mid - in_level_st
                            mid_seg_2 = in_level_en - in_level_mid

                            total_seg = mid_seg_1 + mid_seg_2
                            total_seg = 0.01 if total_seg < 0.001 else total_seg

                            pt_1x = in_level_st * mul_fact
                            pt_2x = (
                                ((in_level_st * mid_seg_2) + (in_level_en * mid_seg_1))
                                / total_seg
                            ) * mul_fact
                            pt_3x = in_level_en * mul_fact

                            pt_1y = out_level_st * mul_fact
                            pt_2y = (
                                (out_level_st * 0.5) + (out_level_en * 0.5)
                            ) * mul_fact
                            pt_3y = out_level_en * mul_fact

                            level_curve_x_list = np.array([pt_1x, pt_2x, pt_3x])
                            level_curve_y_list = np.array([pt_1y, pt_2y, pt_3y])

                            if pt_1x > 0.0:
                                level_curve_x_list = np.insert(
                                    level_curve_x_list, 0, 0.0
                                )
                                level_curve_y_list = np.insert(
                                    level_curve_y_list, 0, 0.0
                                )

                                level_curve_x_list = np.insert(
                                    level_curve_x_list, 1, pt_1x
                                )
                                level_curve_y_list = np.insert(
                                    level_curve_y_list, 1, 0.0
                                )

                            if pt_3x < 255.0:
                                level_curve_x_list = np.insert(
                                    level_curve_x_list, len(level_curve_x_list), 255.0
                                )
                                level_curve_y_list = np.insert(
                                    level_curve_y_list, len(level_curve_y_list), 255.0
                                )

                                level_curve_x_list = np.insert(
                                    level_curve_x_list, -1, pt_3x
                                )
                                level_curve_y_list = np.insert(
                                    level_curve_y_list, -1, 255.0
                                )

                            mod_x = level_curve_x_list
                            mod_y = level_curve_y_list

                            st_line_seg_curve = []

                            st_x = 0
                            for k_cnt in range(1, len(mod_x)):
                                en_x = int(mod_x[k_cnt] + 0.499) + 1

                                for i_cnt in range(st_x, en_x):
                                    st_line_seg_curve.append(
                                        int(np.interp(i_cnt, mod_x, mod_y) + 0.499)
                                    )

                                st_x = en_x

                            self.level_map_np_arr_1 = np.array(st_line_seg_curve)
                            self.level_map_np_arr_1 = np.clip(
                                self.level_map_np_arr_1, 0, 255
                            )

                        out_img = copy.deepcopy(in_img)

                        out_img[..., 2] = self.level_map_np_arr_1[out_img[..., 2]]
                        out_img[..., 1] = self.level_map_np_arr_1[out_img[..., 1]]
                        out_img[..., 0] = self.level_map_np_arr_1[out_img[..., 0]]

                    # histogram_equalization
                    elif process_type == "histogram_equalization":
                        yuv_img = cv.cvtColor(in_img, cv.COLOR_BGR2YUV)

                        st_row = 0
                        en_row = in_img.shape[0]
                        st_col = 0
                        en_col = in_img.shape[1]

                        if not histogram_calc_on_full_img_flag:
                            st_row = in_st_row
                            en_row = in_en_row + 1
                            st_col = in_st_col
                            en_col = in_en_col + 1

                        hist, bins = np.histogram(
                            yuv_img[st_row:en_row, st_col:en_col, 0], 256, [0, 256]
                        )
                        cdf = hist.cumsum()
                        cdf = (
                            (cdf - cdf.min()) * 255 / max((cdf.max() - cdf.min()), 1)
                        ) + 0.499
                        cdf = cdf.astype("uint8")

                        yuv_img[:, :, 0] = cdf[yuv_img[:, :, 0]]

                        out_img = cv.cvtColor(yuv_img, cv.COLOR_YUV2BGR)

                    # CLAHE
                    elif process_type == "CLAHE":
                        yuv_img = cv.cvtColor(in_img, cv.COLOR_BGR2YUV)

                        clahe = cv.createCLAHE(
                            clipLimit=in_clip_limit, tileGridSize=(grid_col, grid_row)
                        )

                        yuv_img[:, :, 0] = clahe.apply(yuv_img[:, :, 0])

                        yuv_mod_img = cv.cvtColor(yuv_img, cv.COLOR_YUV2BGR)

                        out_img = cv.cvtColor(yuv_img, cv.COLOR_YUV2BGR)

                    # contrast_stretch
                    elif process_type == "contrast_stretch":
                        yuv_img = cv.cvtColor(in_img, cv.COLOR_BGR2YUV)

                        hist, bins = np.histogram(yuv_img[:, :, 0], 256, [0, 256])
                        cdf = hist.cumsum()
                        cdf = cdf / cdf[-1]

                        st_x = 0
                        for i_cnt in range(0, 256):
                            if cdf[i_cnt] < 0.5 * in_con_stretch_amt:
                                st_x = i_cnt
                            else:
                                break

                        en_x = 255
                        for i_cnt in range(255, -1, -1):
                            if cdf[i_cnt] > 1 - 0.5 * in_con_stretch_amt:
                                en_x = i_cnt
                            else:
                                break

                        st_x = st_x - int(
                            st_x * np.power((1 - in_con_stretch_amt), 4) + 0.4999
                        )
                        en_x = en_x + int(
                            ((255 - en_x) * np.power((1 - in_con_stretch_amt), 4))
                            + 0.4999
                        )

                        mod_x = [0, st_x, en_x, 255]
                        mod_y = [0, 0, 255, 255]

                        st_line_seg_curve = []

                        st_x = 0
                        for k_cnt in range(1, len(mod_x)):
                            en_x = int(mod_x[k_cnt] + 0.499) + 1

                            for i_cnt in range(st_x, en_x):
                                st_line_seg_curve.append(
                                    int(np.interp(i_cnt, mod_x, mod_y) + 0.499)
                                )

                            st_x = en_x

                        self.con_strt_map_np_arr_1 = np.array(st_line_seg_curve)
                        np.clip(self.con_strt_map_np_arr_1, 0, 255)

                        yuv_img[:, :, 0] = self.con_strt_map_np_arr_1[yuv_img[:, :, 0]]

                        out_img = cv.cvtColor(yuv_img, cv.COLOR_YUV2BGR)

                    t_en_process = time.time()
                    self.last_processing_time += t_en_process - t_st_process

                    t_st_write = time.time()

                    cv.imwrite(
                        os.path.join(out_img_path, f_name_list[f_i_cnt]), out_img
                    )
                    t_en_write = time.time()
                    self.last_writing_time += t_en_write - t_st_write

        t_en = time.time()
        self.last_overall_time = t_en - t_st


# In[2]:


# im_cp = adjust_process()

# # In[5]:


# in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]

# # In[7]:


# im_cp.mod_adjust(process_type = "exposure_control_set_spline",
#             exposure_times = -3)

# print(f"Time taken for functional change = {round(im_cp.last_functional_processing_time, 2)}s")

# # In[9]:


# im_cp.mod_adjust(process_type = "curve_set_spline",
#             curve_x_list = [0.0, 100.0, 150.0, 255.0],
#             curve_y_list = [0.0, 50.0, 200.0, 255.0])

# print(f"Time taken for functional change = {round(im_cp.last_functional_processing_time, 2)}s")

# # In[11]:


# im_cp.mod_adjust(process_type = "level_control_set_lines",
# #            in_level_st = 0.2,
# #            in_level_mid = 0.4,
# #            in_level_en = 0.8,
# #            out_level_st = 0.0,
# #            out_level_en = 1.0

# #            in_level_st = 0.0,
# #            in_level_mid = 0.5,
# #            in_level_en = 1.0,
# #            out_level_st = 0.2,
# #            out_level_en = 0.8

#             in_level_st = 0.1,
#             in_level_mid = 0.3,
#             in_level_en = 0.9,
#             out_level_st = 0.2,
#             out_level_en = 0.8
#             )

# print(f"Time taken for functional change = {round(im_cp.last_functional_processing_time, 2)}s")

# # In[13]:


# im_cp.mod_adjust(process_type = "write_curve_map_arr_image",
#             #write_plot_fig_file = "D:/MyData/Test_Set_01/vid_2/curve_map.jpg",
#             write_plot_fig_file = "D:/MyData/Test_Set_01/vid_2/line_map.jpg",
#             #curve_name = "curve_map_np_arr_1")
#             curve_name = "level_map_np_arr_1")

# print(f"Time taken for functional change = {round(im_cp.last_functional_processing_time, 2)}s")

# # In[15]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "contrast_change",
#             contrast_change_factor = 2,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[17]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "brightness_change",
#             brightness_amount_change = 0.5,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[19]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "brightness_contrast_change",
#             brightness_amount_change = -0.25,
#             contrast_change_factor = 2,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[21]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "exposure_control",
#             exposure_times = -5,
#             set_exposure_curve_flag = True,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[23]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "hue_change",
#             hue_degree_change = 180,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[25]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "saturation_change",
#             saturation_times_change = 5,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[27]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "intensity_value_change",
#             intensity_value_amount_change = 0.5,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[29]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "hue_sat_val_change",
#             hue_degree_change = 180,
#             saturation_times_change = 5,
#             intensity_value_amount_change = 0.5,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[31]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "curve",
#             curve_set_spline_flag = True,
#             curve_x_list = [0.0, 100.0, 150.0, 255.0],
#             curve_y_list = [0.0, 50.0, 200.0, 255.0],
#             curve_color_ch_red = True,
#             curve_color_ch_green = False,
#             curve_color_ch_blue = True,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[33]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "level_control",
#             level_control_set_lines_flag = True,
#             in_level_st = 0.2,
#             in_level_mid = 0.3,
#             in_level_en = 0.8,
#             out_level_st = 0.1,
#             out_level_en = 0.9,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[35]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "histogram_equalization",
#             histogram_calc_on_full_img_flag = False,
#             in_st_row = 372,
#             in_en_row = 604,
#             in_st_col = 329,
#             in_en_col = 374,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[37]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "CLAHE",
#             in_clip_limit = 20,
#             grid_row = 10,
#             grid_col = 10,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[39]:


# im_cp.mod_adjust(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "contrast_stretch",
#             in_con_stretch_amt = 0.6,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")

# # In[ ]:
