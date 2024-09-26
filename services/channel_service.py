import time

import grpc
from stubs import channel_pb2 as channel_pb2
from stubs import channel_pb2_grpc as channel_pb2_grpc
from stubs import main_pb2_grpc
from stubs import job_pb2
from image_processing_service.vid2img_channel_x import channel_process
from utility.utility import clear_output_folder, count_images_in_folder
import uuid
from logging_config import setup_logging

logger = setup_logging()

class ImageProcessingServiceServicer(main_pb2_grpc.ImageProcessingServiceServicer):
    def __init__(self):
        self.processor = channel_process()
        self.job_status = {}

    def Channel(self, request, context):
        job_id = str(uuid.uuid4())
        try:
            if request.process_all_flag:
                total_images = count_images_in_folder(request.in_img_path)
            else:
                total_images = len(request.in_img_list)
        
            self.job_status[job_id] = {
                'job_id': job_id,
                'percentage': 0.0,
                'in_img_path': request.in_img_path,
                'out_img_path': request.out_img_path,
                'total_images': total_images
            }
            logger.info(f"Job is created {self.job_status}")
            
            clear_output_folder(request.out_img_path)

            yield channel_pb2.ImageProcessingResponse(
                processed_image_count=0,
                status_message="Job started.",
                total_time=0.0,
                reading_time=0.0,
                writing_time=0.0,
                processing_time=0.0,
                job_id=job_id
            )

            # Image Processing Algorithm
            self.processor.mod_channel(
                in_img_path=request.in_img_path,
                process_all_flag=request.process_all_flag,
                in_img_list=request.in_img_list,
                out_img_path=request.out_img_path,
                process_type=request.process_type,
                sub_process_black=request.sub_process_black,
                sub_process_white=request.sub_process_white,
                sub_process_mid=request.sub_process_mid,
                sub_process_num=request.sub_process_num,
            )
            # Final Output after completion of process
            yield channel_pb2.ImageProcessingResponse(
                processed_image_count=self.processor.processing_image_cnt,
                status_message="Processing completed.",
                total_time=round(self.processor.last_processing_time, 2),
                reading_time=round(self.processor.last_reading_time, 2),
                writing_time=round(self.processor.last_writing_time, 2),
                processing_time=round(self.processor.last_processing_time, 2),
                job_id=job_id
            )
        except Exception as e:
            logger.error(f"Error in Channel processing: {e}")
            context.set_details('Internal server error occurred.')
            context.set_code(grpc.StatusCode.INTERNAL)
            yield channel_pb2.ImageProcessingResponse(
                processed_image_count=0,
                status_message="Processing failed.",
                total_time=0.0,
                reading_time=0.0,
                writing_time=0.0,
                processing_time=0.0,
                job_id=job_id
            )
            clear_output_folder(request.out_img_path)


    def GetJobStatus(self, request, context):
        job_id = request.job_id
        
        try:
            if job_id in self.job_status:
                total_processed_file = count_images_in_folder(self.job_status[job_id]['out_img_path'])
                self.job_status[job_id]['percentage'] = (total_processed_file * 100) / self.job_status[job_id]['total_images']
                percentage = self.job_status[job_id]['percentage']
                response = job_pb2.JobStatusResponse(job_id=job_id, percentage=percentage)
            else:
                response = job_pb2.JobStatusResponse(job_id=job_id, percentage=0.0)
            return response
        except Exception as e:
            logger.error(f"Error in GetJobStatus: {e}")
            context.set_details('Internal server error occurred.')
            context.set_code(grpc.StatusCode.INTERNAL)
            return job_pb2.JobStatusResponse(job_id=job_id, percentage=0.0)
