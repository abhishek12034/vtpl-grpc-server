import grpc
from concurrent import futures
from grpc_service.channel.channel_service import ChannelService
from grpc_service.adjust.adjust_service import AdjustFilterService
from grpc_service.extract.extract_service import ExtractService
from grpc_service.pdf_generate.pdf_service import PDFGenerateService
from grpc_service.measure.measure_service import MeasureService
from grpc_service.edit.edit_service import EditService
from grpc_service.sharpen.sharpen_service import SharpenService
from grpc_service.denoise.denoise_service import DenoiseService
from grpc_service.stablization.stablization_service import StablizationService

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
    main_pb2_grpc.add_MeasureServiceServicer_to_server(MeasureService(), server)
    main_pb2_grpc.add_EditServiceServicer_to_server(EditService(), server)
    main_pb2_grpc.add_SharpenServiceServicer_to_server(SharpenService(), server)
    main_pb2_grpc.add_DenoiseServiceServicer_to_server(DenoiseService(), server)
    main_pb2_grpc.add_StablizationServiceServicer_to_server(
        StablizationService(), server
    )

    port = os.getenv("GRPC_SERVER_PORT", "5012")
    server.add_insecure_port(f"[::]:{port}")

    print(f"Server is running on port {port}...")

    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server is shutting down...")


if __name__ == "__main__":
    serve()
