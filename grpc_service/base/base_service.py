import threading
import json
import time
from concurrent.futures import ThreadPoolExecutor
from logging_config import setup_logging
from config.redis_config import get_redis_client
from stubs import job_pb2
from grpc_service.base.base_filter_type import StatusMessage
import uuid
import grpc
logger = setup_logging()

class BaseService:
    def __init__(self):
        self.job_status = {}
        self.lock = threading.Lock()
        self.redis_client = get_redis_client()
        self.executor = ThreadPoolExecutor(max_workers=10)

    def store_job_status_in_redis(self, job_id, job_status):
        try:
            job_status_json = json.dumps(job_status)
            self.redis_client.set(job_id, job_status_json)
            logger.info(f"Job status for {job_id} stored in Redis: {job_status}")
        except Exception as e:
            logger.error(f"Error storing job status in Redis for {job_id}: {e}")
            raise e

    def create_job_status_response(self, job_id, job_status=None, error=None):
        if job_status is None:
            return job_pb2.JobStatusResponse(
                job_id=job_id,
                percentage=0.0,
                in_img_path='',
                out_img_path='',
                total_input_images=0,
                processed_image_count=0,
                status_message=StatusMessage.JOB_NOT_FOUND.value,
                completed=False,
                error=error
            )
        return job_pb2.JobStatusResponse(
            job_id=job_status['job_id'],
            percentage=job_status['percentage'],
            in_img_path=job_status['in_img_path'],
            out_img_path=job_status['out_img_path'],
            total_input_images=job_status['total_images'],
            processed_image_count=job_status['processed_image_count'],
            status_message=job_status['status_message'],
            completed=job_status['completed'],
            error=error if error else job_status.get('error')
        )

    def update_progress_in_redis(self, job_id):
        retry_count = 0
        max_retries = 5

        while True:
            try:
                time.sleep(1)

                with self.lock:
                    job_status = self.job_status.get(job_id)
                    if job_status['status_message'] == StatusMessage.JOB_FAILED.value:
                        break
                    if job_status:
                        # Calculate percentage
                        if job_status['total_images'] > 0:
                            job_status['percentage'] = (job_status['processed_image_count'] * 100) / job_status['total_images']
                        else:
                            job_status['percentage'] = 100  # Prevent division by zero

                        if job_status['percentage'] == 100:
                            job_status['status_message'] = StatusMessage.JOB_COMPLETED.value

                        # Store job status in Redis
                        self.store_job_status_in_redis(job_id, job_status)
                        logger.info(f"Job {job_id} progress updated in Redis: {job_status}")

                    if job_status and job_status['completed']:
                        logger.info(f"Job {job_id} is completed.")
                        break
            except Exception as e:
                logger.error(f"Error updating progress for Job {job_id}: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    job_status['status_message'] = StatusMessage.JOB_FAILED.value
                    logger.error(f"Max retries reached for Job {job_id}. Exiting the update loop.")
                    break
                else:
                    logger.info(f"Retrying... ({retry_count}/{max_retries})")
    def _start_image_processing_job(self, request,context, process_type, processing_func):
        try:
            job_id = str(uuid.uuid4())

            # Validate required fields
            if not request.in_img_path:
                raise ValueError("in_img_path is required")
            if request.out_img_path == "":
                raise ValueError("out_img_path is required")
            if request.process_all_flag is None:
                raise ValueError("process_all_flag is required")
            
            # Initialize job status
            with self.lock:
                self.job_status[job_id] = {
                    'job_id': job_id,
                    'percentage': 0.0,
                    'in_img_path': request.in_img_path,
                    'out_img_path': request.out_img_path,
                    'total_images': 0,
                    'processed_image_count': 0,
                    'status_message': StatusMessage.JOB_STARTED.value,
                    'completed': False,
                    'error': None,
                    'thread_id': None
                }
            logger.info(f"Job Created: {self.job_status[job_id]}")

            # Submit the image processing job and progress update to the executor
            self.executor.submit(self.update_progress_in_redis, job_id)

            # Submit the image processing task
            self.executor.submit(processing_func, request,context, job_id, process_type)

            # Return the initial job status response
            return self.create_job_status_response(job_id, job_status=self.job_status[job_id])

        except ValueError as ve:
            # Handle validation errors and send a specific message
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(ve))
        
        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while starting job: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")
