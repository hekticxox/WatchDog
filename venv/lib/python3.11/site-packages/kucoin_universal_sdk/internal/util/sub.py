from typing import List

from ..interfaces.websocket import WebSocketMessageCallback


EMPTY_ARGS_STR = "EMPTY_ARGS"
class SubInfo:
    def __init__(self, prefix: str, args: List[str], callback: WebSocketMessageCallback):
        self.prefix = prefix
        self.args = args
        self.callback = callback

    def to_id(self) -> str:
        if not self.args:
            args_str = EMPTY_ARGS_STR
        else:
            sorted_args = sorted(self.args)
            args_str = ",".join(sorted_args)
        return f"{self.prefix}@@{args_str}"

    @classmethod
    def from_id(cls, id: str, callback: WebSocketMessageCallback = None) -> 'SubInfo':
        parts = id.split("@@")
        if len(parts) != 2:
            raise ValueError(f"SubInfo.from_id: invalid id format: {id}")

        prefix = parts[0]
        if parts[1] == EMPTY_ARGS_STR:
            args = []
        else:
            args = parts[1].split(",")
        return cls(prefix=prefix, args=args, callback=callback)

    def topics(self) -> List[str]:
        if not self.args:
            return [self.prefix]
        return [f"{self.prefix}:{arg}" for arg in self.args]

    def sub_topic(self) -> str:
        if not self.args:
            return self.prefix
        return f"{self.prefix}:{','.join(self.args)}"
