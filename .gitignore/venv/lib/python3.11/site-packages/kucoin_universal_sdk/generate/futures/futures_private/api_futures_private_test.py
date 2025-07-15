import unittest
from .model_all_order_event import AllOrderEvent
from .model_all_position_event import AllPositionEvent
from .model_balance_event import BalanceEvent
from .model_cross_leverage_event import CrossLeverageEvent
from .model_margin_mode_event import MarginModeEvent
from .model_order_event import OrderEvent
from .model_position_event import PositionEvent
from .model_stop_orders_event import StopOrdersEvent
from kucoin_universal_sdk.model.common import WsMessage


class FuturesPrivateAPITest(unittest.TestCase):

    def test_all_order_resp_model(self):
        """
        all_order
        All Order change pushes.
        /allOrder/contractMarket/tradeOrders
        """
        data = "{\"topic\":\"/contractMarket/tradeOrders:XBTUSDTM\",\"type\":\"message\",\"subject\":\"symbolOrderChange\",\"userId\":\"633559791e1cbc0001f319bc\",\"channelType\":\"private\",\"data\":{\"symbol\":\"XBTUSDTM\",\"side\":\"buy\",\"canceledSize\":\"0\",\"orderId\":\"247899236673269761\",\"liquidity\":\"maker\",\"marginMode\":\"ISOLATED\",\"type\":\"open\",\"orderTime\":1731916985768138917,\"size\":\"1\",\"filledSize\":\"0\",\"price\":\"91670\",\"remainSize\":\"1\",\"status\":\"open\",\"ts\":1731916985789000000}}"
        common_response = WsMessage.from_json(data)
        resp = AllOrderEvent.from_dict(common_response.raw_data)

    def test_all_position_resp_model(self):
        """
        all_position
        All symbol position change events push
        /allPosition/contract/positionAll
        """
        data = "{\"topic\":\"/contract/position:XBTUSDTM\",\"type\":\"message\",\"data\":{\"symbol\":\"XBTUSDTM\",\"maintMarginReq\":0.005,\"riskLimit\":500000,\"realLeverage\":4.9685590767,\"crossMode\":false,\"delevPercentage\":0.10,\"openingTimestamp\":1731916913097,\"autoDeposit\":true,\"currentTimestamp\":1731924561514,\"currentQty\":1,\"currentCost\":91.5306,\"currentComm\":0.09179284,\"unrealisedCost\":91.6945,\"realisedCost\":-0.07210716,\"isOpen\":true,\"markPrice\":91839.79,\"markValue\":91.83979,\"posCost\":91.6945,\"posCross\":0,\"posInit\":18.3389,\"posComm\":0.06602004,\"posLoss\":0,\"posMargin\":18.40492004,\"posFunding\":0,\"posMaint\":0.5634627025,\"maintMargin\":18.55021004,\"avgEntryPrice\":91694.5,\"liquidationPrice\":73853.0426625,\"bankruptPrice\":73355.6,\"settleCurrency\":\"USDT\",\"changeReason\":\"positionChange\",\"riskLimitLevel\":2,\"realisedGrossCost\":-0.1639,\"realisedGrossPnl\":0.1639,\"realisedPnl\":0.07210716,\"unrealisedPnl\":0.14529,\"unrealisedPnlPcnt\":0.0016,\"unrealisedRoePcnt\":0.0079,\"leverage\":4.9685590767,\"marginMode\":\"ISOLATED\",\"positionSide\":\"BOTH\"},\"subject\":\"position.change\",\"userId\":\"633559791e1cbc0001f319bc\",\"channelType\":\"private\"}"
        common_response = WsMessage.from_json(data)
        resp = AllPositionEvent.from_dict(common_response.raw_data)

    def test_balance_resp_model(self):
        """
        balance
        the balance change push
        /balance/contractAccount/wallet
        """
        data = "{\"topic\":\"/contractAccount/wallet\",\"type\":\"message\",\"subject\":\"walletBalance.change\",\"id\":\"673b0bb925b4bc0001fadfef\",\"userId\":\"633559791e1cbc0001f319bc\",\"channelType\":\"private\",\"data\":{\"crossPosMargin\":\"0\",\"isolatedOrderMargin\":\"18.1188\",\"holdBalance\":\"0\",\"equity\":\"81.273621258\",\"version\":\"1337\",\"availableBalance\":\"26.144281178\",\"isolatedPosMargin\":\"36.80984008\",\"walletBalance\":\"81.072921258\",\"isolatedFundingFeeMargin\":\"0\",\"crossUnPnl\":\"0\",\"totalCrossMargin\":\"26.144281178\",\"currency\":\"USDT\",\"isolatedUnPnl\":\"0.2007\",\"crossOrderMargin\":\"0\",\"timestamp\":\"1731916996764\"}}"
        common_response = WsMessage.from_json(data)
        resp = BalanceEvent.from_dict(common_response.raw_data)

    def test_cross_leverage_resp_model(self):
        """
        cross_leverage
        the leverage change push
        /crossLeverage/contract/crossLeverage
        """
        data = "{\"topic\":\"/contract/crossLeverage\",\"type\":\"message\",\"data\":{\"ETHUSDTM\":{\"leverage\":\"8\"}},\"subject\":\"user.config\",\"userId\":\"66f12e8befb04d0001882b49\",\"channelType\":\"private\"}"
        common_response = WsMessage.from_json(data)
        resp = CrossLeverageEvent.from_dict(common_response.raw_data)

    def test_margin_mode_resp_model(self):
        """
        margin_mode
        the margin mode change
        /marginMode/contract/marginMode
        """
        data = "{\"topic\":\"/contract/marginMode\",\"type\":\"message\",\"data\":{\"ETHUSDTM\":\"ISOLATED\"},\"subject\":\"user.config\",\"userId\":\"66f12e8befb04d0001882b49\",\"channelType\":\"private\"}"
        common_response = WsMessage.from_json(data)
        resp = MarginModeEvent.from_dict(common_response.raw_data)

    def test_order_resp_model(self):
        """
        order
        Order change pushes.
        /order/contractMarket/tradeOrders:_symbol_
        """
        data = "{\"topic\":\"/contractMarket/tradeOrders:XBTUSDTM\",\"type\":\"message\",\"subject\":\"symbolOrderChange\",\"userId\":\"633559791e1cbc0001f319bc\",\"channelType\":\"private\",\"data\":{\"symbol\":\"XBTUSDTM\",\"side\":\"buy\",\"canceledSize\":\"0\",\"orderId\":\"247899236673269761\",\"liquidity\":\"maker\",\"marginMode\":\"ISOLATED\",\"type\":\"open\",\"orderTime\":1731916985768138917,\"size\":\"1\",\"filledSize\":\"0\",\"price\":\"91670\",\"remainSize\":\"1\",\"status\":\"open\",\"ts\":1731916985789000000}}"
        common_response = WsMessage.from_json(data)
        resp = OrderEvent.from_dict(common_response.raw_data)

    def test_position_resp_model(self):
        """
        position
        the position change events push
        /position/contract/position:_symbol_
        """
        data = "{\"topic\":\"/contract/position:XBTUSDTM\",\"type\":\"message\",\"data\":{\"symbol\":\"XBTUSDTM\",\"maintMarginReq\":0.005,\"riskLimit\":500000,\"realLeverage\":4.9685590767,\"crossMode\":false,\"delevPercentage\":0.10,\"openingTimestamp\":1731916913097,\"autoDeposit\":true,\"currentTimestamp\":1731924561514,\"currentQty\":1,\"currentCost\":91.5306,\"currentComm\":0.09179284,\"unrealisedCost\":91.6945,\"realisedCost\":-0.07210716,\"isOpen\":true,\"markPrice\":91839.79,\"markValue\":91.83979,\"posCost\":91.6945,\"posCross\":0,\"posInit\":18.3389,\"posComm\":0.06602004,\"posLoss\":0,\"posMargin\":18.40492004,\"posFunding\":0,\"posMaint\":0.5634627025,\"maintMargin\":18.55021004,\"avgEntryPrice\":91694.5,\"liquidationPrice\":73853.0426625,\"bankruptPrice\":73355.6,\"settleCurrency\":\"USDT\",\"changeReason\":\"positionChange\",\"riskLimitLevel\":2,\"realisedGrossCost\":-0.1639,\"realisedGrossPnl\":0.1639,\"realisedPnl\":0.07210716,\"unrealisedPnl\":0.14529,\"unrealisedPnlPcnt\":0.0016,\"unrealisedRoePcnt\":0.0079,\"leverage\":4.9685590767,\"marginMode\":\"ISOLATED\",\"positionSide\":\"BOTH\"},\"subject\":\"position.change\",\"userId\":\"633559791e1cbc0001f319bc\",\"channelType\":\"private\"}"
        common_response = WsMessage.from_json(data)
        resp = PositionEvent.from_dict(common_response.raw_data)

    def test_stop_orders_resp_model(self):
        """
        stop_orders
        stop order change pushes.
        /stopOrders/contractMarket/advancedOrders
        """
        data = "{\"topic\":\"/contractMarket/advancedOrders\",\"type\":\"message\",\"data\":{\"createdAt\":1730194206837,\"marginMode\":\"ISOLATED\",\"orderId\":\"240673378116083712\",\"orderPrice\":\"0.1\",\"orderType\":\"stop\",\"side\":\"buy\",\"size\":1,\"stop\":\"down\",\"stopPrice\":\"1000\",\"stopPriceType\":\"TP\",\"symbol\":\"XBTUSDTM\",\"ts\":1730194206843133000,\"type\":\"open\"},\"subject\":\"stopOrder\",\"id\":\"6720ab1ea52a9b0001734392\",\"userId\":\"66f12e8befb04d0001882b49\",\"channelType\":\"private\"}"
        common_response = WsMessage.from_json(data)
        resp = StopOrdersEvent.from_dict(common_response.raw_data)
