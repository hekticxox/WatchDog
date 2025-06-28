import unittest
from .model_get_account_resp import GetAccountResp
from kucoin_universal_sdk.model.common import RestResponse


class AffiliateAPITest(unittest.TestCase):

    def test_get_account_req_model(self):
        """
       get_account
       Get Account
       /api/v2/affiliate/inviter/statistics
       """

    def test_get_account_resp_model(self):
        """
        get_account
        Get Account
        /api/v2/affiliate/inviter/statistics
        """
        data = "{\n    \"code\": \"200000\",\n    \"data\": {\n        \"parentUid\": \"1000000\",\n        \"orders\": [\n            {\n                \"orderId\": \"1668458892612980737\",\n                \"currency\": \"USDT\",\n                \"principal\": \"100\",\n                \"interest\": \"0\"\n            }\n        ],\n        \"ltv\": {\n            \"transferLtv\": \"0.6000\",\n            \"onlyClosePosLtv\": \"0.7500\",\n            \"delayedLiquidationLtv\": \"0.9000\",\n            \"instantLiquidationLtv\": \"0.9500\",\n            \"currentLtv\": \"0.0854\"\n        },\n        \"totalMarginAmount\": \"1170.36181573\",\n        \"transferMarginAmount\": \"166.66666666\",\n        \"margins\": [\n            {\n                \"marginCcy\": \"USDT\",\n                \"marginQty\": \"1170.36181573\",\n                \"marginFactor\": \"1.000000000000000000\"\n            }\n        ]\n    }\n}"
        common_response = RestResponse.from_json(data)
        resp = GetAccountResp.from_dict(common_response.data)
