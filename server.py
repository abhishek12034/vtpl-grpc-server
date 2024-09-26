import grpc
from concurrent import futures
from services.channel_service import ImageProcessingServiceServicer
from stubs import main_pb2_grpc
from logging_config import setup_logging  # Import the centralized logging config

def serve():
    logger = setup_logging()  # Setup logging once at the start

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    main_pb2_grpc.add_ImageProcessingServiceServicer_to_server(ImageProcessingServiceServicer(), server)
    server.add_insecure_port('[::]:50051')

    # Log that the server has started
    logger.info("Server is running on port 50051...")

    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server is shutting down...")

if __name__ == '__main__':
    serve()
