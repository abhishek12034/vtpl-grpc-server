import grpc
from concurrent import futures
from grpc_service.channel.channel_service import ChannelService
from grpc_service.adjust.adjust_service import AdjustFilterService
from grpc_service.extract.extract_service import ExtractService
from grpc_service.pdf_generate.pdf_service import PDFGenerateService
from stubs import main_pb2_grpc
from logging_config import setup_logging  # Import the centralized logging config
import os


def serve():
    logger = setup_logging()  # Setup logging once at the start

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    main_pb2_grpc.add_ChannelServiceServicer_to_server(ChannelService(), server)
    main_pb2_grpc.add_AdjustServiceServicer_to_server(AdjustFilterService(), server)
    main_pb2_grpc.add_ExtractServiceServicer_to_server(ExtractService(), server)
    main_pb2_grpc.add_PDFGenerateServiceServicer_to_server(PDFGenerateService(), server)

    # Log that the server has started
    port = os.getenv("GRPC_SERVER_PORT", "50051")
    server.add_insecure_port(f"[::]:{port}")

    print(f"Server is running on port {port}...")

    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server is shutting down...")


if __name__ == "__main__":
    serve()
