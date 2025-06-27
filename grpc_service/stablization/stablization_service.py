from concurrent.futures import ThreadPoolExecutor
from stubs import stablization_pb2 as stablization_pb2
from stubs import stablization_pb2_grpc
from stubs import main_pb2_grpc
from image_processing_algorithm.vid2img_stabilization_x import stabilization_process
from logging_config import setup_logging
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
from grpc_service.stablization.stablization_filter_type import (
    StablizationProcessingType,
)
from grpc_service.base.base_service import BaseService
import grpc
import threading

logger = setup_logging()


class StablizationService(main_pb2_grpc.StablizationServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.processor = stabilization_process()
        self.base_obj = BaseService()

    def LocalStablizationFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            StablizationProcessingType.LOCAL_STABILIZATION.value,
            self.process_local_stablization,
            False,
        )

    def GlobalStablizationFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            StablizationProcessingType.GLOBAL_STABILIZATION.value,
            self.process_global_stablization,
            False,
        )

    def process_local_stablization(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            (
                in_st_row,
                in_en_row,
                in_st_col,
                in_en_col,
                in_stabilization_power,
                in_video_fps,
            ) = (
                request.in_st_row,
                request.in_en_row,
                request.in_st_col,
                request.in_en_col,
                request.in_stabilization_power,
                request.in_video_fps,
            )
            logger.info(
                f"Request details: "
                f"in_st_row={request.in_st_row}, "
                f"in_en_row={request.in_en_row}, "
                f"in_st_col={request.in_st_col}, "
                f"in_en_col={request.in_en_col}, "
                f"in_stabilization_power={request.in_stabilization_power}, "
                f"in_video_fps={request.in_video_fps}, "
            )
            adjust_params = {
                "process_type": process_type,
                "in_st_row": in_st_row,
                "in_en_row": in_en_row,
                "in_st_col": in_st_col,
                "in_en_col": in_en_col,
                "in_stabilization_power": in_stabilization_power,
                "in_video_fps": in_video_fps,
            }
            logger.info(f"Local Adjust params: {adjust_params}")
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_global_stablization(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:

            (
                in_stabilization_power,
                in_video_fps,
            ) = (
                request.in_stabilization_power,
                request.in_video_fps,
            )
            adjust_params = {
                "process_type": process_type,
                "in_stabilization_power": in_stabilization_power,
                "in_video_fps": in_video_fps,
            }
            logger.info(f"Global Adjust params: {adjust_params}")

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
            print("Inisde process_image stablization")
            with self.base_obj.lock:
                self.base_obj.job_status[job_id]["thread_id"] = threading.get_ident()

                # Process each image in the list
            print(f"Image chunk{img_chunk}")
            self.processor.mod_stabilization(
                process_all_flag=False,
                in_img_path=request.in_img_path,
                out_img_path=request.out_img_path,
                in_img_list=list(img_chunk),
                **adjust_params,  # Pass specific filter parameters
            )

            # Update processed image count
            with self.base_obj.lock:
                self.base_obj.job_status[job_id]["processed_image_count"] = len(
                    request.in_img_list
                )

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
