from enum import Enum

class ChannelProcessingType(Enum):
    GRAYSCALE = "grayscale"
    COLOR_SWITCH = "color_switch"
    COLOR_CONVERSION = "color_conversion"
    EXTRACT_SINGLE_CHANNEL = "extract_single_channel"
    DISPLAY_SELECTED_CHANNEL = "display_selected_channels"

class StatusMessage(Enum):
    JOB_STARTED = "Job started"
    JOB_COMPLETED = "Job completed"
    JOB_CANCELLED = "Job cancelled"
    JOB_FAILED = "Job failed"
    JOB_NOT_FOUND = "Job Not Found"
