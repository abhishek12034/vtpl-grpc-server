import grpc
import time
from stubs import channel_pb2
from stubs import channel_pb2_grpc

def run():
    # Create a channel to the server
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = channel_pb2_grpc.ImageProcessingServiceStub(channel)

        # Prepare the request
        request = channel_pb2.GrayscaleRequest(
            in_img_path="/home/vadmin/Documents/grpc_ips/output_frames",
            process_all_flag=True,
            in_img_list=["frm000000.jpg", "frm000001.jpg"],  # Replace with actual image file names
            out_img_path="/home/vadmin/Documents/grpc_ips/vid_2"
        )

        # Call the Grayscale method and handle streaming responses
        response_iterator = stub.Grayscale(request)

        for response in response_iterator:
            print(f"Processed Image Count: {response.processed_image_count}")
            print(f"Status Message: {response.status_message}")
            print(f"Total Time: {response.total_time:.2f}s")
            print(f"Reading Time: {response.reading_time:.2f}s")
            print(f"Writing Time: {response.writing_time:.2f}s")
            print(f"Processing Time: {response.processing_time:.2f}s")

if __name__ == '__main__':
    run()
