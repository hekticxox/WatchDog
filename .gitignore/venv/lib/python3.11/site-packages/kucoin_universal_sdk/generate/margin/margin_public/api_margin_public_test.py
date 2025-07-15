import unittest
from .model_index_price_event import IndexPriceEvent
from .model_mark_price_event import MarkPriceEvent
from typing import List
from kucoin_universal_sdk.model.common import WsMessage


class MarginPublicAPITest(unittest.TestCase):

    def test_index_price_resp_model(self):
        """
        index_price
        Index Price
        /indexPrice/indicator/index:_symbol_,_symbol_
        """
        data = "{\"id\":\"5c24c5da03aa673885cd67a0\",\"type\":\"message\",\"topic\":\"/indicator/index:USDT-BTC\",\"subject\":\"tick\",\"data\":{\"symbol\":\"USDT-BTC\",\"granularity\":5000,\"timestamp\":1551770400000,\"value\":0.0001092}}"
        common_response = WsMessage.from_json(data)
        resp = IndexPriceEvent.from_dict(common_response.raw_data)

    def test_mark_price_resp_model(self):
        """
        mark_price
        Mark Price
        /markPrice/indicator/markPrice:_symbol_,_symbol_
        """
        data = "{\"id\":\"5c24c5da03aa673885cd67aa\",\"type\":\"message\",\"topic\":\"/indicator/markPrice:USDT-BTC\",\"subject\":\"tick\",\"data\":{\"symbol\":\"USDT-BTC\",\"granularity\":5000,\"timestamp\":1551770400000,\"value\":0.0001093}}"
        common_response = WsMessage.from_json(data)
        resp = MarkPriceEvent.from_dict(common_response.raw_data)
