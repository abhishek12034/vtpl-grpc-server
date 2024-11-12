import time
import threading
import grpc
from concurrent.futures import ThreadPoolExecutor
from stubs import channel_pb2 as channel_pb2
from stubs import channel_pb2_grpc
from stubs import main_pb2_grpc
from stubs import job_pb2
from image_processing_algorithm.vid2img_channel_x import channel_process
from utility.utility import count_images_in_folder, list_image_files
import uuid
import json
from logging_config import setup_logging
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
from grpc_service.channel.channel_filter_type import ChannelProcessingType
from grpc_service.base.base_service import BaseService
import os

logger = setup_logging()


class ChannelService(BaseService, main_pb2_grpc.ChannelServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.processor = channel_process()

    def GrayscaleFilter(self, request, context):
        return self._start_image_processing_job(
            request,
            context,
            ChannelProcessingType.GRAYSCALE.value,
            self.process_grayscale,
        )

    def ColorSwitchFilter(self, request, context):
        return self._start_image_processing_job(
            request,
            context,
            ChannelProcessingType.COLOR_SWITCH.value,
            self.process_color_switch,
        )

    def ColorConversionFilter(self, request, context):
        return self._start_image_processing_job(
            request,
            context,
            ChannelProcessingType.COLOR_CONVERSION.value,
            self.process_color_conversion,
        )

    def ExtractSingleChannelFilter(self, request, context):
        return self._start_image_processing_job(
            request,
            context,
            ChannelProcessingType.EXTRACT_SINGLE_CHANNEL.value,
            self.process_extract_single_channel,
        )

    def DisplaySelectedChannelFilter(self, request, context):

        return self._start_image_processing_job(
            request,
            context,
            ChannelProcessingType.DISPLAY_SELECTED_CHANNEL.value,
            self.process_display_selected_channel,
        )

    def GetJobStatus(self, request, context):
        job_id = request.job_id
        try:
            job_status_json = self.redis_client.get(job_id)
            if job_status_json:
                job_status = json.loads(job_status_json)

                # Check if the job status code is 500 (FAILED)
                if job_status.get("status_code") == JobStatusCode.FAILED.value:
                    logger.error(f"Job {job_id} has failed.")
                    # context.set_details(f"Job {job_id} has failed.")
                    # context.set_code(grpc.StatusCode.INTERNAL)
                    return self.create_job_status_response(job_id, job_status)

                # If status code is not 500, return the job status as usual
                return self.create_job_status_response(job_id, job_status)
            else:
                logger.warning(f"Job ID {job_id} not found in Redis.")
                return self.create_job_status_response(
                    job_id, error="Job ID not found."
                )
        except Exception as e:
            logger.error(f"Error in GetJobStatus: {e}")
            context.set_details("Internal server error occurred.")
            context.set_code(grpc.StatusCode.INTERNAL)
            return self.create_job_status_response(job_id, error=str(e))

    def process_grayscale(self, request, context, job_id, process_type, img_chunk):
        try:
            adjust_params = {"process_type": process_type}
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_extract_single_channel(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:

            adjust_params = {"process_type": process_type}
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_color_conversion(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:

            adjust_params = {
                "process_type": process_type,
                "sub_process_black": request.sub_process_black,
                "sub_process_white": request.sub_process_white,
                "sub_process_mid": request.sub_process_mid,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_color_switch(self, request, context, job_id, process_type, img_chunk):
        try:

            adjust_params = {
                "process_type": process_type,
                "sub_process_num": request.sub_process_num,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_extract_single_channel(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:

            adjust_params = {
                "process_type": process_type,
                "sub_process_num": request.sub_process_num,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_display_selected_channel(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:

            adjust_params = {
                "process_type": process_type,
                "sub_process_num": request.sub_process_num,
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

                self.store_job_status_in_redis(job_id, self.job_status[job_id])

            # Process each image in the list
            for in_img in img_chunk:
                self.processor.mod_channel(
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
