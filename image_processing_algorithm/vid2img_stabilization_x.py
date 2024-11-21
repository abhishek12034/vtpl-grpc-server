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
from vidstab.VidStab import VidStab
import matplotlib.pyplot as plt


class stabilization_process:
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

        self.in_param += "\n\t <process_type> = local_stabilization - sharpening using laplacian filter"
        self.in_param += "\n\t\t <in_stabilization_power> = 1 to 20 --> 1 is mild stabilization and 20 is high, default is 5"
        self.in_param += "\n\t\t <in_video_fps> = FPS of the video --> if no fps is available then give 10"
        self.in_param += "\n\t\t <in_st_row> = top position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_en_row> = bottom position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_st_col> = left position --> range 0 - max_row"
        self.in_param += "\n\t\t <in_en_col> = right position --> range 0 - max_row"

        self.in_param += "\n\t <process_type> = global_stabilization - sharpening using laplacian filter"
        self.in_param += "\n\t\t <in_stabilization_power> = 1 to 20 --> 1 is mild stabilization and 20 is high, default is 5"
        self.in_param += "\n\t\t <in_video_fps> = FPS of the video --> if no fps is available then give 10"

    def mod_stabilization(
        self,
        in_img_path="",
        curve_name="",
        write_plot_fig_file="",
        process_all_flag=False,
        in_img_list=[],
        process_type="",
        in_stabilization_power=5,
        in_video_fps=10,
        in_st_row=0,
        in_en_row=1,
        in_st_col=0,
        in_en_col=1,
        out_img_path="",
    ):
        print(f"inside stablization{in_img_list}")
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

        if process_type == "local_stabilization":

            f_path_list = sorted(f_path_list)

            f_i_cnt = 0
            total_image_count = len(f_path_list)

            in_object_bounding_box = (
                in_st_col,
                in_st_row,
                (in_en_col - in_st_col + 1),
                (in_en_row - in_st_row + 1),
            )
            ori_cen_box_col = int(
                in_object_bounding_box[0] + in_object_bounding_box[2] / 2
            )
            ori_cen_box_row = int(
                in_object_bounding_box[1] + in_object_bounding_box[3] / 2
            )

            window_size = in_stabilization_power * in_video_fps
            window_size = min(window_size, 200, total_image_count - 2)
            window_size = max(window_size, 1)

            stabilizer = VidStab()
            object_tracker = cv.TrackerCSRT_create()

            stab_count = 0
            file_queue = []
            first_img_frame_flag = True

            while True:
                if f_i_cnt < total_image_count:
                    if os.path.exists(f_path_list[f_i_cnt]):
                        t_st_read = time.time()
                        in_img = cv.imread(f_path_list[f_i_cnt])

                        self.processing_image_cnt += 1
                        t_en_read = time.time()
                        self.last_reading_time += t_en_read - t_st_read

                        file_queue.append(os.path.basename(f_path_list[f_i_cnt]))

                        if first_img_frame_flag:
                            object_tracker.init(in_img, in_object_bounding_box)
                            first_img_frame_flag = False

                f_i_cnt += 1
                if False:
                    print(f_i_cnt)

                t_st_process = time.time()

                stabilized_frame = stabilizer.stabilize_frame(
                    input_frame=in_img, smoothing_window=window_size
                )

                t_en_process = time.time()
                self.last_processing_time += t_en_process - t_st_process

                if stab_count >= window_size:
                    if len(file_queue) > 0:
                        out_fn = file_queue.pop(0)

                        success, object_bounding_box = object_tracker.update(
                            stabilized_frame
                        )

                        if success:
                            out_img = np.zeros(
                                shape=(
                                    stabilized_frame.shape[0],
                                    stabilized_frame.shape[1],
                                    3,
                                ),
                                dtype=np.uint8,
                            )

                            det_cen_box_col = int(
                                object_bounding_box[0] + (object_bounding_box[2] / 2)
                            )
                            det_cen_box_row = int(
                                object_bounding_box[1] + (object_bounding_box[3] / 2)
                            )

                            dev_row = np.clip(
                                (ori_cen_box_row - det_cen_box_row),
                                -int(stabilized_frame.shape[0] / 5),
                                int(stabilized_frame.shape[0] / 5),
                            )
                            dev_col = np.clip(
                                (ori_cen_box_col - det_cen_box_col),
                                -int(stabilized_frame.shape[1] / 5),
                                int(stabilized_frame.shape[1] / 5),
                            )

                            if dev_row < 0:
                                st_stb_row = -dev_row
                                en_stb_row = out_img.shape[0]
                                st_out_row = 0
                                en_out_row = stabilized_frame.shape[0] + dev_row
                            else:
                                st_stb_row = 0
                                en_stb_row = out_img.shape[0] - dev_row
                                st_out_row = dev_row
                                en_out_row = stabilized_frame.shape[0]

                            if dev_col < 0:
                                st_stb_col = -dev_col
                                en_stb_col = out_img.shape[1]
                                st_out_col = 0
                                en_out_col = stabilized_frame.shape[1] + dev_col
                            else:
                                st_stb_col = 0
                                en_stb_col = out_img.shape[1] - dev_col
                                st_out_col = dev_col
                                en_out_col = stabilized_frame.shape[1]

                            out_img[st_out_row:en_out_row, st_out_col:en_out_col, :] = (
                                stabilized_frame[
                                    st_stb_row:en_stb_row, st_stb_col:en_stb_col, :
                                ]
                            )

                            draw_rectangle_flag = False
                            if draw_rectangle_flag:
                                (x, y, w, h) = [int(v) for v in object_bounding_box]
                                cv.rectangle(
                                    out_img,
                                    (x + dev_col, y + dev_row),
                                    (x + dev_col + w, y + dev_row + h),
                                    (0, 255, 0),
                                    4,
                                )
                        else:
                            out_img = stabilized_frame

                        t_st_write = time.time()
                        cv.imwrite(os.path.join(out_img_path, out_fn), out_img)
                        t_en_write = time.time()
                        self.last_writing_time += t_en_write - t_st_write

                    else:
                        break

                stab_count += 1

        if process_type == "global_stabilization":
            f_path_list = sorted(f_path_list)

            f_i_cnt = 0
            total_image_count = len(f_path_list)

            window_size = in_stabilization_power * in_video_fps
            window_size = min(window_size, 200, total_image_count - 2)
            window_size = max(window_size, 1)

            stabilizer = VidStab()
            stab_count = 0
            file_queue = []

            while True:
                if f_i_cnt < total_image_count:
                    if os.path.exists(f_path_list[f_i_cnt]):
                        t_st_read = time.time()
                        in_img = cv.imread(f_path_list[f_i_cnt])

                        self.processing_image_cnt += 1
                        t_en_read = time.time()
                        self.last_reading_time += t_en_read - t_st_read

                        file_queue.append(os.path.basename(f_path_list[f_i_cnt]))

                f_i_cnt += 1
                if False:
                    print(f_i_cnt)

                t_st_process = time.time()

                out_img = stabilizer.stabilize_frame(
                    input_frame=in_img, smoothing_window=window_size
                )

                t_en_process = time.time()
                self.last_processing_time += t_en_process - t_st_process

                if stab_count >= window_size:
                    if len(file_queue) > 0:
                        out_fn = file_queue.pop(0)

                        t_st_write = time.time()
                        cv.imwrite(os.path.join(out_img_path, out_fn), out_img)
                        t_en_write = time.time()
                        self.last_writing_time += t_en_write - t_st_write

                    else:
                        break

                stab_count += 1

        t_en = time.time()
        self.last_overall_time = t_en - t_st


# In[2]:


# im_cp = stabilization_process()


# # In[ ]:


# #in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]


# # In[5]:


# im_cp.mod_stabilization(in_img_path = "C:/Users/vadmin/Documents/MyData/test_video/off_2_img/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "local_stabilization",
#             in_stabilization_power = 5,
#             in_video_fps = 10,
#             in_st_row = 474,
#             in_en_row = 714,
#             in_st_col = 1340,
#             in_en_col = 1450,
#             out_img_path = "C:/Users/vadmin/Documents/MyData/test_video/out_img_7/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[7]:


# im_cp.mod_stabilization(in_img_path = "C:/Users/vadmin/Documents/MyData/test_video/off_2_img/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "global_stabilization",
#             in_stabilization_power = 5,
#             in_video_fps = 10,
#             out_img_path = "C:/Users/vadmin/Documents/MyData/test_video/out_img_8/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[ ]:
