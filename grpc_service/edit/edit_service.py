from concurrent.futures import ThreadPoolExecutor
from stubs import edit_pb2 as edit_pb2
from stubs import edit_pb2_grpc
from stubs import main_pb2_grpc
from image_processing_algorithm.vid2img_edit_xy import edit_process
from logging_config import setup_logging
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
from grpc_service.edit.edit_filter_type import EditProcessingType
from grpc_service.base.base_service import BaseService
import grpc
import threading

logger = setup_logging()


class EditService(main_pb2_grpc.EditServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.processor = edit_process()
        self.base_obj = BaseService()

    def CropFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request, context, EditProcessingType.CROP.value, self.process_crop
        )

    def FlipFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request, context, EditProcessingType.FLIP.value, self.process_flip
        )

    def RotateFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request, context, EditProcessingType.ROTATE.value, self.process_rotate
        )

    def ResizeFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request, context, EditProcessingType.RESIZE.value, self.process_resize
        )

    def PerspectiveFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            EditProcessingType.PERSPECTIVE.value,
            self.process_perspective,
        )

    def UndistortFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            EditProcessingType.UNDISTORT.value,
            self.process_undistort,
        )

    def AspectRatioFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            EditProcessingType.CORRECT_ASPECT_RATIO.value,
            self.process_aspect_ratio,
        )

    def FisheyeFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            EditProcessingType.CORRECT_FISHEYE.value,
            self.process_fisheye,
        )

    def SmartResizeFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            EditProcessingType.SMART_RESIZE.value,
            self.process_smart_resize,
        )

    def process_perspective(self, request, context, job_id, process_type, img_chunk):
        try:
            in_select_rc_arr = request.in_select_rc_arr.points
            logger.info(f"Select RC Array {in_select_rc_arr}")

            in_select_rc_arr_list = [[point.x, point.y] for point in in_select_rc_arr]
            logger.info(f"Select RC Array List {in_select_rc_arr_list}")
            adjust_params = {
                "process_type": process_type,
                "in_select_rc_arr": in_select_rc_arr_list,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_crop(self, request, context, job_id, process_type, img_chunk):
        try:
            in_st_row, in_en_row, in_st_col, in_en_col = (
                request.in_st_row,
                request.in_en_row,
                request.in_st_col,
                request.in_en_col,
            )

            adjust_params = {
                "process_type": process_type,
                "in_st_row": in_st_row,
                "in_en_row": in_en_row,
                "in_st_col": in_st_col,
                "in_en_col": in_en_col,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_flip(self, request, context, job_id, process_type, img_chunk):
        try:
            in_flip_hori_true_vert_false = request.in_flip_hori_true_vert_false
            adjust_params = {
                "process_type": process_type,
                "in_flip_hori_true_vert_false": in_flip_hori_true_vert_false,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_rotate(self, request, context, job_id, process_type, img_chunk):
        try:
            in_rotate_deg = request.in_rotate_deg
            adjust_params = {
                "process_type": process_type,
                "in_rotate_deg": in_rotate_deg,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_resize(self, request, context, job_id, process_type, img_chunk):
        try:
            in_st_row, in_en_row, in_st_col, in_en_col, in_keep_same_selection_size = (
                request.in_st_row,
                request.in_en_row,
                request.in_st_col,
                request.in_en_col,
                request.in_keep_same_selection_size,
            )

            adjust_params = {
                "process_type": process_type,
                "in_st_row": in_st_row,
                "in_en_row": in_en_row,
                "in_st_col": in_st_col,
                "in_en_col": in_en_col,
                "in_keep_same_selection_size": in_keep_same_selection_size,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_undistort(self, request, context, job_id, process_type, img_chunk):
        try:
            in_distortion_power = request.in_distortion_power
            logger.info(f"Distortion is {in_distortion_power}")
            adjust_params = {
                "process_type": process_type,
                "in_distortion_power": in_distortion_power,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_aspect_ratio(self, request, context, job_id, process_type, img_chunk):
        try:
            in_aspect_ratio_times = request.in_aspect_ratio_times
            logger.info(f"Aspect ratio times is {in_aspect_ratio_times}")
            adjust_params = {
                "process_type": process_type,
                "in_aspect_ratio_times": in_aspect_ratio_times,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_fisheye(self, request, context, job_id, process_type, img_chunk):
        try:
            in_distortion_power = request.in_distortion_power
            in_start_clock_pos = request.in_start_clock_pos
            in_direction = request.in_direction
            logger.info(f"Distortion Power is {in_distortion_power}")
            adjust_params = {
                "process_type": process_type,
                "in_distortion_power": in_distortion_power,
                "in_start_clock_pos": in_start_clock_pos,
                "in_direction": in_direction,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_smart_resize(self, request, context, job_id, process_type, img_chunk):
        try:
            in_st_row, in_en_row, in_st_col, in_en_col, in_scale_fact = (
                request.in_st_row,
                request.in_en_row,
                request.in_st_col,
                request.in_en_col,
                request.in_scale_fact,
            )
            adjust_params = {
                "process_type": process_type,
                "in_st_row": in_st_row,
                "in_en_row": in_en_row,
                "in_st_col": in_st_col,
                "in_en_col": in_en_col,
                "in_scale_fact": in_scale_fact,
                "model_folder_path": "image_processing_algorithm/edit_model_bank",
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_images(self, request, job_id, process_type, adjust_params, img_chunk):
        try:

            # Store thread ID in job status
            with self.base_obj.lock:
                self.base_obj.job_status[job_id]["thread_id"] = threading.get_ident()

            # Process each image in the list
            for in_img in img_chunk:
                self.processor.mod_edit(
                    process_all_flag=False,
                    in_img_path=request.in_img_path,
                    out_img_path=request.out_img_path,
                    in_img_list=[in_img],
                    **adjust_params,  # Pass specific filter parameters
                )

                # Update processed image count
                with self.base_obj.lock:
                    self.base_obj.job_status[job_id]["processed_image_count"] += 1

        except Exception as e:
            # Handle exceptions and update job status as failed
            with self.base_obj.lock:
                self.base_obj.job_status[job_id]["completed"] = False
                self.base_obj.job_status[job_id][
                    "status_message"
                ] = StatusMessage.JOB_FAILED.value
                self.base_obj.job_status[job_id][
                    "status_message"
                ] = JobStatusCode.FAILED.value
                self.base_obj.job_status[job_id]["error"] = str(e)
                logger.info(f"Job Failed for job_id {job_id} with error {e}")
                self.base_obj.store_job_status_in_redis(
                    job_id, self.base_obj.job_status[job_id]
                )
                raise e
