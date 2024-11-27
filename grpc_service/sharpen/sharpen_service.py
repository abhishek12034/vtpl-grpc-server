from concurrent.futures import ThreadPoolExecutor
from stubs import edit_pb2 as edit_pb2
from stubs import sharpen_pb2_grpc
from stubs import main_pb2_grpc
from image_processing_algorithm.vid2img_sharpen_x import sharpen_process
from logging_config import setup_logging
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
from grpc_service.sharpen.sharpen_filter_type import SharpenProcessingType
from grpc_service.base.base_service import BaseService
import grpc
import threading

logger = setup_logging()


class SharpenService(main_pb2_grpc.SharpenServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.processor = sharpen_process()
        self.base_obj = BaseService()

    def LaplacianFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            SharpenProcessingType.LAPLACIAN_SHARPEN.value,
            self.process_laplacian_sharpen,
        )

    def UnsharpMaskFilter(self, request, context):
        return self.base_obj._start_image_processing_job(
            request,
            context,
            SharpenProcessingType.UNSHARP_MASK.value,
            self.process_unsharp_mask,
        )

    def process_laplacian_sharpen(
        self, request, context, job_id, process_type, img_chunk
    ):
        try:
            in_lap_method = request.in_lap_method
            adjust_params = {
                "process_type": process_type,
                "in_lap_method": in_lap_method,
            }
            self.process_images(request, job_id, process_type, adjust_params, img_chunk)

        except Exception as e:
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )

    def process_unsharp_mask(self, request, context, job_id, process_type, img_chunk):
        try:
            in_sharpen_power = request.in_sharpen_power
            in_sharpen_spread = request.in_sharpen_spread
            adjust_params = {
                "process_type": process_type,
                "in_sharpen_power": in_sharpen_power,
                "in_sharpen_spread": in_sharpen_spread,
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
                self.processor.mod_sharpen(
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
