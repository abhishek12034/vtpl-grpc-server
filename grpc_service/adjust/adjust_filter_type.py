from enum import Enum

from enum import Enum

class AdjustProcessingType(Enum):
    EXPOSURE_CONTROL_SET_SPLINE = "exposure_control_set_spline" #Done
    CURVE_SET_SPLINE = "curve_set_spline" #Done
    LEVEL_CONTROL_SET_LINES = "level_control_set_lines" #Done
    WRITE_CURVE_MAP_ARR_IMAGE = "write_curve_map_arr_image"
    CONTRAST_CHANGE = "contrast_change"
    BRIGHTNESS_CHANGE = "brightness_change"
    BRIGHTNESS_CONTRAST_CHANGE = "brightness_contrast_change" #Done
    EXPOSURE_CONTROL = "exposure_control" #Done
    HUE_CHANGE = "hue_change" #Done
    SATURATION_CHANGE = "saturation_change" #Done
    INTENSITY_VALUE_CHANGE = "intensity_value_change" #Done
    HUE_SAT_VAL_CHANGE = "hue_sat_val_change" # Done
    CURVE = "curve" #Done
    LEVEL_CONTROL = "level_control" #Done
    HISTOGRAM_EQUALIZATION = "histogram_equalization" #Done
    CLAHE = "CLAHE"#Done
    CONTRAST_STRETCH = "contrast_stretch"#Done
