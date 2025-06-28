from __future__ import annotations

from typing import Optional

from .transport_option import TransportOption
from .websocket_option import WebSocketClientOption


class ClientOption:
    """
    ClientOption holds the configuration details for a client, including authentication keys, API endpoints, and transport options.

    Attributes:
        key (str): Authentication key for the client.
        secret (str): Authentication secret for the client.
        passphrase (str): Authentication passphrase for the client.
        broker_name (str): The name of the broker.
        broker_partner (str): The partner associated with the broker.
        broker_key (str): The secret key for the broker.
        spot_endpoint (str): Spot market API endpoint for the client.
        futures_endpoint (str): Futures market API endpoint for the client.
        broker_endpoint (str): Broker API endpoint for the client.
        transport_option (Optional[TransportOption]): Optional configuration for HTTP network transport.
        websocket_client_option (Optional[WebSocketClientOption]): Optional configuration for WebSocket transport.
    """

    def __init__(self,
                 key: str,
                 secret: str,
                 passphrase: str,
                 spot_endpoint: str,
                 futures_endpoint: str,
                 broker_endpoint: str,
                 broker_name: str,
                 broker_partner: str,
                 broker_key: str,
                 transport_option: Optional[TransportOption] = None,
                 websocket_client_option: Optional[WebSocketClientOption] = None):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.broker_name = broker_name
        self.broker_partner = broker_partner
        self.broker_key = broker_key
        self.spot_endpoint = spot_endpoint
        self.futures_endpoint = futures_endpoint
        self.broker_endpoint = broker_endpoint
        self.transport_option = transport_option
        self.websocket_client_option = websocket_client_option


class ClientOptionBuilder:
    """
    ClientOptionBuilder is a builder class for constructing a ClientOption instance.
    """

    def __init__(self):
        self._key = None
        self._secret = None
        self._passphrase = None
        self._spot_endpoint = None
        self._broker_endpoint = None
        self._futures_endpoint = None
        self._broker_name = None
        self._broker_partner = None
        self._broker_key = None
        self._transport_option = None
        self._websocket_client_option = None

    def set_key(self, key: str) -> ClientOptionBuilder:
        self._key = key
        return self

    def set_secret(self, secret: str) -> ClientOptionBuilder:
        self._secret = secret
        return self

    def set_passphrase(self, passphrase: str) -> ClientOptionBuilder:
        self._passphrase = passphrase
        return self

    def set_spot_endpoint(self, spot_endpoint: str) -> ClientOptionBuilder:
        self._spot_endpoint = spot_endpoint
        return self

    def set_futures_endpoint(self, futures_endpoint: str) -> ClientOptionBuilder:
        self._futures_endpoint = futures_endpoint
        return self

    def set_broker_endpoint(self, broker_endpoint: str) -> ClientOptionBuilder:
        self._broker_endpoint = broker_endpoint
        return self

    def set_broker_name(self, broker_name: str) -> ClientOptionBuilder:
        self._broker_name = broker_name
        return self

    def set_broker_partner(self, broker_partner: str) -> ClientOptionBuilder:
        self._broker_partner = broker_partner
        return self

    def set_broker_key(self, broker_key: str) -> ClientOptionBuilder:
        self._broker_key = broker_key
        return self

    def set_transport_option(self, transport_option: Optional[TransportOption]) -> ClientOptionBuilder:
        self._transport_option = transport_option
        return self

    def set_websocket_client_option(self,
                                    websocket_client_option: Optional[WebSocketClientOption]) -> ClientOptionBuilder:
        self._websocket_client_option = websocket_client_option
        return self

    def build(self) -> ClientOption:
        return ClientOption(
            key=self._key,
            secret=self._secret,
            passphrase=self._passphrase,
            spot_endpoint=self._spot_endpoint,
            futures_endpoint=self._futures_endpoint,
            broker_endpoint=self._broker_endpoint,
            broker_name=self._broker_name,
            broker_partner=self._broker_partner,
            broker_key=self._broker_key,
            transport_option=self._transport_option,
            websocket_client_option=self._websocket_client_option
        )
