from stubs import main_pb2_grpc
from stubs import measure_pb2, measure_pb2_grpc
from image_processing_algorithm.vid2img_measure_X import measure_process
from grpc_service.base.base_filter_type import StatusMessage, JobStatusCode
import uuid
from logging_config import setup_logging
from grpc_service.base.base_service import BaseService
from grpc_service.measure.measure_filter import MeasureProcessingType

logger = setup_logging()


class MeasureService(main_pb2_grpc.MeasureServiceServicer):
    def __init__(self):
        super().__init__()  # Ensure parent class initialization, if any
        self.processor = measure_process()
        self.base_obj = BaseService()

    def MeasureOneD(self, request, context):
        logger.info(f"Measure 1D Request Object {request}")
        job_id = str(uuid.uuid4())  # Ensure job_id is a string
        self.base_obj.job_status[job_id] = {
            "job_id": job_id,
            "percentage": 100,
            "input_image_path": request.in_img_path,
            "output_image_path": request.out_img_path,
            "total_input_images": len(request.in_img_list),
            "processed_image_count": 0,
            "status_message": StatusMessage.JOB_STARTED.value,
            "completed": False,
            "error_message": "",
            "process_type": MeasureProcessingType.MEASURE_1D.value,
            "status_code": JobStatusCode.IN_PROGRESS.value,
            "object_length": 0.0,
        }

        try:
            self.base_obj.store_job_status_in_redis(
                job_id, self.base_obj.job_status[job_id]
            )

            logger.info(f"Received MeasureOneD request: {request}")

            # Extract points from the request
            cal_points = request.in_calc_dual_pt_rc_list.points
            ref_points = request.in_ref_dual_pt_rc_list.points

            logger.info(f"Calibration Points: {cal_points}")
            logger.info(f"Reference Points: {ref_points}")

            # Convert points to the desired format
            in_calc_dual_pt_rc_list = [[point.row, point.col] for point in cal_points]
            in_ref_dual_pt_rc_list = [[point.row, point.col] for point in ref_points]

            logger.info(
                "Calling processor.mod_measure() with provided points and image paths."
            )
            self.processor.mod_measure(
                in_img_path=request.in_img_path,
                in_img_list=list(request.in_img_list),
                process_all_flag=False,
                process_type=MeasureProcessingType.MEASURE_1D.value,
                in_ref_dual_pt_rc_list=in_ref_dual_pt_rc_list,
                in_calc_dual_pt_rc_list=in_calc_dual_pt_rc_list,
                in_ref_val=request.in_ref_val,
                out_img_path=request.out_img_path,
            )

            logger.info(
                f"Processing completed. Calculated reference value: {self.processor.calc_ref_val}"
            )

            # Update job status with completed details
            self.base_obj.job_status[job_id][
                "status_message"
            ] = StatusMessage.JOB_COMPLETED.value
            self.base_obj.job_status[job_id]["completed"] = True
            self.base_obj.job_status[job_id][
                "status_code"
            ] = JobStatusCode.COMPLETED.value
            self.base_obj.job_status[job_id]["object_length"] = round(
                self.processor.calc_ref_val, 2
            )

            self.base_obj.job_status[job_id]["processed_image_count"] = len(
                request.in_img_list
            )

            # Create response
            response = measure_pb2.MeasureResponse(**self.base_obj.job_status[job_id])

            logger.info(f"Returning response: {response}")
            print(
                self.base_obj.job_status[job_id]["object_length"],
                self.base_obj.job_status[job_id],
                response,
            )
            self.base_obj.store_job_status_in_redis(
                job_id, self.base_obj.job_status[job_id]
            )

            return response

        except Exception as e:
            # Log the exception
            logger.error(f"An error occurred: {e}", exc_info=True)

            # Update job status with failure details
            self.base_obj.job_status[job_id][
                "status_message"
            ] = StatusMessage.JOB_FAILED.value
            self.base_obj.job_status[job_id]["completed"] = False
            self.base_obj.job_status[job_id]["status_code"] = JobStatusCode.FAILED.value
            self.base_obj.job_status[job_id]["error_message"] = str(e)

            # Create response
            response = measure_pb2.MeasureResponse(**self.base_obj.job_status[job_id])
            self.base_obj.store_job_status_in_redis(
                job_id, self.base_obj.job_status[job_id]
            )

            return response

    def MeasureTwoD(self, request, context):
        logger.info(f"Measure 2D Request Object {request}")

        job_id = str(uuid.uuid4())  # Ensure job_id is a string
        self.base_obj.job_status[job_id] = {
            "job_id": job_id,
            "percentage": 100,
            "input_image_path": request.in_img_path,
            "output_image_path": request.out_img_path,
            "total_input_images": 1,
            "processed_image_count": 0,
            "status_message": StatusMessage.JOB_STARTED.value,
            "completed": False,
            "error_message": "",
            "process_type": MeasureProcessingType.MEASURE_2D.value,
            "status_code": JobStatusCode.IN_PROGRESS.value,
            "object_length": 0.0,
        }
        self.base_obj.store_job_status_in_redis(
            job_id, self.base_obj.job_status[job_id]
        )
        try:
            logger.info(f"Received MeasureOneD request: {request}")

            # Extract points from the request
            cal_points = request.in_calc_dual_pt_rc_list.points
            ref_points = request.in_ref_dual_pt_rc_list.points

            logger.info(f"Calibration Points: {cal_points}")
            logger.info(f"Reference Points: {ref_points}")

            # Convert points to the desired format
            in_calc_dual_pt_rc_list = [[point.row, point.col] for point in cal_points]
            in_ref_dual_pt_rc_list = [[point.row, point.col] for point in ref_points]
            logger.info(
                "Calling processor.mod_measure() with provided points and image paths."
            )
            self.processor.mod_measure(
                in_img_path=request.in_img_path,
                in_img_list=list(request.in_img_list),
                process_all_flag=False,
                process_type=MeasureProcessingType.MEASURE_2D.value,
                in_ref_dual_pt_rc_list=in_ref_dual_pt_rc_list,
                in_calc_dual_pt_rc_list=in_calc_dual_pt_rc_list,
                in_ref_val_list=request.in_ref_val_list,
                out_img_path=request.out_img_path,
            )

            logger.info(
                f"Processing completed. Calculated reference value: {self.processor.calc_ref_val}"
            )

            # Update job status with completed details
            self.base_obj.job_status[job_id][
                "status_message"
            ] = StatusMessage.JOB_COMPLETED.value
            self.base_obj.job_status[job_id]["completed"] = True
            self.base_obj.job_status[job_id][
                "status_code"
            ] = JobStatusCode.COMPLETED.value
            self.base_obj.job_status[job_id]["object_length"] = round(
                self.processor.calc_ref_val, 2
            )
            self.base_obj.job_status[job_id]["processed_image_count"] = len(
                request.in_img_list
            )

            # Create response
            response = measure_pb2.MeasureResponse(**self.base_obj.job_status[job_id])

            logger.info(f"Returning response: {response}")
            self.base_obj.store_job_status_in_redis(
                job_id, self.base_obj.job_status[job_id]
            )
            return response

        except Exception as e:
            # Log the exception
            logger.error(f"An error occurred: {e}", exc_info=True)

            # Update job status with failure details
            self.base_obj.job_status[job_id][
                "status_message"
            ] = StatusMessage.JOB_FAILED.value
            self.base_obj.job_status[job_id]["completed"] = False
            self.base_obj.job_status[job_id]["status_code"] = JobStatusCode.FAILED.value
            self.base_obj.job_status[job_id]["error_message"] = str(e)

            self.base_obj.store_job_status_in_redis(
                job_id, self.base_obj.job_status[job_id]
            )
            response = measure_pb2.MeasureResponse(**self.base_obj.job_status[job_id])

            return response

    def MeasureThreeD(self, request, context):
        logger.info(f"Measure 3D Request Object {request}")

        job_id = str(uuid.uuid4())  # Ensure job_id is a string
        self.base_obj.job_status[job_id] = {
            "job_id": job_id,
            "percentage": 100,
            "input_image_path": request.in_img_path,
            "output_image_path": request.out_img_path,
            "total_input_images": 1,
            "processed_image_count": 0,
            "status_message": StatusMessage.JOB_STARTED.value,
            "completed": False,
            "error_message": "",
            "process_type": MeasureProcessingType.MEASURE_3D.value,
            "status_code": JobStatusCode.IN_PROGRESS.value,
            "object_length": 0.0,
        }
        self.base_obj.store_job_status_in_redis(
            job_id, self.base_obj.job_status[job_id]
        )
        try:
            logger.info(f"Received MeasureOneD request: {request}")

            # Extract points from the request data
            cal_points = request.in_calc_line_rc.points
            ref_points_lists = [item.points for item in request.in_ref_line_rc_list]
            # Log calibration points
            logger.info(f"Calibration Points: {cal_points}")
            logger.info(f"Reference Points: {ref_points_lists}")

            # Convert calibration points to desired format
            in_calc_line_rc = [[point.row, point.col] for point in cal_points]

            # Convert reference points to desired format for each set in the list
            in_ref_line_rc_list = [
                [[point.row, point.col] for point in ref_points]
                for ref_points in ref_points_lists
            ]

            logger.info(
                "Calling processor.mod_measure() with provided points and image paths."
            )
            self.processor.mod_measure(
                in_img_path=request.in_img_path,
                in_img_list=list(request.in_img_list),
                process_all_flag=False,
                process_type=MeasureProcessingType.MEASURE_3D.value,
                in_ref_line_rc_list=in_ref_line_rc_list,  # Use this instead of in_ref_line_rc_points_list
                in_calc_line_rc=in_calc_line_rc,
                in_ref_base_ht_mesr_list=request.in_ref_base_ht_mesr_list,
                out_img_path=request.out_img_path,
            )

            logger.info(
                f"Processing completed. Calculated reference value: {self.processor.calc_ref_val}"
            )

            # Update job status with completed details
            self.base_obj.job_status[job_id][
                "status_message"
            ] = StatusMessage.JOB_COMPLETED.value
            self.base_obj.job_status[job_id]["completed"] = True
            self.base_obj.job_status[job_id][
                "status_code"
            ] = JobStatusCode.COMPLETED.value
            self.base_obj.job_status[job_id]["object_length"] = round(
                self.processor.calc_ref_val, 2
            )
            self.base_obj.job_status[job_id]["processed_image_count"] = len(
                request.in_img_list
            )

            # Create response
            response = measure_pb2.MeasureResponse(**self.base_obj.job_status[job_id])

            logger.info(f"Returning response: {response}")
            self.base_obj.store_job_status_in_redis(
                job_id, self.base_obj.job_status[job_id]
            )
            return response

        except Exception as e:
            # Log the exception
            logger.error(f"An error occurred: {e}", exc_info=True)

            # Update job status with failure details
            self.base_obj.job_status[job_id][
                "status_message"
            ] = StatusMessage.JOB_FAILED.value
            self.base_obj.job_status[job_id]["completed"] = False
            self.base_obj.job_status[job_id]["status_code"] = JobStatusCode.FAILED.value
            self.base_obj.job_status[job_id]["error_message"] = str(e)

            self.base_obj.store_job_status_in_redis(
                job_id, self.base_obj.job_status[job_id]
            )
            response = measure_pb2.MeasureResponse(**self.base_obj.job_status[job_id])

            return response
