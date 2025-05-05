from logging_config import setup_logging
from grpc_service.base.base_service import BaseService
from stubs import main_pb2_grpc
from stubs import annotation_pb2
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
import uuid

logger = setup_logging()


class AnnotationService(main_pb2_grpc.AnnotationServiceServicer):
    def __init__(self):
        super().__init__()  # Call the __init__ method of BaseService
        self.base_obj = BaseService()

    def AnnotationFilter(self, request, context):
        print("yes this is 2 ")
        job_id = str(uuid.uuid4())  # Ensure job_id is a string
        self.base_obj.job_status[job_id] = {
            "job_id": job_id,
            "percentage": 100,
            "white_img_path": request.white_img_path,
            "black_img_path": request.black_img_path,
            "status_message": StatusMessage.JOB_STARTED.value,
            "completed": False,
            "error_message": "",
            "process_type": "annotation",
            "status_code": JobStatusCode.IN_PROGRESS.value,
        }
        print(self.base_obj.job_status[job_id])
        response = annotation_pb2.AnnotationResponse(**self.base_obj.job_status[job_id])
        return response
