from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from requests import Request, Response


class Interceptor(ABC):
    """
    Interceptor is an abstract base class for defining HTTP request interceptors.
    """

    @abstractmethod
    def before(self, req: Request) -> Request:
        """Executed before the request is sent. Allows modification of the request before sending."""
        pass

    @abstractmethod
    def after(self, req: Request, resp: Optional[Response], err: Optional[Exception]) -> Response:
        """
        Executed after the request is completed. Allows processing of the response or error.

        Parameters:
            req (Request): The original request object.
            resp (Optional[Response]): The response received, if any.
            err (Optional[Exception]): The exception raised, if any.

        Returns:
            Response: The processed response object.
        """
        pass


class TransportOption:
    """
    TransportOption holds configurations for HTTP client behavior.

    Attributes:
        keep_alive (bool): Enables keep-alive for persistent connections. Defaults to True.
        max_pool_size (int): The number of connection pools to cache(how many hosts). Defaults to 10.
        max_connection_per_pool: The maximum number of connections to save in the pool. Defaults to 10
        connect_timeout (float): Connection timeout duration in seconds. Defaults to 10.
        read_timeout (float): Read timeout duration in seconds. Defaults to 30.
        proxy (Optional[dict]): HTTP(s) proxy. Defaults to None. Example {'http': '192.168.1.1', 'https': '192.168.1.1'}
        max_retries (int): Maximum number of retry attempts. Defaults to 3.
        interceptors (Optional[List[Interceptor]]): List of HTTP interceptors. Defaults to an empty list.
    """

    def __init__(self,
                 keep_alive: bool = True,
                 max_pool_size: int = 10,
                 max_connection_per_pool: int = 10,
                 connect_timeout: float = 10,
                 read_timeout: float = 30,
                 proxy: Optional[dict] = None,
                 max_retries: int = 3,
                 retry_delay: float = 2,
                 interceptors: Optional[List[Interceptor]] = None):
        self.keep_alive = keep_alive
        self.max_pool_size = max_pool_size
        self.max_connection_per_pool = max_connection_per_pool
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.proxy = proxy
        self.max_retries = max_retries
        self.interceptors = interceptors if interceptors is not None else []


class TransportOptionBuilder:
    def __init__(self):
        """
        TransportOptionBuilder is a builder for TransportOption.
        """
        self.option = TransportOption()

    def set_keep_alive(self, keep_alive: bool) -> TransportOptionBuilder:
        self.option.keep_alive = keep_alive
        return self

    def set_max_pool_size(self, max_pool_size: int) -> TransportOptionBuilder:
        self.option.max_pool_size = max_pool_size
        return self

    def set_max_connection_per_pool(self, max_connection_per_pool: int) -> TransportOptionBuilder:
        self.option.max_connection_per_pool = max_connection_per_pool
        return self

    def set_read_timeout(self, read_timeout: float) -> TransportOptionBuilder:
        self.option.read_timeout = read_timeout
        return self

    def set_connect_timeout(self, connect_timeout: float) -> TransportOptionBuilder:
        self.option.connect_timeout = connect_timeout
        return self

    def set_proxy(self, proxy: []) -> TransportOptionBuilder:
        """
         Example:{'http': '192.168.1.1', 'https': '192.168.1.1'}
        """
        self.option.proxy = proxy
        return self

    def set_https_proxy(self, https_proxy: str) -> TransportOptionBuilder:
        self.option.https_proxy = https_proxy
        return self

    def set_max_retries(self, max_retries: int) -> TransportOptionBuilder:
        self.option.max_retries = max_retries
        return self

    def set_interceptors(self, interceptors: List[Interceptor]) -> TransportOptionBuilder:
        self.option.interceptors = interceptors
        return self

    def add_interceptor(self, interceptor: Interceptor) -> TransportOptionBuilder:
        if self.option.interceptors is None:
            self.option.interceptors = []
        self.option.interceptors.append(interceptor)
        return self

    def build(self) -> TransportOption:
        return self.option
