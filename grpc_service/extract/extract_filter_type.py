from enum import Enum


class ExtractProcessingType(Enum):
    NEGATIVE = "negative"
    THRESHOLD = "threshold"
    ADAPTIVE_THRESHOLD = "adaptive_threshold"
    LAPLACE = "Laplace"
    PREWITT = "Prewitt"
    SOBEL = "Sobel"
    SCHARR = "Scharr"
    CANNY = "Canny"
    LINEAR_FILTER = "linear_filter"
    BILINEAR_FILTER = "bilinear_filter"
    CHANNEL_SELECTOR = "channel_selector"
    CHANNEL_DEMUX = "channel_demux"
    FOURIER = "fourier"

    # Add more process types as needed
