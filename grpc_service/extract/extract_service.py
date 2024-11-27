from stubs import channel_pb2 as channel_pb2
from stubs import main_pb2_grpc
from image_processing_algorithm.vid2img_extract_X import extract_process
from logging_config import setup_logging
from grpc_service.extract.extract_filter_type import ExtractProcessingType
from grpc_service.base.base_service import BaseService
import grpc
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
import threading

logger = setup_logging()


class ExtractService(main_pb2_grpc.ExtractServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.processor = extract_process()
        self.base_obj = BaseService()

    def NegativeFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.NEGATIVE.value,
            self.process_negative_extract,
        )

    def ThresholdFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.THRESHOLD.value,
            self.process_threshold_extract,
        )

    def AdaptiveThresholdFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.ADAPTIVE_THRESHOLD.value,
            self.process_adaptive_threshold_extract,
        )

    def LaplaceFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.LAPLACE.value,
            self.process_laplace_extract,
        )

    def PrewittFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.PREWITT.value,
            self.process_prewitt_extract,
        )

    def SobelFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.SOBEL.value,
            self.process_sobel_extract,
        )

    def ScharrFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.SCHARR.value,
            self.process_scharr_extract,
        )

    def CannyFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.CANNY.value,
            self.process_canny_extract,
        )

    def LinearFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.LINEAR_FILTER.value,
            self.process_linear_filter_extract,
        )

    def BiLinearFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.BILINEAR_FILTER.value,
            self.process_bilinear_filter_extract,
        )

    def ChannelSelectorFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.CHANNEL_SELECTOR.value,
            self.process_channel_selector_extract,
        )

    def ChannelSelectorFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.CHANNEL_SELECTOR.value,
            self.process_channel_selector_extract,
        )

    def ChannelDemuxFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.CHANNEL_DEMUX.value,
            self.process_channel_demux_extract,
        )

    def FourierFilter(self, request, context):

        return self.base_obj._start_image_processing_job(
            request,
            context,
            ExtractProcessingType.FOURIER.value,
            self.process_channel_fourier_extract,
        )

    def process_negative_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:

            adjust_params = {
                "process_type": process_type,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_threshold_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:

            adjust_params = {
                "process_type": process_type,
                "threshold_option": request.threshold_option,
                "threshold_level": request.threshold_level,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_adaptive_threshold_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            adjust_params = {
                "process_type": process_type,
                "adaptive_threshold_option": request.adaptive_threshold_option,
                "ad_th_box_len": request.ad_th_box_len,
                "ad_th_edge_reducer": request.ad_th_edge_reducer,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_laplace_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:

            adjust_params = {
                "process_type": process_type,
                "in_kernal_size": request.in_kernal_size,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_sobel_extract(self, request, context, job_id, process_type, img_chunk):
        try:

            adjust_params = {
                "process_type": process_type,
                "in_kernal_size": request.in_kernal_size,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_scharr_extract(self, request, context, job_id, process_type, img_chunk):
        try:

            adjust_params = {
                "process_type": process_type,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_prewitt_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:

            adjust_params = {
                "process_type": process_type,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_canny_extract(self, request, context, job_id, process_type, img_chunk):
        try:

            adjust_params = {
                "process_type": process_type,
                "in_rejection_upper_level": request.in_rejection_upper_level,
                "in_inclusion_lower_level": request.in_inclusion_lower_level,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_linear_filter_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            in_kernal_1 = (
                request.in_kernal_1
                if request.kernal_request_format == "horizontal"
                else [item.values for item in request.in_kernal_2]
            )

            adjust_params = {
                "process_type": process_type,
                "in_filter_display_mode": request.in_filter_display_mode,
                "in_kernal_1": in_kernal_1,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_bilinear_filter_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            in_kernal_1 = request.in_kernal_1
            in_kernal_2 = [item.values for item in request.in_kernal_2]
            adjust_params = {
                "process_type": process_type,
                "in_kernal_1": in_kernal_1,
                "in_kernal_2": in_kernal_2,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_channel_demux_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            in_filter_power = round(request.in_filter_power, 5)
            points = request.in_select_dual_pt_rc_list.points
            in_bg_rc_pt = request.in_bg_rc_pt

            # Convert points to the desired format
            in_select_dual_pt_rc_list = [[point.x, point.y] for point in points]
            in_bg_rc_pt = [in_bg_rc_pt.x, in_bg_rc_pt.y]
            logger.info(
                f"Input Values - in_filter_power: {in_filter_power}, in_bg_rc_pt: {in_bg_rc_pt}, in_select_dual_pt_rc_list: {in_select_dual_pt_rc_list}"
            )
            adjust_params = {
                "process_type": process_type,
                "in_select_dual_pt_rc_list": in_select_dual_pt_rc_list,
                "in_bg_rc_pt": in_bg_rc_pt,
                "in_filter_pass_true_block_false_flag": request.in_filter_pass_true_block_false_flag,
                "in_filter_power": in_filter_power,
            }

            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_channel_fourier_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            in_period_closeness = round(request.in_period_closeness, 5)
            in_clarity_strength = round(request.in_clarity_strength, 5)
            adjust_params = {
                "process_type": process_type,
                "in_period_closeness": in_period_closeness,
                "in_clarity_strength": in_clarity_strength,
            }

            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_channel_selector_extract(
        self, request, context, job_id, process_type, img_chunk
    ):
        in_manual_color_level = round(request.in_manual_color_level, 5)
        in_mid_color_val = round(request.in_mid_color_val, 5)
        in_spread_color = round(request.in_spread_color, 5)
        logger.info(
            f"Input Values - in_manual_color_level: {in_manual_color_level}, in_mid_color_val: {in_mid_color_val}, in_spread_color: {in_spread_color}"
        )
        try:
            adjust_params = {
                "process_type": process_type,
                "in_color_intensity_selection": request.in_color_intensity_selection,
                "in_manual_color_level": in_manual_color_level,
                "in_mid_color_val": in_mid_color_val,
                "in_spread_color": in_spread_color,
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
                self.base_obj.store_job_status_in_redis(
                    job_id, self.base_obj.job_status[job_id]
                )

            # Process each image in the list
            for in_img in img_chunk:
                self.processor.mod_extract(
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
