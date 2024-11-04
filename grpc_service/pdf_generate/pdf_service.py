from stubs import channel_pb2 as channel_pb2
from stubs import pdf_generate_pb2
from stubs import main_pb2
from stubs import main_pb2_grpc
from report_generator.report_generate_v2 import GenerateReport
import time


class PDFGenerateService(main_pb2_grpc.PDFGenerateServiceServicer):
    def __init__(self):
        pass  # You can also call everything from here as well by passing request, there is no need of PDFGeneration function.

    def PDFGeneretion(self, request, context):
        print("REQUEST :", request)
        report_obj = GenerateReport(request)
        report_obj.generate_report()

        response = pdf_generate_pb2.PDFGenerateResponse(
            status_code=200,
            status_message="PDF generated successfully",
            pdf_url=request.out_docs_path,
            error_details="",
        )

        # Return the response
        return response
