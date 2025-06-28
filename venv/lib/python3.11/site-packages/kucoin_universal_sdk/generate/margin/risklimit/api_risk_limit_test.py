import unittest
from .model_get_margin_risk_limit_req import GetMarginRiskLimitReq
from .model_get_margin_risk_limit_resp import GetMarginRiskLimitResp
from kucoin_universal_sdk.model.common import RestResponse


class RiskLimitAPITest(unittest.TestCase):

    def test_get_margin_risk_limit_req_model(self):
        """
       get_margin_risk_limit
       Get Margin Risk Limit
       /api/v3/margin/currencies
       """
        data = "{\"isIsolated\": true, \"currency\": \"BTC\", \"symbol\": \"BTC-USDT\"}"
        req = GetMarginRiskLimitReq.from_json(data)

    def test_get_margin_risk_limit_resp_model(self):
        """
        get_margin_risk_limit
        Get Margin Risk Limit
        /api/v3/margin/currencies
        """
        data = "{\n    \"code\": \"200000\",\n    \"data\": [\n        {\n            \"timestamp\": 1729678659275,\n            \"currency\": \"BTC\",\n            \"borrowMaxAmount\": \"75.15\",\n            \"buyMaxAmount\": \"217.12\",\n            \"holdMaxAmount\": \"217.12\",\n            \"borrowCoefficient\": \"1\",\n            \"marginCoefficient\": \"1\",\n            \"precision\": 8,\n            \"borrowMinAmount\": \"0.001\",\n            \"borrowMinUnit\": \"0.0001\",\n            \"borrowEnabled\": true\n        }\n    ]\n}\n"
        common_response = RestResponse.from_json(data)
        resp = GetMarginRiskLimitResp.from_dict(common_response.data)
