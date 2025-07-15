import unittest
from .model_get_rebase_req import GetRebaseReq
from .model_get_rebase_resp import GetRebaseResp
from kucoin_universal_sdk.model.common import RestResponse


class APIBrokerAPITest(unittest.TestCase):

    def test_get_rebase_req_model(self):
        """
       get_rebase
       Get Broker Rebate
       /api/v1/broker/api/rebase/download
       """
        data = "{\"begin\": \"20240610\", \"end\": \"20241010\", \"tradeType\": \"1\"}"
        req = GetRebaseReq.from_json(data)

    def test_get_rebase_resp_model(self):
        """
        get_rebase
        Get Broker Rebate
        /api/v1/broker/api/rebase/download
        """
        data = "{\n    \"code\": \"200000\",\n    \"data\": {\n        \"url\": \"https://kc-v2-promotion.s3.ap-northeast-1.amazonaws.com/broker/671aec522593f600019766d0_file.csv?X-Amz-Security-Token=IQo*********2cd90f14efb\"\n    }\n}"
        common_response = RestResponse.from_json(data)
        resp = GetRebaseResp.from_dict(common_response.data)
