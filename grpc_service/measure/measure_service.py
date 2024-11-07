from stubs import main_pb2_grpc
from stubs import measure_pb2, measure_pb2_grpc


class MeasureService(main_pb2_grpc.MeasureServiceServicer):
    def MeasureOneD(self, request, context):
        return measure_pb2_grpc.MeasureResponse()
