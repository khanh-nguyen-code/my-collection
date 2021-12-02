from typing import Any


class Codec:
    def marshal(self, o: Any) -> bytes:
        raise NotImplemented

    def unmarshal(self, b: bytes) -> Any:
        raise NotImplemented
