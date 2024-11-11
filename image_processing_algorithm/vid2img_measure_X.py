#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os
import time
from os import walk
import copy
import numpy as np
import cv2 as cv
from sympy import symbols, Eq, solve, sympify
import matplotlib.pyplot as plt


class measure_process:
    def __init__(self):
        self.last_overall_time = 0
        self.last_processing_time = 0
        self.last_reading_time = 0
        self.last_writing_time = 0
        self.last_functional_processing_time = 0
        self.processing_image_cnt = 0

        self.in_out_type = ""
        self.in_param = ""
        self.out_param = ""
        self.calc_ref_val = 0
        self.ad_th_name = ["adaptive_mean", "adaptive_gaussian"]
        self.assign_default()

    def assign_default(self):
        self.in_out_type = "cv2"
        self.out_param = "\n\t\t <calc_ref_val >= the value will come unitless and in the same unit as the reference input is."

        self.in_param = "Input-"
        self.in_param += "\n <in_img_path> path of the image folder"
        self.in_param += "\n <process_all_flag> If true the process for all the files"

        self.in_param += "\n <in_img_list> list of the images image folder"
        self.in_param += "\n <process_type> is to set what processing is required"

        self.in_param += "\n\t <process_type> = measure1D - measurement of linear distance on flat plane"
        self.in_param += "\n\t\t <in_ref_dual_pt_rc_list> >= [[359, 957], [559, 952]], ((x1, y1), (x2, y2)) of the given reference straight line"
        self.in_param += "\n\t\t <in_calc_dual_pt_rc_list> >= [[348, 1266], [502, 1261]], ((x'1, y'1), (x'2, y'2)) of the straight line for calculation"
        self.in_param += "\n\t\t <in_ref_val> >= 68, measurement for the reference straight line as 68cm. Unit doesn't matter"
        self.in_param += (
            "\n\t\t              >= as calculated result will be on same unit."
        )

        self.in_param += "\n\t <process_type> = measure2D - measurement of linear distance on 2D plane which may not be flat"
        self.in_param += "\n\t\t <in_ref_dual_pt_rc_list> >= [[361, 1119], [403, 1160], [462, 890], [519, 1093]], terminal points of two straight lines"
        self.in_param += "\n\t\t                         >= First straight line is ((x1, y1), (x2, y2) Second straight line is ((x3, y3), (x4, y4)"
        self.in_param += "\n\t\t <in_calc_dual_pt_rc_list> >= [[348, 1266], [502, 1261]], ((x'1, y'1), (x'2, y'2)) of the straight line for calculation"
        self.in_param += "\n\t\t <in_ref_val_list> >= [40, 80], 2 measurements for the given 2 straight lines given by user as 40inch and 80inch"
        self.in_param += "\n\t\t                   >= unit doesn't matter as calculated result will be on same unit."

        self.in_param += (
            "\n\t <process_type> = measure3D - measurement of height on a 3D plane"
        )
        self.in_param += "\n\t\t <in_ref_line_rc_list> >= "
        self.in_param += "\n\t\t           >= [[[360, 956], [560, 956]], [[500, 1125], [741, 1125]], [[323, 1650], [357, 1650], [448, 1650]]]"
        self.in_param += "\n\t\t                       >= Three set of vertical lines which may have 2 or 3 coliner points"
        self.in_param += "\n\t\t                       >= 1st line has 2 points [[360, 956], [560, 956]]"
        self.in_param += "\n\t\t                       >= 2nd line has 2 points [[500, 1125], [741, 1125]]"
        self.in_param += "\n\t\t                       >= 3rd line has 3 points [[323, 1650], [357, 1650], [448, 1650]]"
        self.in_param += "\n\t\t                       >= Columns for all the 2 or 3 points in a line segment has same column as"
        self.in_param += (
            "\n\t\t                       >= 956 for 1st, 1125 for 2nd and 1650 for 3rd"
        )
        self.in_param += "\n\t\t                       >= 1st and 2nd points are compulsory whereas 3rd point is optional."
        self.in_param += "\n\t\t                       >= If 2 points are present then 2nd point is considered on the ground and."
        self.in_param += "\n\t\t                       >= if 3 points are present then 3rd point is considered on the ground."
        self.in_param += "\n\t\t <in_ref_base_ht_mesr_list> >= [71, 73, 15], height of the object in real measurement received as user input"
        self.in_param += "\n\t\t                             >= heigt of the object always given between 1st and 2nd points."
        self.in_param += "\n\t\t                             >= Here the reference height 71 is between  [360, 956] and [560, 956]. "
        self.in_param += "\n\t\t                             >= Here the reference height 73 is between  [500, 1125] and [741, 1125]. "
        self.in_param += "\n\t\t                             >= Here the reference height 15 is between  [323, 1650] and [357, 1650]. "
        self.in_param += "\n\t\t                             >= unit doesn't matter as calculated result will be on same unit."
        self.in_param += "\n\t\t <in_calc_line_rc> >= [[360, 1320], [400, 1320], [500, 1320]] -- This can be 2 or 3 points."
        self.in_param += "\n\t\t                   >= Here it is 3 points which are [360, 1320], [400, 1320] and [500, 1320]]"
        self.in_param += "\n\t\t                   >= Calculation has to be done for the height between 1st and 2nd points "
        self.in_param += (
            "\n\t\t                   >=  which are [360, 1320] and [400, 1320]"
        )
        self.in_param += "\n\t\t                   >=  If 3 points are available the the 3rd or last one is on the ground and "
        self.in_param += "\n\t\t                   >=  If 2 points are available the the 2nd or last one is on the ground."

    def mod_measure(
        self,
        in_img_path="",
        process_all_flag=False,
        in_img_list=[],
        process_type="",
        in_ref_dual_pt_rc_list=[[0, 0], [1, 1]],
        in_calc_dual_pt_rc_list=[[0, 0], [1, 1]],
        in_ref_val=1,
        in_ref_val_list=[1, 1],
        in_ref_line_rc_list=[
            [[0, 0], [1, 0]],
            [[0, 1], [1, 1]],
            [[0, 2], [1, 2], [2, 2]],
        ],
        in_ref_base_ht_mesr_list=[1, 2, 3],
        in_calc_line_rc=[[0, 1], [1, 1], [2, 1]],
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

                # measureme for 1D in flat plane
                if process_type == "measure1D":
                    out_img = copy.deepcopy(in_img)

                    ref_dist = np.power(
                        (
                            np.power(
                                (
                                    in_ref_dual_pt_rc_list[0][0]
                                    - in_ref_dual_pt_rc_list[1][0]
                                ),
                                2,
                            )
                            + np.power(
                                (
                                    in_ref_dual_pt_rc_list[0][1]
                                    - in_ref_dual_pt_rc_list[1][1]
                                ),
                                2,
                            )
                        ),
                        0.5,
                    )

                    calc_dist = np.power(
                        (
                            np.power(
                                (
                                    in_calc_dual_pt_rc_list[0][0]
                                    - in_calc_dual_pt_rc_list[1][0]
                                ),
                                2,
                            )
                            + np.power(
                                (
                                    in_calc_dual_pt_rc_list[0][1]
                                    - in_calc_dual_pt_rc_list[1][1]
                                ),
                                2,
                            )
                        ),
                        0.5,
                    )

                    if ref_dist > 0:
                        calc_val = (in_ref_val * calc_dist) / ref_dist
                    else:
                        calc_val = 0

                    self.calc_ref_val = calc_val

                # measurement for the lenght in 2D plane where plane may not be flat
                elif process_type == "measure2D":
                    out_img = copy.deepcopy(in_img)

                    a, b = symbols("a,b")

                    x1 = np.absolute(
                        in_ref_dual_pt_rc_list[0][0] - in_ref_dual_pt_rc_list[1][0]
                    )
                    y1 = np.absolute(
                        in_ref_dual_pt_rc_list[0][1] - in_ref_dual_pt_rc_list[1][1]
                    )

                    x2 = np.absolute(
                        in_ref_dual_pt_rc_list[2][0] - in_ref_dual_pt_rc_list[3][0]
                    )
                    y2 = np.absolute(
                        in_ref_dual_pt_rc_list[2][1] - in_ref_dual_pt_rc_list[3][1]
                    )

                    xc = np.absolute(
                        in_calc_dual_pt_rc_list[0][0] - in_calc_dual_pt_rc_list[1][0]
                    )
                    yc = np.absolute(
                        in_calc_dual_pt_rc_list[0][1] - in_calc_dual_pt_rc_list[1][1]
                    )

                    eq1 = Eq((x1 * a + y1 * b), in_ref_val_list[0])
                    eq2 = Eq((x2 * a + y2 * b), in_ref_val_list[1])

                    solve((eq1, eq2), (a, b))

                    # solving the equation
                    try:
                        solution = solve((eq1, eq2), (a, b))

                        # Access the resolved values
                        a_value = float(solution[a].evalf())
                        b_value = float(solution[b].evalf())

                        calc_val = xc * a_value + yc * b_value
                    except:
                        ref_dist = np.power(
                            (
                                np.power(
                                    (
                                        in_ref_dual_pt_rc_list[0][0]
                                        - in_ref_dual_pt_rc_list[1][0]
                                    ),
                                    2,
                                )
                                + np.power(
                                    (
                                        in_ref_dual_pt_rc_list[0][1]
                                        - in_ref_dual_pt_rc_list[1][1]
                                    ),
                                    2,
                                )
                            ),
                            0.5,
                        )

                        calc_dist = np.power(
                            (
                                np.power(
                                    (
                                        in_calc_dual_pt_rc_list[0][0]
                                        - in_calc_dual_pt_rc_list[1][0]
                                    ),
                                    2,
                                )
                                + np.power(
                                    (
                                        in_calc_dual_pt_rc_list[0][1]
                                        - in_calc_dual_pt_rc_list[1][1]
                                    ),
                                    2,
                                )
                            ),
                            0.5,
                        )

                        ref_val = in_ref_val_list[0]

                        if ref_dist > 0:
                            calc_val = (ref_val * calc_dist) / ref_dist
                        else:
                            calc_val = 0

                    self.calc_ref_val = calc_val

                # measurement of the height in 3D plane where the view is perspective
                elif process_type == "measure3D":
                    out_img = copy.deepcopy(in_img)

                    try:
                        in_ref_ratio_list = []
                        for i_cnt in range(len(in_ref_line_rc_list)):
                            ht_pixel = (
                                in_ref_line_rc_list[i_cnt][1][0]
                                - in_ref_line_rc_list[i_cnt][0][0]
                            )
                            in_ref_ratio_list.append(
                                in_ref_base_ht_mesr_list[i_cnt] / (ht_pixel)
                            )

                        in_calc_base_ht_pixel = (
                            in_calc_line_rc[1][0] - in_calc_line_rc[0][0]
                        )

                        a, b, c = symbols("a,b,c")

                        # defining equations
                        x1 = in_ref_line_rc_list[0][-1][0]
                        y1 = in_ref_line_rc_list[0][-1][1]
                        r1 = in_ref_ratio_list[0]

                        x2 = in_ref_line_rc_list[1][-1][0]
                        y2 = in_ref_line_rc_list[1][-1][1]
                        r2 = in_ref_ratio_list[1]

                        x3 = in_ref_line_rc_list[2][-1][0]
                        y3 = in_ref_line_rc_list[2][-1][1]
                        r3 = in_ref_ratio_list[2]

                        eq1 = Eq((x1 * a + y1 * b + c), r1)
                        eq2 = Eq((x2 * a + y2 * b + c), r2)
                        eq3 = Eq((x3 * a + y3 * b + c), r3)

                        solve((eq1, eq2, eq3), (a, b, c))

                        # solving the equation
                        solution = solve((eq1, eq2, eq3), (a, b, c))

                        # Access the resolved values
                        a_value = float(solution[a].evalf())
                        b_value = float(solution[b].evalf())
                        c_value = float(solution[c].evalf())

                        r_calc = (
                            in_calc_line_rc[-1][0] * a_value
                            + in_calc_line_rc[0][0] * b_value
                            + c_value
                        )
                        ht_calc = in_calc_base_ht_pixel * r_calc
                    except:
                        ht_calc = 0

                    self.calc_ref_val = ht_calc

                t_en_process = time.time()
                self.last_processing_time += t_en_process - t_st_process

                t_st_write = time.time()

                # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                # THIS PRINT ONLY FOR RETURN TESTING AND NEED NOT TO PRINT
                # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

                cv.imwrite(os.path.join(out_img_path, f_name_list[f_i_cnt]), out_img)
                t_en_write = time.time()
                self.last_writing_time += t_en_write - t_st_write

        t_en = time.time()
        self.last_overall_time = t_en - t_st


# In[5]:


# im_cp = measure_process()


# # In[7]:


# in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]


# # In[9]:


# im_cp.mod_measure(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "measure1D",
#             in_ref_dual_pt_rc_list = [[359, 957], [559, 952]],
#             in_calc_dual_pt_rc_list = [[348, 1266], [502, 1261]],
#             in_ref_val = 68,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[11]:


# im_cp.mod_measure(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "measure2D",
#             in_ref_dual_pt_rc_list = [[361, 1119], [403, 1160], [462, 890], [519, 1093]],
#             in_calc_dual_pt_rc_list = [[471, 1150], [452, 1495]],
#             in_ref_val_list = [40, 80],
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[13]:


# im_cp.mod_measure(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "measure3D",
#             in_ref_line_rc_list = [[[360, 956], [560, 956]], [[500, 1125], [741, 1125]], [[323, 1650], [357, 1650], [448, 1650]]],
#             in_ref_base_ht_mesr_list = [71, 73, 15],
#             in_calc_line_rc = [[360, 1320], [400, 1320], [500, 1320]],
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# In[ ]:
