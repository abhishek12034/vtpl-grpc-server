from stubs import channel_pb2 as channel_pb2
from stubs import pdf_generate_pb2
from stubs import main_pb2
from stubs import main_pb2_grpc
from report_generator.report_generate_v1 import GenerateReport
import time


class PDFGenerateService(main_pb2_grpc.PDFGenerateServiceServicer):
    def __init__(self):
        self.pdf_generate_obj = GenerateReport

    def PDFGeneretion(self, request, context):

        print(type(request), request)
        # Here We have to call PDF Generation Code
        # self.pdf_generate_obj.generate_report(
        #     request.processes, request.processes_meta, request.out_pdf_path
        # )
        # Create the response object
        response = pdf_generate_pb2.PDFGenerateResponse(
            status_code=200,
            status_message="PDF generated successfully",
            pdf_url=request.out_pdf_path,
            error_details="",
        )

        # Return the response
        return response
