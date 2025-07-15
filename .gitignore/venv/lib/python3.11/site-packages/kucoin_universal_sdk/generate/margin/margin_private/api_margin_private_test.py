import unittest
from .model_cross_margin_position_event import CrossMarginPositionEvent
from .model_isolated_margin_position_event import IsolatedMarginPositionEvent
from kucoin_universal_sdk.model.common import WsMessage


class MarginPrivateAPITest(unittest.TestCase):

    def test_cross_margin_position_resp_model(self):
        """
        cross_margin_position
        Get Cross Margin Position change
        /crossMarginPosition/margin/position
        """
        data = "{\"topic\":\"/margin/position\",\"subject\":\"debt.ratio\",\"type\":\"message\",\"userId\":\"633559791e1cbc0001f319bc\",\"channelType\":\"private\",\"data\":{\"debtRatio\":0,\"totalAsset\":0.00052431772284080000000,\"marginCoefficientTotalAsset\":\"0.0005243177228408\",\"totalDebt\":\"0\",\"assetList\":{\"BTC\":{\"total\":\"0.00002\",\"available\":\"0\",\"hold\":\"0.00002\"},\"USDT\":{\"total\":\"33.68855864\",\"available\":\"15.01916691\",\"hold\":\"18.66939173\"}},\"debtList\":{\"BTC\":\"0\",\"USDT\":\"0\"},\"timestamp\":1729912435657}}"
        common_response = WsMessage.from_json(data)
        resp = CrossMarginPositionEvent.from_dict(common_response.raw_data)

    def test_isolated_margin_position_resp_model(self):
        """
        isolated_margin_position
        Get Isolated Margin Position change
        /isolatedMarginPosition/margin/isolatedPosition:_symbol_
        """
        data = "{\"topic\":\"/margin/isolatedPosition:BTC-USDT\",\"subject\":\"positionChange\",\"type\":\"message\",\"userId\":\"633559791e1cbc0001f319bc\",\"channelType\":\"private\",\"data\":{\"tag\":\"BTC-USDT\",\"status\":\"DEBT\",\"statusBizType\":\"DEFAULT_DEBT\",\"accumulatedPrincipal\":\"5.01\",\"changeAssets\":{\"BTC\":{\"total\":\"0.00043478\",\"hold\":\"0\",\"liabilityPrincipal\":\"0\",\"liabilityInterest\":\"0\"},\"USDT\":{\"total\":\"0.98092004\",\"hold\":\"0\",\"liabilityPrincipal\":\"26\",\"liabilityInterest\":\"0.00025644\"}},\"timestamp\":1730121097742}}"
        common_response = WsMessage.from_json(data)
        resp = IsolatedMarginPositionEvent.from_dict(common_response.raw_data)
