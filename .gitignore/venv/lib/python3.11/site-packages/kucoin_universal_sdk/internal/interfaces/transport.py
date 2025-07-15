from abc import ABC, abstractmethod
from typing import Any

from .response import Response


class Transport(ABC):
    @abstractmethod
    def call(self, domain: str, broker: bool, method: str, path: str, request_obj: Any, response_obj: Response,
             request_as_json: bool, **kwargs: Any) -> Any:
        """
        Executes a remote call using the specified method, path, and request data, 
        and populates the provided response object with the result.

        :param domain: Which endpoint; spot/futures/broker
        :param broker: Is a broker service or not
        :param method: The HTTP method (e.g., 'GET', 'POST') or equivalent for the call
        :param path: The target endpoint or path for the remote service
        :param request_obj: The request data or payload to send; could be a dictionary or any serializable structure
        :param response_obj: An instance of a Response subclass, to be filled with data from the remote call
        :param request_as_json: Mark the request body is a json str
        :param kwargs: Additional optional arguments for the call
        :return final response object, raise Exception if error occurs
        """
        pass
    def close(self):
        """
        Closes the underlying transport connection.
        """
        pass
