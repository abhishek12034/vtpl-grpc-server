#!/usr/bin/env python
# coding: utf-8

# In[13]:


import os
import time
from os import walk
import copy
from PIL import Image, ImageOps
import cv2 as cv


class channel_process:
    def __init__(self):
        self.jpg_quality = [
            int(cv.IMWRITE_JPEG_QUALITY),
            int(os.getenv("JPEG_QUALITY", 100)),
        ]
        self.last_overall_time = 0
        self.last_processing_time = 0
        self.last_reading_time = 0
        self.last_writing_time = 0
        self.processing_image_cnt = 0

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
        self.in_out_type = "pil"
        self.in_param = "Input-"
        self.in_param = "\n <in_img_path> path of the image folder"
        self.in_param = "\n <process_all_flag> If true the process for all the files"
        self.in_param = "\n <in_img_list> list of the images image folder"
        self.in_param = "\n <process_type> is to set what processing is required"
        self.in_param = "\n\t <process_type> = grayscale - to convert to gray"
        self.in_param = "\n\t <process_type> = color_conversion - to colorize the image"
        self.in_param = "\n\t\t <sub_process_black> = 'red/green/yellow...' - if process_type = color_conversion"
        self.in_param = "\n\t\t <sub_process_white> = 'blue/magenta/white...' - if process_type = color_conversion"
        self.in_param = "\n\t\t <sub_process_mid> = 'black/magenta/white...' - if process_type = color_conversion"
        self.in_param = "\n\t <process_type> = color_switch - to switch colors"
        self.in_param = (
            "\n\t\t <sub_process_num> = xyz - if process_type = color_switch"
        )
        self.in_param = (
            "\n\t\t <sub_process_num> = xyz - x, y, z is 1 for R, 2 for G and 3 for B"
        )
        self.in_param = "\n\t <out_img_path> = color_switch - to switch colors"
        self.in_param = "\n\t <in_mat> = matrix as follows to process"
        self.in_param = "\n\t\t <in_mat> = [ 1, 0, 0, 0,"
        self.in_param = "\n\n\t              0, 1, 0, 0,"
        self.in_param = "\n\n\t              0, 0, 1, 0 ]"
        self.in_param = "\n\t <process_type> = extract_single_channel - extract a single color channel and show in gray"
        self.in_param = (
            "\n\t\t <sub_process_num> = x - if process_type = extract_single_channel"
        )
        self.in_param = (
            "\n\t\t <sub_process_num> = x - x is 1 for R, 2 for G and 3 for B"
        )
        self.in_param = "\n\t <process_type> = display_selected_channels - display only a single color channel"
        self.in_param = "\n\t\t <sub_process_num> = xyz - if process_type = display_selected_channels"
        self.in_param = "\n\t\t <sub_process_num> = x - x is 1 for R, y is 2 for G and z is 3 for B, 0 for ignoring the same"
        self.in_param = "\n\t\t <sub_process_num> = red = 100, green = 20, blue = 3, yellow = 120, magenta = 103, cyan = 23"

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

    def mod_channel(
        self,
        in_img_path="",
        process_all_flag=False,
        in_img_list=[],
        process_type="",
        sub_process_num=0,
        sub_process_black="black",
        sub_process_white="white",
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

        for i_cnt in range(len(f_path_list)):
            t_st_read = time.time()

            with Image.open(f_path_list[i_cnt]) as in_img:
                self.processing_image_cnt += 1
                t_en_read = time.time()
                self.last_reading_time += t_en_read - t_st_read

                t_st_process = time.time()

                # grayscale
                if process_type == "grayscale":
                    # ITU-R 601-2 luma transform
                    # L = R * 299/1000 + G * 587/1000 + B * 114/1000
                    out_img = in_img.convert(mode="L")
                    out_img = out_img.convert("RGB")

                # color_conversion
                elif process_type == "color_conversion":
                    black_name = "black"
                    if sub_process_black in self.cl_name:
                        black_name = sub_process_black

                    white_name = "white"
                    if sub_process_white in self.cl_name:
                        white_name = sub_process_white

                    out_img = in_img.convert(mode="L")
                    if sub_process_mid in self.cl_name:
                        # print(f"black_name = {black_name}  white_name = {white_name}  sub_process_mid = {sub_process_mid}")
                        out_img = ImageOps.colorize(
                            out_img,
                            black=black_name,
                            white=white_name,
                            mid=sub_process_mid,
                        )
                    else:
                        out_img = ImageOps.colorize(
                            out_img, black=black_name, white=white_name
                        )

                # color_switch
                elif process_type == "color_switch":
                    self.get_mat_from_sub_process_num(sub_process_num)
                    out_img = in_img.convert("RGB", self.p_mat)

                # extract_single_channel
                elif process_type == "extract_single_channel":
                    mod_sub_process_num = (
                        0
                        if sub_process_num < 1
                        else (0 if sub_process_num > 3 else sub_process_num)
                    )
                    if sub_process_num < 1:
                        mod_sub_process_num = 0
                    elif sub_process_num > 3:
                        mod_sub_process_num = 0

                    mod_sub_process_num = mod_sub_process_num * 111
                    self.get_mat_from_sub_process_num(mod_sub_process_num)
                    out_img = in_img.convert("RGB", self.p_mat)

                # display_selected_channels
                elif process_type == "display_selected_channels":
                    self.get_mat_from_sub_process_num(sub_process_num)
                    out_img = in_img.convert("RGB", self.p_mat)

                t_en_process = time.time()
                self.last_processing_time += t_en_process - t_st_process

                t_st_write = time.time()
                out_img.save(
                    os.path.join(out_img_path, f_name_list[i_cnt]),
                    quality=self.jpg_quality[1],
                    subsampling=0,
                )

                t_en_write = time.time()
                self.last_writing_time += t_en_write - t_st_write

        t_en = time.time()
        self.last_overall_time = t_en - t_st


# In[14]:


# im_cp = channel_process()


# # In[15]:


# in_list = ["frm000000.jpg", "frm000001.jpg", "frm000002.jpg", "frm000003.jpg"]


# # In[20]:


# im_cp.mod_channel(in_img_path = "/home/vadmin/Documents/grpc-image-processing/vid_1",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "grayscale",
#             out_img_path = "/home/vadmin/Documents/grpc-image-processing/vid_2")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[7]:


# im_cp.mod_channel(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "color_conversion",
#             sub_process_black = "black",
#             sub_process_white = "orange",
#             #sub_process_mid = "gray",
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[8]:


# im_cp.mod_channel(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "color_switch",
#             sub_process_num = 312,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[9]:


# im_cp.mod_channel(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "extract_single_channel",
#             sub_process_num = 1,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# # In[10]:


# im_cp.mod_channel(in_img_path = "D:/MyData/Test_Set_01/vid_1/",
#             process_all_flag = True,
#             #in_img_list = in_list,
#             process_type = "display_selected_channels",
#             sub_process_num = 120,
#             out_img_path = "D:/MyData/Test_Set_01/vid_2/")

# print(f"Time taken for {im_cp.processing_image_cnt} images processing = {round(im_cp.last_processing_time, 2)}s  \
# read = {round(im_cp.last_reading_time, 2)}s  write = {round(im_cp.last_writing_time, 2)}s  overall = {round(im_cp.last_overall_time, 2)}s")


# In[ ]:
