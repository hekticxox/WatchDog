from enum import Enum

# Global API endpoints
GLOBAL_API_ENDPOINT = "https://api.kucoin.com"
GLOBAL_FUTURES_API_ENDPOINT = "https://api-futures.kucoin.com"
GLOBAL_BROKER_API_ENDPOINT = "https://api-broker.kucoin.com"


class DomainType(Enum):
    """Enum for domain types."""
    SPOT = "spot"  # Spot market domain type
    FUTURES = "futures"  # Futures market domain type
    BROKER = "broker"  # Broker domain type


class RestResultCode(Enum):
    """Enum for HTTP result codes."""
    SUCCESS = "200000"  # Operation was successful


class WsMessageType(Enum):
    """
    MessageType defines various types of messages that can be sent or received.

    Attributes:
        WELCOME: Indicates a welcome message upon initial connection.
        PING: Represents a ping message to check the connection status.
        PONG: Represents a pong message in response to a ping.
        SUBSCRIBE: Message to request subscription to a topic or channel.
        ACK: Acknowledgement message indicating a successful action.
        UNSUBSCRIBE: Message to request unsubscription from a topic or channel.
        ERROR: Represents an error message indicating something went wrong.
        MESSAGE: Generic message type for data transmission.
        NOTICE: Notification or informational message.
        COMMAND: Command message for specific actions or controls.
    """

    WELCOME = "welcome"  # Indicates a welcome message upon initial connection
    PING = "ping"  # Represents a ping message to check the connection status
    PONG = "pong"  # Represents a pong message in response to a ping
    SUBSCRIBE = "subscribe"  # Message to request subscription to a topic or channel
    ACK = "ack"  # Acknowledgement message indicating a successful action
    UNSUBSCRIBE = "unsubscribe"  # Message to request unsubscription from a topic or channel
    ERROR = "error"  # Represents an error message indicating something went wrong
    MESSAGE = "message"  # Generic message type for data transmission
    NOTICE = "notice"  # Notification or informational message
    COMMAND = "command"  # Command message for specific actions or controls
