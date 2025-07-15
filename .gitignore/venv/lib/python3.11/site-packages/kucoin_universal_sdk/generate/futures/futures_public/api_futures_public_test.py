import unittest
from .model_announcement_event import AnnouncementEvent
from .model_execution_event import ExecutionEvent
from .model_instrument_event import InstrumentEvent
from .model_klines_event import KlinesEvent
from .model_orderbook_increment_event import OrderbookIncrementEvent
from .model_orderbook_level50_event import OrderbookLevel50Event
from .model_orderbook_level5_event import OrderbookLevel5Event
from .model_symbol_snapshot_event import SymbolSnapshotEvent
from .model_ticker_v1_event import TickerV1Event
from .model_ticker_v2_event import TickerV2Event
from kucoin_universal_sdk.model.common import WsMessage


class FuturesPublicAPITest(unittest.TestCase):

    def test_announcement_resp_model(self):
        """
        announcement
        announcement
        /announcement/contract/announcement:_symbol_
        """
        data = "{\"topic\":\"/contract/announcement\",\"subject\":\"funding.begin\",\"data\":{\"symbol\":\"XBTUSDTM\",\"fundingTime\":1551770400000,\"fundingRate\":-0.002966,\"timestamp\":1551770400000}}"
        common_response = WsMessage.from_json(data)
        resp = AnnouncementEvent.from_dict(common_response.raw_data)

    def test_execution_resp_model(self):
        """
        execution
        Match execution data.
        /execution/contractMarket/execution:_symbol_
        """
        data = "{\"topic\":\"/contractMarket/execution:XBTUSDTM\",\"type\":\"message\",\"subject\":\"match\",\"sn\":1794100537695,\"data\":{\"symbol\":\"XBTUSDTM\",\"sequence\":1794100537695,\"side\":\"buy\",\"size\":2,\"price\":\"90503.9\",\"takerOrderId\":\"247822202957807616\",\"makerOrderId\":\"247822167163555840\",\"tradeId\":\"1794100537695\",\"ts\":1731898619520000000}}"
        common_response = WsMessage.from_json(data)
        resp = ExecutionEvent.from_dict(common_response.raw_data)

    def test_instrument_resp_model(self):
        """
        instrument
        instrument
        /instrument/contract/instrument:_symbol_
        """
        data = "{\"topic\":\"/contract/instrument:XBTUSDTM\",\"type\":\"message\",\"subject\":\"mark.index.price\",\"data\":{\"markPrice\":90445.02,\"indexPrice\":90445.02,\"granularity\":1000,\"timestamp\":1731899129000}}"
        common_response = WsMessage.from_json(data)
        resp = InstrumentEvent.from_dict(common_response.raw_data)

    def test_klines_resp_model(self):
        """
        klines
        Klines
        /klines/contractMarket/limitCandle:_symbol___type_
        """
        data = "{\"topic\":\"/contractMarket/limitCandle:XBTUSDTM_1min\",\"type\":\"message\",\"data\":{\"symbol\":\"XBTUSDTM\",\"candles\":[\"1731898200\",\"90638.6\",\"90638.6\",\"90638.6\",\"90638.6\",\"21.0\",\"21\"],\"time\":1731898208357},\"subject\":\"candle.stick\"}"
        common_response = WsMessage.from_json(data)
        resp = KlinesEvent.from_dict(common_response.raw_data)

    def test_orderbook_increment_resp_model(self):
        """
        orderbook_increment
        Orderbook - Increment
        /orderbookIncrement/contractMarket/level2:_symbol_
        """
        data = "{\"topic\":\"/contractMarket/level2:XBTUSDTM\",\"type\":\"message\",\"subject\":\"level2\",\"sn\":1709400450243,\"data\":{\"sequence\":1709400450243,\"change\":\"90631.2,sell,2\",\"timestamp\":1731897467182}}"
        common_response = WsMessage.from_json(data)
        resp = OrderbookIncrementEvent.from_dict(common_response.raw_data)

    def test_orderbook_level50_resp_model(self):
        """
        orderbook_level50
        Orderbook - Level50
        /orderbookLevel50/contractMarket/level2Depth50:_symbol_
        """
        data = "{\"topic\":\"/contractMarket/level2Depth50:XBTUSDTM\",\"type\":\"message\",\"subject\":\"level2\",\"sn\":1731680249700,\"data\":{\"bids\":[[\"89778.6\",1534],[\"89778.2\",54]],\"sequence\":1709294490099,\"timestamp\":1731680249700,\"ts\":1731680249700,\"asks\":[[\"89778.7\",854],[\"89779.2\",4]]}}"
        common_response = WsMessage.from_json(data)
        resp = OrderbookLevel50Event.from_dict(common_response.raw_data)

    def test_orderbook_level5_resp_model(self):
        """
        orderbook_level5
        Orderbook - Level5
        /orderbookLevel5/contractMarket/level2Depth5:_symbol_
        """
        data = "{\"topic\":\"/contractMarket/level2Depth5:XBTUSDTM\",\"type\":\"message\",\"subject\":\"level2\",\"sn\":1731680019100,\"data\":{\"bids\":[[\"89720.9\",513],[\"89720.8\",12],[\"89718.6\",113],[\"89718.4\",19],[\"89718.3\",7]],\"sequence\":1709294294670,\"timestamp\":1731680019100,\"ts\":1731680019100,\"asks\":[[\"89721\",906],[\"89721.1\",203],[\"89721.4\",113],[\"89723.2\",113],[\"89725.4\",113]]}}"
        common_response = WsMessage.from_json(data)
        resp = OrderbookLevel5Event.from_dict(common_response.raw_data)

    def test_symbol_snapshot_resp_model(self):
        """
        symbol_snapshot
        Symbol Snapshot
        /symbolSnapshot/contractMarket/snapshot:_symbol_
        """
        data = "{\"topic\":\"/contractMarket/snapshot:XBTUSDTM\",\"type\":\"message\",\"subject\":\"snapshot.24h\",\"id\":\"673ab3fff4088b0001664f41\",\"data\":{\"highPrice\":91512.8,\"lastPrice\":90326.7,\"lowPrice\":88747.8,\"price24HoursBefore\":89880.4,\"priceChg\":446.3,\"priceChgPct\":0.0049,\"symbol\":\"XBTUSDTM\",\"ts\":1731900415023929239,\"turnover\":526928331.0482177734,\"volume\":5834.46}}"
        common_response = WsMessage.from_json(data)
        resp = SymbolSnapshotEvent.from_dict(common_response.raw_data)

    def test_ticker_v1_resp_model(self):
        """
        ticker_v1
        Get Ticker(not recommended)
        /tickerV1/contractMarket/ticker:_symbol_
        """
        data = "{\"topic\":\"/contractMarket/ticker:XBTUSDTM\",\"type\":\"message\",\"subject\":\"ticker\",\"sn\":1793133570931,\"data\":{\"symbol\":\"XBTUSDTM\",\"sequence\":1793133570931,\"side\":\"sell\",\"size\":1,\"price\":\"90147.7\",\"bestBidSize\":2186,\"bestBidPrice\":\"90147.7\",\"bestAskPrice\":\"90147.8\",\"tradeId\":\"1793133570931\",\"bestAskSize\":275,\"ts\":1731679215637000000}}"
        common_response = WsMessage.from_json(data)
        resp = TickerV1Event.from_dict(common_response.raw_data)

    def test_ticker_v2_resp_model(self):
        """
        ticker_v2
        Get Ticker V2
        /tickerV2/contractMarket/tickerV2:_symbol_
        """
        data = "{\"topic\":\"/contractMarket/tickerV2:XBTUSDTM\",\"type\":\"message\",\"subject\":\"tickerV2\",\"sn\":1709284589209,\"data\":{\"symbol\":\"XBTUSDTM\",\"sequence\":1709284589209,\"bestBidSize\":713,\"bestBidPrice\":\"88987.4\",\"bestAskPrice\":\"88987.5\",\"bestAskSize\":1037,\"ts\":1731665526461000000}}"
        common_response = WsMessage.from_json(data)
        resp = TickerV2Event.from_dict(common_response.raw_data)
