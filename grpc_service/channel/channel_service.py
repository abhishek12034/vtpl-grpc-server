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
from grpc_service.base.base_filter_type import StatusMessage
from grpc_service.channel.channel_filter_type import ChannelProcessingType
from grpc_service.base.base_service import BaseService
import os
logger = setup_logging()

class ChannelService(BaseService,main_pb2_grpc.ChannelServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.processor = channel_process()

    def GrayscaleFilter(self, request, context):
        try:
            # Check if input and output paths exist
            if not os.path.exists(request.in_img_path):
                raise FileNotFoundError(f"Input image path does not exist: {request.in_img_path}")
            if not os.path.exists(os.path.dirname(request.out_img_path)):
                raise FileNotFoundError(f"Output directory does not exist: {os.path.dirname(request.out_img_path)}")

            # Generate a new job ID
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
                    'status_message': StatusMessage.JOB_STARTED.value,
                    'completed': False,
                    'error': None,
                    'thread_id': None 
                }
            logger.info(f"Job Created: {self.job_status[job_id]}")

            # Submit the image processing job and the progress update to the executor
            self.executor.submit(self.update_progress_in_redis, job_id)

            # Submit the image processing task to a thread
            self.executor.submit(self.process_image, request, job_id, ChannelProcessingType.GRAYSCALE.value)

            # Return the initial job status response
            return self.create_job_status_response(job_id, job_status=self.job_status[job_id])
        
        except FileNotFoundError as fnf_error:
            logger.error(f"FileNotFoundError: {fnf_error}")
            context.set_details(str(fnf_error))
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            context.set_details(f"An error occurred while processing the image: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return None


    
    def ColorSwitchFilter(self, request, context):

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
                'status_message': StatusMessage.JOB_STARTED.value,
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
                'status_message': StatusMessage.JOB_STARTED.value,
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
                'status_message': StatusMessage.JOB_STARTED.value,
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
                'status_message': StatusMessage.JOB_STARTED.value,
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
                self.job_status[job_id]['status_message'] = StatusMessage.JOB_STARTED.value
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
                self.job_status[job_id]['status_message'] = StatusMessage.JOB_COMPLETED.value
                self.store_job_status_in_redis(job_id, self.job_status[job_id])

        except Exception as e:
            # Handle exceptions and update job status as failed
            with self.lock:
                self.job_status[job_id]['completed'] = False
                self.job_status[job_id]['status_message'] = StatusMessage.JOB_FAILED.value
                self.job_status[job_id]['error'] = str(e)
                logger.info(f"Job Failed for job_id {job_id} with error {e}")
                self.store_job_status_in_redis(job_id, self.job_status[job_id])

    
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