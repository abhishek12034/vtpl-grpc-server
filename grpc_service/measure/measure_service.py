import logging
from stubs import main_pb2_grpc
from stubs import measure_pb2, measure_pb2_grpc
from image_processing_algorithm.vid2img_measure_X import measure_process
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class MeasureService(main_pb2_grpc.MeasureServiceServicer):
    def __init__(self):
        self.processor = measure_process()

    def MeasureOneD(self, request, context):
        try:
            logger.info(f"Received MeasureOneD request.{request}")

            # Extract points from the request
            cal_points = request.in_calc_dual_pt_rc_list.points
            ref_points = request.in_ref_dual_pt_rc_list.points

            logger.info(f"Calibration Points: {cal_points}")
            logger.info(f"Reference Points: {ref_points}")

            # Convert points to the desired format
            in_calc_dual_pt_rc_list = [[point.x, point.y] for point in cal_points]
            in_ref_dual_pt_rc_list = [[point.x, point.y] for point in ref_points]

            logger.info(
                "Calling processor.mod_measure() with provided points and image paths."
            )
            self.processor.mod_measure(
                in_img_path=request.in_img_path,
                in_img_list=["t1.png"],
                process_all_flag=False,
                process_type="measure1D",
                in_ref_dual_pt_rc_list=in_ref_dual_pt_rc_list,
                in_calc_dual_pt_rc_list=in_calc_dual_pt_rc_list,
                in_ref_val=68,
                out_img_path=request.out_img_path,
            )

            logger.info(
                f"Processing completed. Calculated reference value: {self.processor.calc_ref_val}"
            )

            # Create response
            response = measure_pb2.MeasureResponse(
                job_id="12345",  # Job identifier
                percentage=75.5,  # Percentage of the task completed
                input_image_path=request.in_img_path,  # Path to the input image
                output_image_path=request.out_img_path,  # Path to the output image
                total_input_images=1,  # Total number of input images
                processed_image_count=100,  # Number of processed images
                status_message=StatusMessage.JOB_COMPLETED.value,  # Status message
                completed=True,  # Completion status (True in this case)
                error_message="",  # Error message (empty string here)
                process_type="measure1D",  # Type of processing (e.g., "resize")
                status_code=JobStatusCode.COMPLETED.value,  # Status code (e.g., HTTP-like status code)
                object_length=self.processor.calc_ref_val,  # Length of the object (using the processed result)
            )

            logger.info(f"Returning response: {response}")
            return response

        except Exception as e:
            # Log the exception
            logger.error(f"An error occurred: {e}", exc_info=True)

            # Return a failed response with error message
            response = measure_pb2.MeasureResponse(
                job_id="12345",
                percentage=0.0,
                input_image_path=request.in_img_path,
                output_image_path=request.out_img_path,
                total_input_images=0,
                processed_image_count=0,
                status_message=StatusMessage.JOB_FAILED.value,  # Status message
                completed=False,
                error_message=str(e),  # Error message from exception
                process_type="measure1D",
                status_code=JobStatusCode.FAILED.value,  # Failed status code
                object_length=0.0,  # No calculated length
            )

            return response
