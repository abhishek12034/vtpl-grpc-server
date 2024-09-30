import time
import threading
import grpc
from concurrent.futures import ThreadPoolExecutor
from stubs import channel_pb2 as channel_pb2
from stubs import channel_pb2_grpc
from stubs import main_pb2_grpc
from stubs import job_pb2
from image_processing_algorithm.vid2img_channel_x import channel_process
from utility.utility import count_images_in_folder, list_image_files,clear_output_folder
import uuid
import json
from logging_config import setup_logging
from config.redis_config import get_redis_client
from .channel_filter_type import ChannelProcessingType,StatusMessage
logger = setup_logging()

class ImageProcessingService(main_pb2_grpc.ImageProcessingServicer):
    def __init__(self):
        self.job_status = {}  # Make job_status an instance variable
        self.processor = channel_process()
        self.lock = threading.Lock()
        self.redis_client = get_redis_client()
        self.executor = ThreadPoolExecutor(max_workers=10)

    def GrayscaleFilter(self, request, context):
        # Temporrary line
        # clear_output_folder(request.out_img_path)
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        with self.lock:
            self.job_status[job_id] = {
                'job_id': job_id,
                'percentage': 0.0,
                'in_img_path': request.in_img_path,
                'out_img_path': request.out_img_path,
                'total_images': 0,
                'processed_image_count': 0,
                'status_message': StatusMessage.JOB_STARTED.name,
                'completed': False,
                'error': None,
                'thread_id': None 
            }
        logger.info(f"Job Created: {self.job_status[job_id]}")

        # Submit the image processing job and the progress update to the executor
        self.executor.submit(self.update_progress_in_redis, job_id)

        # Submit the image processing task to a thread
        self.executor.submit(self.process_image, request, job_id,ChannelProcessingType.GRAYSCALE.value)

        # Return the initial job status response
        return self.create_job_status_response(job_id, job_status=self.job_status[job_id])
    
    def ColorSwitchFilter(self, request, context):
        # Temporrary line
        clear_output_folder(request.out_img_path)

        job_id = str(uuid.uuid4())
        total_images = count_images_in_folder(request.in_img_path)
        
        # Initialize job status
        with self.lock:
            self.job_status[job_id] = {
                'job_id': job_id,
                'percentage': 0.0,
                'in_img_path': request.in_img_path,
                'out_img_path': request.out_img_path,
                'total_images': total_images,
                'processed_image_count': 0,
                'status_message': StatusMessage.JOB_STARTED.name,
                'completed': False,
                'error': None,
                'thread_id': None 
            }
        logger.info(f"Job Created: {self.job_status[job_id]}")

        # Submit the image processing job and the progress update to the executor
        self.executor.submit(self.update_progress_in_redis, job_id)

        # Submit the image processing task to a thread
        self.executor.submit(self.process_image, request, job_id,ChannelProcessingType.COLOR_SWITCH.value)

        # Return the initial job status response
        return self.create_job_status_response(job_id, job_status=self.job_status[job_id])


    def ColorConversionFilter(self, request, context):
        # Temporrary line
        clear_output_folder(request.out_img_path)

        job_id = str(uuid.uuid4())
        total_images = count_images_in_folder(request.in_img_path)
        
        # Initialize job status
        with self.lock:
            self.job_status[job_id] = {
                'job_id': job_id,
                'percentage': 0.0,
                'in_img_path': request.in_img_path,
                'out_img_path': request.out_img_path,
                'total_images': total_images,
                'processed_image_count': 0,
                'status_message': StatusMessage.JOB_STARTED.name,
                'completed': False,
                'error': None,
                'thread_id': None 
            }
        logger.info(f"Job Created: {self.job_status[job_id]}")

        # Submit the image processing job and the progress update to the executor
        self.executor.submit(self.update_progress_in_redis, job_id)

        # Submit the image processing task to a thread
        self.executor.submit(self.process_image, request, job_id,ChannelProcessingType.COLOR_CONVERSION.value)

        # Return the initial job status response
        return self.create_job_status_response(job_id, job_status=self.job_status[job_id])
    
    def ExtractSingleChannelFilter(self, request, context):
        # Temporrary line
        clear_output_folder(request.out_img_path)

        job_id = str(uuid.uuid4())
        total_images = count_images_in_folder(request.in_img_path)
        
        # Initialize job status
        with self.lock:
            self.job_status[job_id] = {
                'job_id': job_id,
                'percentage': 0.0,
                'in_img_path': request.in_img_path,
                'out_img_path': request.out_img_path,
                'total_images': total_images,
                'processed_image_count': 0,
                'status_message': StatusMessage.JOB_STARTED.name,
                'completed': False,
                'error': None,
                'thread_id': None 
            }
        logger.info(f"Job Created: {self.job_status[job_id]}")

        # Submit the image processing job and the progress update to the executor
        self.executor.submit(self.update_progress_in_redis, job_id)

        # Submit the image processing task to a thread
        self.executor.submit(self.process_image, request, job_id,ChannelProcessingType.EXTRACT_SINGLE_CHANNEL.value)

        # Return the initial job status response
        return self.create_job_status_response(job_id, job_status=self.job_status[job_id])
    
    def DisplaySelectedChannelFilter(self, request, context):
        # Temporrary line
        clear_output_folder(request.out_img_path)

        job_id = str(uuid.uuid4())
        total_images = count_images_in_folder(request.in_img_path)
        
        # Initialize job status
        with self.lock:
            self.job_status[job_id] = {
                'job_id': job_id,
                'percentage': 0.0,
                'in_img_path': request.in_img_path,
                'out_img_path': request.out_img_path,
                'total_images': total_images,
                'processed_image_count': 0,
                'status_message': StatusMessage.JOB_STARTED.name,
                'completed': False,
                'error': None,
                'thread_id': None 
            }
        logger.info(f"Job Created: {self.job_status[job_id]}")

        # Submit the image processing job and the progress update to the executor
        self.executor.submit(self.update_progress_in_redis, job_id)

        # Submit the image processing task to a thread
        self.executor.submit(self.process_image, request, job_id,ChannelProcessingType.DISPLAY_SELECTED_CHANNEL.value)

        # Return the initial job status response
        return self.create_job_status_response(job_id, job_status=self.job_status[job_id])

    def process_image(self, request, job_id, process_type: ChannelProcessingType):
        try:
            # checking a flag is true then updating the in_img_list with complete frames
            in_img_list = request.in_img_list
            if request.process_all_flag:
                in_img_list = list_image_files(request.in_img_path)

            # storing thread in redis along with job_id
            with self.lock:
                self.job_status[job_id]['thread_id'] = threading.get_ident()
                self.job_status[job_id]['status_message'] = StatusMessage.JOB_STARTED.name
                self.job_status[job_id]['total_images'] = len(in_img_list)
                self.store_job_status_in_redis(job_id, self.job_status[job_id])
            # Process each image in the list
            for in_img in in_img_list:
                self.processor.mod_channel(
                    in_img_path=request.in_img_path,
                    process_all_flag=False,
                    in_img_list=[in_img],
                    out_img_path=request.out_img_path,
                    process_type=process_type,
                    sub_process_black=getattr(request, 'sub_process_black', None),
                    sub_process_white=getattr(request, 'sub_process_white', None),
                    sub_process_mid=getattr(request, 'sub_process_mid', None),
                    sub_process_num=getattr(request, 'sub_process_num', None),
                )

                # Updating the number of images processed 
                with self.lock:
                    self.job_status[job_id]['processed_image_count'] += 1  

            # Mark job as completed
            with self.lock:
                self.job_status[job_id]['completed'] = True
                self.job_status[job_id]['status_message'] = StatusMessage.JOB_COMPLETED.name
                self.store_job_status_in_redis(job_id, self.job_status[job_id])

        except Exception as e:
            # Handle exceptions and update job status as failed
            with self.lock:
                self.job_status[job_id]['completed'] = False
                self.job_status[job_id]['status_message'] = StatusMessage.JOB_FAILED.name
                self.job_status[job_id]['error'] = str(e)
                logger.info(f"Job Failed for job_id {job_id} with error {e}")
                self.store_job_status_in_redis(job_id, self.job_status[job_id])

    def store_job_status_in_redis(self, job_id, job_status):
        try:
            # Check if job_status is serializable
            job_status_json = json.dumps(job_status)  # This will raise an error if it's not serializable
            # If the check passes, serialize and store in Redis
            self.redis_client.set(job_id, job_status_json)
            logger.info(f"Job status for {job_id} stored in Redis: {job_status}")
            
        except TypeError as e:
            logger.error(f"Error serializing job status for {job_id}: {e}")
            # Optionally log the job_status for debugging
            logger.debug(f"Job status contents: {job_status}")
            raise e
            
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
                status_message=StatusMessage.JOB_NOT_FOUND.name,
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
                time.sleep(1)  # Wait for 1 second

                with self.lock:
                    job_status = self.job_status.get(job_id)
                    if job_status:
                        # Calculate percentage
                        if job_status['total_images'] > 0:
                            job_status['percentage'] = (job_status['processed_image_count'] * 100) / job_status['total_images']
                        else:
                            job_status['percentage'] = 100  # Prevent division by zero if there are no images

                        # Update status message if all images processed
                        if job_status['percentage'] == 100:
                            job_status['status_message'] = StatusMessage.JOB_COMPLETED.name
                            logger.info(f"Job {job_id} completed. Status message updated.")

                        # Store job status in Redis
                        self.store_job_status_in_redis(job_id, job_status)
                        logger.info(f"Job {job_id} progress updated in Redis: {job_status}")

                    # Break the loop if job is completed
                    if job_status and job_status['completed']:
                        logger.info(f"Job {job_id} is completed.")
                        break

            except Exception as e:
                # Handle or log the error when updating Redis
                logger.error(f"Error updating progress for Job {job_id} in Redis: {str(e)}")

                # Increment retry count
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Max retries reached for Job {job_id}. Exiting the update loop.")
                    break  # Exit the loop after max retries
                else:
                    logger.info(f"Retrying... ({retry_count}/{max_retries})")
    
    def GetJobStatus(self, request, context):
        job_id = request.job_id
        try:
            job_status_json = self.redis_client.get(job_id)
            if job_status_json:
                job_status = json.loads(job_status_json)
                return self.create_job_status_response(job_id, job_status)
            else:
                logger.warning(f"Job ID {job_id} not found in Redis.")
                return self.create_job_status_response(job_id, error="Job ID not found.")
        except Exception as e:
            logger.error(f"Error in GetJobStatus: {e}")
            context.set_details('Internal server error occurred.')
            context.set_code(grpc.StatusCode.INTERNAL)
            return self.create_job_status_response(job_id, error=str(e))