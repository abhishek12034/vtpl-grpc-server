from concurrent.futures import ThreadPoolExecutor
from stubs import denoise_pb2 as denoise_pb2
from stubs import denoise_pb2_grpc
from stubs import main_pb2_grpc
from image_processing_algorithm.vid2img_denoise_x import denoise_process
from logging_config import setup_logging
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
from grpc_service.denoise.denoise_filter_type import DenoiseProcessType
from grpc_service.base.base_service import BaseService
import grpc
import threading

logger = setup_logging()


class DenoiseService(BaseService, main_pb2_grpc.DenoiseServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.processor = denoise_process()

    def AveragingFilter(self, request, context):
        return self._start_image_processing_job(
            request,
            context,
            DenoiseProcessType.AVERAGING.value,
            self.process_averaging_denoise,
        )

    def GaussianSmoothingFilter(self, request, context):
        return self._start_image_processing_job(
            request,
            context,
            DenoiseProcessType.GAUSSIAN_SMOOTHING.value,
            self.process_gaussian_smoothing,
        )

    def BilateralFilter(self, request, context):
        return self._start_image_processing_job(
            request,
            context,
            DenoiseProcessType.BILATERAL_FILTERING.value,
            self.process_bilateral_filtering,
        )

    def MedianFilter(self, request, context):
        return self._start_image_processing_job(
            request,
            context,
            DenoiseProcessType.MEDIAN_FILTERING.value,
            self.process_median_filtering,
        )

    def WienerFilter(self, request, context):
        return self._start_image_processing_job(
            request,
            context,
            DenoiseProcessType.WIENER.value,
            self.process_wiener_filter,
        )

    def process_averaging_denoise(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            in_filter_size = request.in_filter_size
            adjust_params = {
                "process_type": process_type,
                "in_filter_size": in_filter_size,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_gaussian_smoothing(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            in_filter_size = request.in_filter_size
            adjust_params = {
                "process_type": process_type,
                "in_filter_size": in_filter_size,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_bilateral_filtering(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            in_filter_size = request.in_filter_size
            in_variation_range = request.in_variation_range
            adjust_params = {
                "process_type": process_type,
                "in_filter_size": in_filter_size,
                "in_variation_range": in_variation_range,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_median_filtering(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            in_filter_size = request.in_filter_size
            adjust_params = {
                "process_type": process_type,
                "in_filter_size": in_filter_size,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_wiener_filter(self, request, context, job_id, process_type, img_chunk):
        try:
            in_filter_size = request.in_filter_size
            wiener_power_val = request.wiener_power_val
            adjust_params = {
                "process_type": process_type,
                "in_filter_size": in_filter_size,
                "wiener_power_val": wiener_power_val,
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
            with self.lock:
                self.job_status[job_id]["thread_id"] = threading.get_ident()

            # Process each image in the list
            for in_img in img_chunk:
                self.processor.mod_denoise(
                    process_all_flag=False,
                    in_img_path=request.in_img_path,
                    out_img_path=request.out_img_path,
                    in_img_list=[in_img],
                    **adjust_params,  # Pass specific filter parameters
                )

                # Update processed image count
                with self.lock:
                    self.job_status[job_id]["processed_image_count"] += 1

        except Exception as e:
            # Handle exceptions and update job status as failed
            with self.lock:
                self.job_status[job_id]["completed"] = False
                self.job_status[job_id][
                    "status_message"
                ] = StatusMessage.JOB_FAILED.value
                self.job_status[job_id]["status_message"] = JobStatusCode.FAILED.value
                self.job_status[job_id]["error"] = str(e)
                logger.info(f"Job Failed for job_id {job_id} with error {e}")
                self.store_job_status_in_redis(job_id, self.job_status[job_id])
                raise e
