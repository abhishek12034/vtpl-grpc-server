import threading
import json
import time
from concurrent.futures import ThreadPoolExecutor
from logging_config import setup_logging
from config.redis_config import get_redis_client
from stubs import job_pb2
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
import uuid
import grpc
from utility.utility import count_images_in_folder
import os

logger = setup_logging()


class BaseService:
    def __init__(self):
        self.job_status = {}
        self.lock = threading.Lock()
        self.redis_client = get_redis_client()
        self.executor = ThreadPoolExecutor(max_workers=10)

    def store_job_status_in_redis(self, job_id, job_status):
        EXPIRATION_TIME = 60 * 60 * 24
        try:
            job_status_json = json.dumps(job_status)
            self.redis_client.set(job_id, job_status_json, ex=EXPIRATION_TIME)
            self.redis_client.set
            logger.info(f"Job status for {job_id} stored in Redis: {job_status}")
        except Exception as e:
            logger.error(f"Error storing job status in Redis for {job_id}: {e}")
            raise e

    def create_job_status_response(
        self, job_id, job_status=None, error=None, status_code=None
    ):
        if job_status is None:
            return job_pb2.JobStatusResponse(
                job_id=job_id,
                percentage=0.0,
                in_img_path="",
                out_img_path="",
                total_input_images=0,
                processed_image_count=0,
                process_type=None,
                status_message=StatusMessage.JOB_NOT_FOUND.value,
                completed=False,
                error=error,
                status_code=JobStatusCode.NOT_FOUND.value,
            )
        return job_pb2.JobStatusResponse(
            job_id=job_status["job_id"],
            percentage=job_status["percentage"],
            in_img_path=job_status["in_img_path"],
            out_img_path=job_status["out_img_path"],
            total_input_images=job_status["total_images"],
            processed_image_count=job_status["processed_image_count"],
            process_type=job_status["process_type"],
            status_message=job_status["status_message"],
            completed=job_status["completed"],
            error=error if error else job_status.get("error"),
            status_code=job_status["status_code"],
        )

    def update_progress_in_redis(self, job_id):
        retry_count = 0
        max_retries = 5

        while True:
            try:
                time.sleep(1)

                with self.lock:
                    job_status = self.job_status.get(job_id)
                    if job_status["status_message"] == StatusMessage.JOB_FAILED.value:
                        break
                    if job_status:
                        # Calculate percentage
                        if job_status["total_images"] > 0:
                            job_status["percentage"] = int(
                                (job_status["processed_image_count"] * 100)
                                / job_status["total_images"]
                            )

                        if job_status["percentage"] == 100:
                            job_status["status_message"] = (
                                StatusMessage.JOB_COMPLETED.value
                            )
                            job_status["status_code"] = JobStatusCode.COMPLETED.value
                            job_status["completed"] = True

                        # Store job status in Redis
                        self.store_job_status_in_redis(job_id, job_status)
                        logger.info(
                            f"Job {job_id} progress updated in Redis: {job_status}"
                        )

                    if job_status and job_status["completed"]:
                        logger.info(f"Job {job_id} is completed.")
                        break
            except Exception as e:
                logger.error(f"Error updating progress for Job {job_id}: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    job_status["status_message"] = StatusMessage.JOB_FAILED.value
                    job_status["status_code"] = JobStatusCode.FAILED.value

                    logger.error(
                        f"Max retries reached for Job {job_id}. Exiting the update loop."
                    )
                    break
                else:
                    logger.info(f"Retrying... ({retry_count}/{max_retries})")

    def _start_image_processing_job(
        self, request, context, process_type, processing_func
    ):

        try:
            job_id = str(uuid.uuid4())
            total_images = (
                count_images_in_folder(request.in_img_path)
                if request.process_all_flag
                else len(request.in_img_list)
            )

            # # Validate required fields
            if not request.in_img_path:
                raise ValueError("in_img_path is required")

            if request.out_img_path == "":
                raise ValueError("out_img_path is required")

            # Check if in_img_path exists and if all images in in_img_list are present
            if not request.process_all_flag and not all(
                img in os.listdir(request.in_img_path) for img in request.in_img_list
            ):
                missing_images = [
                    img
                    for img in request.in_img_list
                    if img not in os.listdir(request.in_img_path)
                ]
                raise ValueError(
                    f"Either in_img_path does not exist: {request.in_img_path} or the following images do not exist in the directory: {', '.join(missing_images)}."
                )

            if not os.path.exists(os.path.dirname(request.out_img_path)):
                logger.info(f"out_img_path directory does not exist: {os.path.dirname(request.out_img_path)}")
                raise ValueError(
                    f"out_img_path directory does not exist: {os.path.dirname(request.out_img_path)}"
                )
            if total_images == 0:
                raise ValueError(
                    "No images found to process. Either provide a valid image path or image list."
                )

            # Initialize job status
            with self.lock:
                self.job_status[job_id] = {
                    "job_id": job_id,
                    "percentage": 0.0,
                    "in_img_path": request.in_img_path,
                    "out_img_path": request.out_img_path,
                    "total_images": total_images,
                    "processed_image_count": 0,
                    "status_message": StatusMessage.JOB_STARTED.value,
                    "process_type": process_type,
                    "completed": False,
                    "error": None,
                    "thread_id": None,
                    "status_code": JobStatusCode.IN_PROGRESS.value,
                }
            logger.info(f"Job Created: {self.job_status[job_id]}")

            # Submit the image processing job and progress update to the executor
            self.executor.submit(self.update_progress_in_redis, job_id)

            # Submit the image processing task
            self.executor.submit(
                processing_func, request, context, job_id, process_type
            )

            # Return the initial job status response
            return self.create_job_status_response(
                job_id, job_status=self.job_status[job_id]
            )
        except ValueError as ve:
            # Handle validation errors and send a specific message
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(ve))

        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while starting job: {str(e)}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Internal error occurred during job initialization",
            )
