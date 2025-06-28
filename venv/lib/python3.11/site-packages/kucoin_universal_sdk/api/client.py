from abc import ABC, abstractmethod

from kucoin_universal_sdk.api.api_rest import KucoinRestService
from kucoin_universal_sdk.api.api_ws import KucoinWSService
from kucoin_universal_sdk.internal.rest.default_rest_impl import DefaultKucoinRestAPIImpl
from kucoin_universal_sdk.internal.ws.default_ws_impl import DefaultKucoinWSAPIImpl
from kucoin_universal_sdk.model.client_option import ClientOption

"""
### REST API Notes

Client Features:
- Advanced HTTP Handling:
  Supports retries, persistent connections, and connection pooling for efficient HTTP request handling.
- Extensible Interceptors:
  Provides support for HTTP interceptors, allowing users to extend and customize request and response processing.
- Rich Response Details:
  API responses include rate-limiting information and raw data to aid debugging and ensure precise control.
- Public API Access:
  Public API endpoints do not require authentication, enabling non-authenticated use cases.

---

### WebSocket API Notes

Client Features:
- Flexible Service Creation:
  Users can create WebSocket services for public/private channels in Spot, Futures, or Margin trading as needed.
  Multiple independent services can be created simultaneously.
- Service Lifecycle:
  If a WebSocket service is closed, always create a new service instead of reusing it to prevent undefined behavior.
- Connection-to-Channel Mapping:
  Each WebSocket connection corresponds to a specific channel type.
  For example, Spot public/private and Futures public/private require 4 active WebSocket connections.

Threading and Callbacks:
- Simple Thread Model:
  WebSocket services use a simple thread model, ensuring that all callbacks are executed on a single thread.
- Subscription Management:
  Subscriptions are synchronous and require acknowledgment (ACK) from the server to be considered successful.
  Each subscription is assigned a unique ID, which can be used to cancel the subscription.

Data and Message Handling:
- Framework-Managed Threads:
  All data messages are processed by a single framework-managed thread, maintaining orderly callback execution.
- Buffer Management:
  When the message buffer is full, new messages are discarded, and a notification event is triggered.
- Duplicate Subscriptions:
  Avoid overlapping subscription parameters. For instance:
    Subscribing to ["BTC-USDT", "ETH-USDT"] and ["ETH-USDT", "DOGE-USDT"] may lead to undefined behavior.
    Identical subscription parameters will raise an error indicating duplicate subscriptions.
"""


class Client(ABC):
    @abstractmethod
    def rest_service(self) -> KucoinRestService:
        """get restful Service"""
        pass

    @abstractmethod
    def ws_service(self) -> KucoinWSService:
        """get websocket Service"""
        pass


class DefaultClient(Client):
    def __init__(self, options: ClientOption):
        if options.transport_option is not None:
            self.rest_impl = DefaultKucoinRestAPIImpl(options)
        if options.websocket_client_option is not None:
            self.ws_impl = DefaultKucoinWSAPIImpl(options)
        if options.transport_option is None and options.websocket_client_option is None:
            raise ValueError("options.transport_option or options.websocket_client_option must be set")

    def rest_service(self) -> KucoinRestService:
        return self.rest_impl

    def ws_service(self) -> KucoinWSService:
        return self.ws_impl
