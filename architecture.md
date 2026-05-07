# Architecture Documentation: VTPL gRPC Server

This document provides an in-depth architectural breakdown of the VTPL gRPC Server. It is designed to help new joiners understand how the components interact, the role of each module, and the underlying design patterns used to handle concurrent image processing workloads.

## 1. System Overview

The VTPL gRPC Server is a high-performance Python application built to provide remote access to a suite of OpenCV-based image enhancement and processing algorithms. The server implements an asynchronous, thread-pooled architecture to efficiently process large batches of images while continuously streaming progress back to the client via a Redis datastore.

### Core Technologies
- **Python 3.10**: Core programming language.
- **gRPC / Protocol Buffers (protobuf)**: Used for inter-process communication, defining strict API contracts between the client and the Python server.
- **Redis**: An in-memory key-value store used to maintain job state and progress for horizontal scalability and fast polling.
- **OpenCV (cv2)**: The underlying engine for all image manipulation algorithms.
- **Docker & Docker Compose**: Containerization for standardized deployments.

---

## 2. Directory Structure

Understanding the layout of the repository is crucial for navigation:

- `protos/`: Contains all `.proto` files defining the gRPC services and message schemas. `main.proto` aggregates all individual service definitions.
- `stubs/`: Contains the auto-generated Python code (`*_pb2.py` and `*_pb2_grpc.py`) created from the protobuf files. **Do not modify these manually.**
- `grpc_service/`: The gRPC server implementation layer. It handles incoming requests, calls the base service, and maps to the actual processing algorithms.
  - `base/base_service.py`: The core orchestrator. Manages thread pools, job tracking, and Redis updates.
  - `<feature>/<feature>_service.py`: Service-specific handlers (e.g., `annotation_service.py`).
- `image_processing_algorithm/`: Pure Python modules containing the OpenCV logic. These scripts are invoked by the gRPC service layer. Examples: `vid2img_adjust_x.py`, `vid2img_denoise_x.py`.
- `config/`: Configuration files (like `redis_config.py`).
- `utility/`: Shared helper functions (e.g., file counting, list chunking).
- `server.py`: The main entry point that starts the gRPC server and registers all servicers.

---

## 3. gRPC Services (API Layer)

The system exposes 13 distinct services, defined in `protos/main.proto`. Each service handles a specific category of image manipulation:

1. **ChannelService**: Grayscale, color switching, channel extraction.
2. **AdjustService**: Level control, contrast stretching, CLAHE, brightness/intensity/hue/saturation changes, curves, histogram equalization.
3. **ExtractService**: Thresholding, Laplace, Prewitt, Sobel, Canny, Linear/Bilinear filters, Fourier.
4. **PDFGenerateService**: Generates PDF reports from images.
5. **MeasureService**: 1D, 2D, and 3D image measurements.
6. **EditService**: Cropping, flipping, rotating, resizing, perspective correction, fisheye handling.
7. **SharpenService**: Laplacian sharpening, unsharp masking.
8. **DenoiseService**: Averaging, Gaussian smoothing, Bilateral, Median, and Wiener filters.
9. **StablizationService**: Local and global video/image stabilization.
10. **DeblurService**: Motion and optical deblurring.
11. **AnnotationService**: Image annotation based on black/white overlay inputs.
12. **AbortService**: Specialized service to gracefully kill running jobs.

---

## 4. Core Component: Base Service (`grpc_service/base/base_service.py`)

The `BaseService` is the heartbeat of the application. It employs the **Singleton Pattern** so that all gRPC servicers share the same thread pool and job state dictionary.

### Key Responsibilities:
- **Thread Pool Management**: Maintains a `ThreadPoolExecutor(max_workers=100)`. This pool is responsible for both executing the image processing chunks and running the background progress-monitoring loops.
- **Priority Queue**: Incorporates a `PriorityQueue`. Jobs marked as `is_preview_flag=True` get a priority of `1` (higher), while bulk jobs get a priority of `10`. This allows quick previews to interrupt or run alongside massive bulk tasks.
- **Concurrency Limiting**: During batch processing, images are chunked. The server dynamically calculates maximum concurrency based on CPU cores (`os.cpu_count() - 2`) to prevent CPU starvation.
- **Redis Synchronization**: Synchronizes an in-memory `job_status` dictionary to Redis.

### State Management schema (Redis/Memory)
When a job is started, a JSON object like this is maintained in memory and pushed to Redis:
```json
{
  "job_id": "uuid-string",
  "percentage": 45,
  "in_img_path": "/path/to/input",
  "out_img_path": "/path/to/output",
  "total_images": 1000,
  "processed_image_count": 450,
  "status_message": "IN_PROGRESS",
  "process_type": "ANNOTATE_WITH_BW",
  "completed": false,
  "error": null,
  "thread_id": [1234567890],
  "status_code": 2,
  "abort_event": false
}
```

---


## 6. Error Handling and "Staleness" Detection

If an OpenCV process hangs or fails silently on a corrupted image, `BaseService` handles this gracefully via **Staleness Tracking**. 
The `update_progress_in_redis` loop expects the `processed_image_count` to change. If it remains identical for `300` iterations (roughly 5 minutes), the server assumes a hang, terminates monitoring, and marks the job as `FAILED` in Redis.
