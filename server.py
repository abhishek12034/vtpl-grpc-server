import grpc
from concurrent import futures
from grpc_service.channel.channel_service import ImageProcessingService
from stubs import main_pb2_grpc
from logging_config import setup_logging  # Import the centralized logging config

def serve():
    logger = setup_logging()  # Setup logging once at the start

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    main_pb2_grpc.add_ImageProcessingServicer_to_server(ImageProcessingService(), server)
    server.add_insecure_port('[::]:50051')

    # Log that the server has started
    print("Server is running on port 50051...")

    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server is shutting down...")

if __name__ == '__main__':
    serve()
