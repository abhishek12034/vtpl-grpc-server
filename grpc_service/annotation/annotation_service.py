from logging_config import setup_logging
from grpc_service.base.base_service import BaseService
from stubs import main_pb2_grpc
from stubs import annotation_pb2
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
from image_processing_algorithm.vid2img_annotate_x import annotate_process
from grpc_service.annotation.annotation_filter_type import AnnotationProcessingType
import grpc
import threading
logger = setup_logging()


class AnnotationService(main_pb2_grpc.AnnotationServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.base_obj = BaseService()
        self.processor = annotate_process()

    def AnnotationFilter(self, request, context):
        response = self.base_obj._start_image_processing_job(
            request,
            context,
            AnnotationProcessingType.ANNOTATE_WITH_BW.value,
            self.process_annotation_filter,
        )
        return annotation_pb2.AnnotationResponse(
            job_id=response.job_id,
            percentage=int(response.percentage),
            white_img_path=request.white_img_path,
            black_img_path=request.black_img_path,
            status_message=response.status_message,
            completed=response.completed,
            error_message=response.error,
            process_type=response.process_type,
            status_code=response.status_code,
        )
    def process_annotation_filter(self, request, context, job_id, process_type, img_chunk):
        try:
            print("all fla ")
            adjust_params = {
                "process_type": process_type,
                "white_image_path": request.white_img_path,
                "black_image_path": request.black_img_path,
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
                self.processor.mod_annotate(
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
