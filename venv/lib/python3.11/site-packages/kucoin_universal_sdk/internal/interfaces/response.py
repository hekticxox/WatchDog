from abc import ABC, abstractmethod
from typing import Optional

from typing_extensions import Self

from kucoin_universal_sdk.model.common import RestResponse


class Response(ABC):
    @abstractmethod
    def set_common_response(self, response: RestResponse):
        """
        Set common response data.

        :param response: A RestResponse object to set common response data
        """
        pass

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """
        Create an instance of RestResponse from a JSON string
        """
        pass

    @classmethod
    def from_dict(cls, dct :dict) -> Optional[Self]:
        """
        Create an instance of RestResponse from a Dict Object
        """
        pass
