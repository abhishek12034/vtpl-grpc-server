from concurrent.futures import ThreadPoolExecutor
from stubs import edit_pb2 as edit_pb2
from stubs import deblur_pb2_grpc
from stubs import main_pb2_grpc

from image_processing_algorithm.vid2img_deblurring_1 import deblurring_process
from logging_config import setup_logging
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
from grpc_service.deblur.deblur_filter_type import DeblurProcessingType
from grpc_service.base.base_service import BaseService
import grpc
import threading

logger = setup_logging()


class DeblurService(main_pb2_grpc.DeblurServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.processor = deblurring_process()
        self.base_obj = BaseService()

    def MotionFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            DeblurProcessingType.MOTION.value,
            self.process_motion,
        )

    def OpticalFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            DeblurProcessingType.OPTICAL.value,
            self.process_optical,
        )

    def process_optical(self, request, context, job_id, process_type, img_chunk):
        try:
            (in_dimention, in_snr) = (
                request.in_dimention,
                request.in_snr,
            )
            logger.info(f"In Dimension: {in_dimention}, In SNR: {in_snr}")
            adjust_params = {
                "process_type": process_type,
                "in_spread_distance": in_dimention,
                "in_snr": in_snr,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_motion(self, request, context, job_id, process_type, img_chunk):
        try:
            (in_angle, in_dimention, in_snr) = (
                request.in_angle,
                request.in_dimention,
                request.in_snr,
            )
            logger.info(
                f"In Angle: {in_angle}, In Dimension: {in_dimention}, In SNR: {in_snr}"
            )
            adjust_params = {
                "process_type": process_type,
                "in_angle": in_angle,
                "in_spread_distance": in_dimention,
                "in_snr": in_snr,
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
                self.processor.mod_deblurring(
                    process_all_flag=False,
                    in_img_path=request.in_img_path,
                    out_img_path=request.out_img_path,
                    in_img_list=[in_img],
                    **adjust_params,  # Pass specific filter parameters
                    par_st_row=request.par_st_row,
                    par_en_row=request.par_en_row,
                    par_st_col=request.par_st_col,
                    par_en_col=request.par_en_col,
                    par_process_flag=request.par_process_flag,
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
