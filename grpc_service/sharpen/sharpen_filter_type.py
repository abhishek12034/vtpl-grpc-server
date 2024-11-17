from enum import Enum


# Define an enum for process types
class SharpenProcessingType(Enum):
    LAPLACIAN_SHARPEN = "laplacian_sharpen"
    UNSHARP_MASK = "unsharp_mask"
