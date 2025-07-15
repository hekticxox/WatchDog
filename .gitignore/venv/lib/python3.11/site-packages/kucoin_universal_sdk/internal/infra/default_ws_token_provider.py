import json
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field
from typing_extensions import Self

from kucoin_universal_sdk.model.common import RestResponse
from kucoin_universal_sdk.model.constants import DomainType
from .default_transport import DefaultTransport
from ..interfaces.websocket import WsToken, WsTokenProvider

PATH_PRIVATE = "/api/v1/bullet-private"
PATH_PUBLIC = "/api/v1/bullet-public"


class DefaultWsTokenProvider(WsTokenProvider):
    def __init__(self, transport: DefaultTransport, domain: DomainType, private: bool):
        self.transport = transport
        self.domain = domain
        self.private = private

    def get_token(self) -> List[dict]:
        path = PATH_PUBLIC if not self.private else PATH_PRIVATE
        try:
            response = TokenResponse()
            response: TokenResponse = self.transport.call(self.domain.value, False, "POST", path, None, response, False)
            
            for sr in response.instanceServers:
                sr.token = response.token
            return response.instanceServers
        except Exception as e:
            raise e
    
    def close(self):
        self.transport.close()


class TokenResponse(BaseModel):
    common_response: Optional["RestResponse"] = Field(default=None, description="Common response")
    token: Optional[str] = Field(default=None, description="Token")
    instanceServers: Optional[List[WsToken]] = Field(default=None, description="Instance servers")

    model_config = {
        "populate_by_name": True,
        "validate_assignment": False,
        "protected_namespaces": (),
    }

    def set_common_response(self, response: "RestResponse") -> None:
        self.common_response = response

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of TokenResponse from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "token": obj.get("token"),
            "instanceServers": [
                WsToken.from_dict(_item)
                for _item in obj["instanceServers"]
            ] if obj.get("instanceServers") is not None else None
        })
        return _obj
