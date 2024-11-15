from enum import Enum


class EditProcessingType(Enum):
    CROP = "crop"
    FLIP = "flip"
    ROTATE = "rotate"
    RESIZE = "resize"
    SMART_RESIZE = "smart_resize"
    PERSPECTIVE = "perspective"
    UNDISTORT = "undistort"
    CORRECT_ASPECT_RATIO = "correct_aspect_ratio"
    CORRECT_FISHEYE = "correct_fisheye"
