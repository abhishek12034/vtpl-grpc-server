from .adjust_filter_type import AdjustProcessingType
from stubs import main_pb2_grpc
from grpc_service.base.base_filter_type import StatusMessage
from image_processing_algorithm.vid2img_adjust_x import adjust_process
from grpc_service.base.base_service import BaseService
from logging_config import setup_logging
from utility.utility import list_image_files
import uuid
import threading
import grpc
logger = setup_logging()

class AdjustFilterService(BaseService, main_pb2_grpc.AdjustServiceServicer):
    def __init__(self):
        super().__init__()
        self.processor = adjust_process()

    def LevelControlFilter(self, request, context):
        return self._start_image_processing_job(
            request,context, AdjustProcessingType.LEVEL_CONTROL.value, self.process_level_control
        )

    def ContrastStretchFilter(self, request, context):
        return self._start_image_processing_job(
            request,context, AdjustProcessingType.CONTRAST_STRETCH.value, self.process_contrast_stretch
        )

    def ClaheFilter(self, request, context):
        return self._start_image_processing_job(
            request,context, AdjustProcessingType.CLAHE.value, self.process_clahe
        )
    
    def BrightnessContrastChangeFilter(self,request,context):
        return self._start_image_processing_job(
            request,context, AdjustProcessingType.BRIGHTNESS_CONTRAST_CHANGE.value, self.process_brightness_contrast_change
        )
    
    def IntensityChangeFilter(self, request, context):
        return self._start_image_processing_job(
            request,context, AdjustProcessingType.INTENSITY_VALUE_CHANGE.value, self.process_intensity_change
        )
    
    def SaturationChangeFilter(self, request, context):
         return self._start_image_processing_job(
            request,context, AdjustProcessingType.SATURATION_CHANGE.value, self.process_saturation_change
        )
    
    def HueSatValChangeFilter(self, request, context):
        return self._start_image_processing_job(
            request,context, AdjustProcessingType.HUE_SAT_VAL_CHANGE.value, self.process_hue_sat_val_change
        )
    
    def ExposureControlFilter(self, request, context):
          return self._start_image_processing_job(
            request,context, AdjustProcessingType.EXPOSURE_CONTROL.value, self.process_exposure_control
        )
    def HueChangeFilter(self, request, context):
        return self._start_image_processing_job(
            request,context, AdjustProcessingType.HUE_CHANGE.value, self.process_hue_change
        )
    def CurveFilter(self, request, context):
        return self._start_image_processing_job(
            request,context, AdjustProcessingType.CURVE.value, self.process_curve
        )
    def HistogramEqualizationFilter(self, request, context):
        return self._start_image_processing_job(
            request,context, AdjustProcessingType.HISTOGRAM_EQUALIZATION.value, self.process_histogram_equalization
        )
    
    def process_images(self, request, job_id, process_type, adjust_params):
        try:

            # List images based on the flag
            in_img_list = request.in_img_list
            if request.process_all_flag:
                in_img_list = list_image_files(request.in_img_path)

            # Store thread ID in job status
            with self.lock:
                self.job_status[job_id]['thread_id'] = threading.get_ident()
                self.job_status[job_id]['status_message'] = StatusMessage.JOB_STARTED.value
                self.job_status[job_id]['total_images'] = len(in_img_list)
                self.store_job_status_in_redis(job_id, self.job_status[job_id])

            # Process each image in the list
            for in_img in in_img_list:
                self.processor.mod_adjust(   
                    process_all_flag=False, 
                    in_img_path = request.in_img_path,
                    out_img_path = request.out_img_path,      
                    in_img_list=[in_img],
                    **adjust_params  # Pass specific filter parameters
                )

                # Update processed image count
                with self.lock:
                    self.job_status[job_id]['processed_image_count'] += 1
                    self.job_status[job_id]['percentage'] = (
                        self.job_status[job_id]['processed_image_count'] / 
                        self.job_status[job_id]['total_images'] * 100
                    )
                    self.store_job_status_in_redis(job_id, self.job_status[job_id])

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
                raise e

    def process_level_control(self, request,context, job_id, process_type):
        try:
            
            self.processor.mod_adjust(
                
                in_level_st = request.in_level_st,
                in_level_mid= request.in_level_mid,
                in_level_en= request.in_level_en,
                out_level_st= request.out_level_st,
                out_level_en= request.out_level_en,
                process_type=AdjustProcessingType.LEVEL_CONTROL_SET_LINES.value
                
            )
            adjust_params = {
                "level_control_set_lines_flag": False,
                "process_type" : process_type

            }
            self.process_images(request, job_id, process_type, adjust_params)

        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")
    def process_exposure_control(self, request,context, job_id, process_type):
        try:
            
            self.processor.mod_adjust(
                           
                exposure_times= request.exposure_times,
                process_type=AdjustProcessingType.EXPOSURE_CONTROL_SET_SPLINE.value
                
            )
            adjust_params = {
            "set_exposure_curve_flag": False,
            "process_type":process_type

            }
            self.process_images(request, job_id, process_type, adjust_params)

        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")
    def process_curve(self, request,context, job_id, process_type):
        try:
            
            self.processor.mod_adjust(
                           
                curve_x_list= request.curve_x_list,
                curve_y_list=request.curve_y_list,
                process_type=AdjustProcessingType.CURVE_SET_SPLINE.value
                
            )
            adjust_params = {
            "curve_set_spline_flag": False,
            "process_type":process_type,
            "curve_color_ch_red":request.curve_color_ch_red,
            "curve_color_ch_green":request.curve_color_ch_green,
            "curve_color_ch_blue":request.curve_color_ch_blue

            }
            self.process_images(request, job_id, process_type, adjust_params)

        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")


    def process_brightness_contrast_change(self, request,context, job_id, process_type):
        try:
            
            adjust_params = {
                "brightness_amount_change" : request.brightness_amount_change,
                "contrast_change_factor" : request.contrast_change_factor,
                "process_type" : process_type

            }
            self.process_images(request, job_id, process_type, adjust_params)

        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")

    def process_intensity_change(self, request,context, job_id, process_type):
        try:
            
            adjust_params = {
                "intensity_value_amount_change" : request.intensity_value_amount_change,        

                "process_type" : process_type

            }
            self.process_images(request, job_id, process_type, adjust_params)

        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")

            
    def process_saturation_change(self, request,context, job_id, process_type):
        try:
            
            adjust_params = {
                "saturation_times_change" : request.saturation_times_change,        
                "process_type" : process_type

            }
            self.process_images(request, job_id, process_type, adjust_params)

        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")


    def process_hue_change(self, request,context, job_id, process_type):
        try:
            
            adjust_params = {
                "hue_degree_change" : request.hue_degree_change,        
                "process_type" : process_type

            }
            self.process_images(request, job_id, process_type, adjust_params)

        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")

    def process_hue_sat_val_change(self, request,context, job_id, process_type):
        try:
            
            adjust_params = {
                "intensity_value_amount_change" : request.intensity_value_amount_change,        
                "hue_degree_change" : request.hue_degree_change,
              "saturation_times_change" : request.saturation_times_change,
                "process_type" : process_type

            }
            self.process_images(request, job_id, process_type, adjust_params)

        except Exception as e:
            # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")


    def process_contrast_stretch(self, request,context, job_id, process_type):
        try:
            adjust_params = {
                "in_con_stretch_amt": request.in_con_stretch_amt,
                "process_type" : process_type

            }
            self.process_images(request, job_id, process_type, adjust_params)
        except Exception as e:
             # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")


    def process_clahe(self, request,context, job_id, process_type):
        try:
            adjust_params = {
                "in_clip_limit": request.in_clip_limit,
                "grid_row": request.grid_row,
                "grid_col": request.grid_col,
                "process_type" : process_type
            }
            print("Hello from clahe")

            self.process_images(request, job_id, process_type, adjust_params)
        except Exception as e:
             # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")
    def process_histogram_equalization(self, request,context, job_id, process_type):
        try:
            adjust_params = {

                 "in_st_row":  request.in_st_row,
                "in_en_row":request.in_en_row,
                "in_st_col":request.in_st_col,
                "in_en_col":request.in_en_col,
                "process_type" : process_type,
                "histogram_calc_on_full_img_flag":request.histogram_calc_on_full_img_flag
            }

            self.process_images(request, job_id, process_type, adjust_params)
        except Exception as e:
             # Handle general errors and return a more generic error message
            logger.error(f"Error occurred while handling params: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal error occurred during job initialization")