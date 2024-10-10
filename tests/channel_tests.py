import unittest
from unittest.mock import Mock
from stubs import main_pb2, main_pb2_grpc, job_pb2, channel_pb2
import grpc
from grpc_service.channel.channel_service import ChannelService


class TestServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.service = ChannelService()
        self.context = Mock()

    def test_grayscale_request_and_response(self):
        request = channel_pb2.GrayScaleRequest(
            in_img_path="/home/vadmin/Documents/vtpl_grpc_server/vid_1",
            process_all_flag=False,
            in_img_list=["frm000000.jpg"],
            out_img_path="/home/vadmin/Documents/vtpl_grpc_server/vid_2",
        )

        response = self.service.GrayscaleFilter(request, self.context)
        print(response)
        self.assertEqual(response.process_type, "grayscale")

        # Ensure no errors were reported
        self.context.set_code.assert_not_called()


if __name__ == "__main__":
    unittest.main()
