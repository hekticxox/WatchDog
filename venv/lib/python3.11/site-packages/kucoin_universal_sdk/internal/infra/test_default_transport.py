import unittest
from unittest.mock import MagicMock, patch
from typing import Optional
from pydantic import BaseModel, Field
from kucoin_universal_sdk.internal.infra.default_transport import DefaultTransport
from kucoin_universal_sdk.model.client_option import ClientOption
from kucoin_universal_sdk.model.transport_option import TransportOption
from kucoin_universal_sdk.model.common import RestRateLimit
from kucoin_universal_sdk.model.common import RestResponse
from kucoin_universal_sdk.model.constants import DomainType
from kucoin_universal_sdk.internal.infra.default_signer import KcSigner

class MockRequest(BaseModel):
    orderId: Optional[str] = Field(default=None, path_variable="True")
    userId: Optional[str] = Field(default=None, path_variable="True")

class TestDefaultTransport(unittest.TestCase):
    def setUp(self):
        transport_option = TransportOption(
            timeout=5,
            max_retries=2,
            retry_delay=1,
            keep_alive=True,
            proxy=None,
            max_idle_conns=10,
        )
        self.client_option = ClientOption(
            key="test_key",
            secret="test_secret",
            passphrase="test_passphrase",
            broker_name="broker",
            broker_partner="partner",
            broker_key="broker_key",
            transport_option=transport_option,
            spot_endpoint="https://api.spot.example.com",
            futures_endpoint="https://api.futures.example.com",
            broker_endpoint="https://api.broker.example.com"
        )
        self.transport = DefaultTransport(self.client_option)

    @patch("requests.Session")
    def test_create_http_client(self, mock_session):
        session = MagicMock()
        mock_session.return_value = session
        client = self.transport.create_http_client(self.client_option.transport_option)

        self.assertEqual(client, session)
        session.mount.assert_called()

    def test_process_headers(self):
        body = b""
        request = MagicMock()
        request.headers = {}
        request.url = "https://api.example.com/path"
        method = "GET"

        self.transport.process_headers(body, request, method, DomainType.SPOT.value)

        self.assertIn("Content-Type", request.headers)
        self.assertIn("User-Agent", request.headers)
        self.assertIn("KC-API-KEY", request.headers)
       
    def test_process_path_variable(self):
        request_obj = MockRequest(orderId="12345", userId="67890")
        path = "/api/v1/orders/{orderId}/users/{userId}"
        processed_path = self.transport.process_path_variable(path, request_obj)

        self.assertEqual(processed_path, "/api/v1/orders/12345/users/67890")

    def test_process_limit(self):
        resp = MagicMock()
        resp.headers = {
            "gw-ratelimit-limit": "100",
            "gw-ratelimit-remaining": "50",
            "gw-ratelimit-reset": "1234567890"
        }

        limit = self.transport.process_limit(resp)
        self.assertIsInstance(limit, RestRateLimit)
        self.assertEqual(limit.limit, 100)
        self.assertEqual(limit.remaining, 50)
        self.assertEqual(limit.reset, 1234567890)

if __name__ == "__main__":
    unittest.main()
