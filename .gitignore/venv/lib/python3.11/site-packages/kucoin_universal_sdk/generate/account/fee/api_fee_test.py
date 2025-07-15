import unittest
from .model_get_basic_fee_req import GetBasicFeeReq
from .model_get_basic_fee_resp import GetBasicFeeResp
from .model_get_futures_actual_fee_req import GetFuturesActualFeeReq
from .model_get_futures_actual_fee_resp import GetFuturesActualFeeResp
from .model_get_spot_actual_fee_req import GetSpotActualFeeReq
from .model_get_spot_actual_fee_resp import GetSpotActualFeeResp
from kucoin_universal_sdk.model.common import RestResponse


class FeeAPITest(unittest.TestCase):

    def test_get_basic_fee_req_model(self):
        """
       get_basic_fee
       Get Basic Fee - Spot/Margin
       /api/v1/base-fee
       """
        data = "{\"currencyType\": 1}"
        req = GetBasicFeeReq.from_json(data)

    def test_get_basic_fee_resp_model(self):
        """
        get_basic_fee
        Get Basic Fee - Spot/Margin
        /api/v1/base-fee
        """
        data = "{\n    \"code\": \"200000\",\n    \"data\": {\n        \"takerFeeRate\": \"0.001\",\n        \"makerFeeRate\": \"0.001\"\n    }\n}"
        common_response = RestResponse.from_json(data)
        resp = GetBasicFeeResp.from_dict(common_response.data)

    def test_get_spot_actual_fee_req_model(self):
        """
       get_spot_actual_fee
       Get Actual Fee - Spot/Margin
       /api/v1/trade-fees
       """
        data = "{\"symbols\": \"BTC-USDT,ETH-USDT\"}"
        req = GetSpotActualFeeReq.from_json(data)

    def test_get_spot_actual_fee_resp_model(self):
        """
        get_spot_actual_fee
        Get Actual Fee - Spot/Margin
        /api/v1/trade-fees
        """
        data = "{\"code\":\"200000\",\"data\":[{\"symbol\":\"BTC-USDT\",\"takerFeeRate\":\"0.001\",\"makerFeeRate\":\"0.001\"},{\"symbol\":\"ETH-USDT\",\"takerFeeRate\":\"0.001\",\"makerFeeRate\":\"0.001\"}]}"
        common_response = RestResponse.from_json(data)
        resp = GetSpotActualFeeResp.from_dict(common_response.data)

    def test_get_futures_actual_fee_req_model(self):
        """
       get_futures_actual_fee
       Get Actual Fee - Futures
       /api/v1/trade-fees
       """
        data = "{\"symbol\": \"XBTUSDTM\"}"
        req = GetFuturesActualFeeReq.from_json(data)

    def test_get_futures_actual_fee_resp_model(self):
        """
        get_futures_actual_fee
        Get Actual Fee - Futures
        /api/v1/trade-fees
        """
        data = "{\"code\":\"200000\",\"data\":{\"symbol\":\"XBTUSDTM\",\"takerFeeRate\":\"0.0006\",\"makerFeeRate\":\"0.0002\"}}"
        common_response = RestResponse.from_json(data)
        resp = GetFuturesActualFeeResp.from_dict(common_response.data)
