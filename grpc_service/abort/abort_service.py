from stubs import channel_pb2 as channel_pb2
from stubs import main_pb2_grpc
from logging_config import setup_logging
from grpc_service.extract.extract_filter_type import ExtractProcessingType
from grpc_service.base.base_service import BaseService
import grpc
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
import threading
from stubs import abort_pb2, job_pb2
from datetime import datetime

logger = setup_logging()


class AbortService(main_pb2_grpc.AbortServiceServicer):
    def __init__(self):
        super().__init__()  # Initialize the mixin
        self.base_obj = BaseService()  # Singleton instance of BaseService

    def AbortProcess(self, request, context):
        try:
            with self.base_obj.lock:  # Thread-safe operation
                job_id = request.job_id
                if job_id in self.base_obj.job_status:
                    # Log the current job status
                    logger.info(
                        f"Job status for {job_id}: {self.base_obj.job_status[job_id]}"
                    )

                    # Update the job_status dictionary for the given job_id
                    self.base_obj.job_status[job_id].update(
                        {
                            "abort_event": True,
                            "status_message": StatusMessage.JOB_ABORTED.value,
                            "status_code": JobStatusCode.ABORTED.value,
                            "completed": False,  # The job was not completed
                            "error": f"Job {job_id} was aborted by user.",
                        }
                    )

                    # Log the updated job status
                    logger.info(
                        f"Updated job status for {job_id}: {self.base_obj.job_status[job_id]}"
                    )
                else:
                    # If the job_id is not found, return an AbortResponse
                    logger.warning(f"Job ID {job_id} not found for abort request.")
                    return abort_pb2.AbortResponse(
                        job_id=job_id,
                        message="Job ID not found.",
                        status_code=404,
                        error_details=f"No job found with ID {job_id}.",
                        timestamp=str(datetime.now()),
                    )
                self.base_obj.store_job_status_in_redis(
                    job_id, self.base_obj.job_status
                )

            # Return a success response to the client
            return abort_pb2.AbortResponse(
                job_id=job_id,
                message="Process aborted successfully.",
                status_code=200,
                error_details=None,
                timestamp=str(datetime.now()),
            )

        except Exception as e:
            # Log the exception
            logger.error(f"An error occurred while processing AbortProcess: {str(e)}")
            # Return an error response
            return abort_pb2.AbortResponse(
                job_id=request.job_id,
                message="An error occurred while aborting the process.",
                status_code=500,
                error_details=str(e),
                timestamp=str(datetime.now()),
            )
