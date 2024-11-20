from enum import Enum


class DenoiseProcessType(Enum):
    AVERAGING = "averaging"
    GAUSSIAN_SMOOTHING = "gaussian_smoothing"
    BILATERAL_FILTERING = "bilateral_filtering"
    MEDIAN_FILTERING = "median_filtering"
    WIENER = "wiener"
