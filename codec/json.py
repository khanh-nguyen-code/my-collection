import json
from typing import Any

from codec import Codec


class Json(Codec):
    def marshal(self, o: Any) -> bytes:
        return json.dumps(o).encode("utf-8")

    def unmarshal(self, b: bytes) -> Any:
        return json.loads(b)
