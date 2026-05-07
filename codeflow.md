# Code Flow: Request to Execution

This document provides a highly detailed, step-by-step walkthrough of what happens when a client sends an image processing request to the VTPL gRPC Server. It is essential reading for new developers contributing to or debugging the platform.

---

## 1. The Client Request

A client application creates a gRPC Stub (e.g., `AnnotationServiceStub`) and constructs a Protobuf Request message. 
For example, to run an annotation filter, the client sends an `AnnotationRequest`:
```protobuf
message AnnotationRequest {
    string in_img_path = 1;      // Folder containing source images
    string out_img_path = 2;     // Target output folder
    string white_img_path = 3;   // Algorithm specific parameter
    string black_img_path = 4;   // Algorithm specific parameter
    bool process_all_flag = 5;   // Whether to process all images in the folder
    repeated string in_img_list = 6; // Specific images to process if process_all is false
    bool is_preview_flag = 7;    // Marks if this is a high-priority preview task
}
```

## 2. Request Interception in the Service Layer

The request arrives at the corresponding Servicer in `grpc_service/annotation/annotation_service.py`.

1. The `AnnotationService` inherits from the auto-generated `AnnotationServiceServicer`.
2. It receives the request in the `AnnotationFilter(self, request, context)` method.
3. It immediately forwards the request to the singleton orchestrator, the `BaseService`.

```python
response = self.base_obj._start_image_processing_job(
    request,
    context,
    AnnotationProcessingType.ANNOTATE_WITH_BW.value,
    self.process_annotation_filter, # Callback to the actual processing logic
)
```

## 3. Deep Dive into a Service Class Implementation

To better understand how algorithms are integrated, let's look at the structure of a typical service class, such as `AnnotationService` (`grpc_service/annotation/annotation_service.py`):

### A. Initialization (`__init__`)
The class inherits from the auto-generated gRPC Servicer (`main_pb2_grpc.AnnotationServiceServicer`).
During initialization, it accesses the singleton `BaseService()` and instantiates the specific algorithm processor class (`annotate_process()` from `image_processing_algorithm`).

### B. The gRPC Method (`AnnotationFilter`)
This is the method defined in the `.proto` file. Its primary job is to act as a bridge. It immediately calls `self.base_obj._start_image_processing_job`, passing along:
- The incoming `request` and `context`.
- A constant defining the process type (e.g., `AnnotationProcessingType.ANNOTATE_WITH_BW.value`).
- A **callback method** (`self.process_annotation_filter`) that the `BaseService` thread pool will execute later.

### C. The Parameter Callback (`process_annotation_filter`)
When the background worker picks up the job, it triggers this callback. This method is responsible for unpacking the gRPC request into a standard Python dictionary (`adjust_params`). For example, it extracts `white_img_path` and `black_img_path`. It then forwards this to the actual execution method (`process_images`).

### D. The Execution Method (`process_images`)
This is where the actual multi-threaded work occurs for the given chunk of images:
1. **Thread Registration**: It locks the base object and records the current thread ID (`threading.get_ident()`) in the `job_status`.
2. **OpenCV Invocation**: It iterates over `img_chunk` (usually 1 image per chunk) and calls the instantiated processor (`self.processor.mod_annotate`), spreading the specific `**adjust_params`.
3. **Progress Increment**: Upon successful processing, it safely increments `processed_image_count` in the shared `job_status` dictionary using a thread lock.
4. **Error Handling**: If `cv2` or file operations fail, it catches the exception, updates the Redis status message to `FAILED`, and raises the error to terminate the specific chunk's execution.


## 4. Orchestration & Validation (`BaseService._start_image_processing_job`)

The `BaseService` takes over to standardize the job initialization:

1. **UUID Generation**: A unique `job_id` is created.
2. **Validation**: 
   - Verifies that `in_img_path` exists.
   - If `process_all_flag` is false, verifies all files in `in_img_list` exist.
   - Creates the `out_img_path` directory if it does not exist.
3. **Job Registration**: Creates the Job State dictionary (containing total images, percentage = 0.0, etc.) in a thread-safe manner using `self.lock`.
4. **Redis Push**: Pushes this initial state to Redis using `self.redis_client`.
5. **Immediate Return**: Generates a `JobStatusResponse` with the newly minted `job_id` and immediately returns it to the Service layer (and subsequently the client). **The gRPC call completes here from the client's perspective.**

## 5. Background Execution Pipeline

Before returning the initial response in Step 4, the `BaseService` spawns background tasks using its `ThreadPoolExecutor`.

### A. The Progress Monitor Loop
It submits `self.update_progress_in_redis` to the thread pool.
- This loop wakes up every 1 second.
- It checks the output folder (`out_img_path`) to see how many images have been created.
- It calculates the percentage: `(current_processed / total_images) * 100`.
- It saves the updated state to Redis.
- **Staleness Check**: If the output count hasn't changed for 300 loops, it marks the job as `FAILED`.
- **Completion Check**: Once `percentage == 100`, it marks the job `COMPLETED` and deletes it from the Python memory dictionary (leaving it in Redis for the client to retrieve).

### B. The Worker Queue
It pushes the image processing task into `self.priority_queue`.
- **Preview Flag**: If `is_preview_flag` is True, priority is `1` (High). Otherwise, priority is `10`.
- A worker method `_process_queue` constantly polls this priority queue.

## 6. Chunking and OpenCV Processing

Once the `_process_queue` worker picks up the job:

1. **Chunking**: It breaks down the list of images (`in_img_list`) into chunks of `1` image each.
2. **Batching by CPU Cores**: It submits these chunks to the thread pool in batches equal to `os.cpu_count() - 2`. It waits for the current batch to finish before submitting the next.
3. **Execution Callback**: For each image, the thread pool executes the callback passed in Step 2 (`self.process_annotation_filter`).
4. **OpenCV Call**: 
   This calls into `image_processing_algorithm/vid2img_annotate_x.py` where the actual `cv2` operations occur, saving the final file directly to disk.
5. **Increment**: The `processed_image_count` is manually incremented in the `job_status` dictionary using a thread lock.

## 7. Status Polling

Because the initial request (Step 4) only returned `job_id` and `0%`, the client must continually poll the server to get updates.
- The client calls `ChannelService.GetJobStatus(JobStatusRequest)`.
- The server checks Redis for the given `job_id` and returns the JSON payload containing the current `percentage`, `completed` flag, and `error` messages.
- The client knows to stop polling when `completed == True` or `status_message == "FAILED"`.
