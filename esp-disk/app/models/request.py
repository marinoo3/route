from typing import Optional


class APIQueueRequest:

    def __init__(
            self,
            kind: str,
            endpoint: str,
            json: Optional[dict] = None,
            data: Optional[bytes] = None,
            ) -> None:
        self.kind = kind
        self.endpoint = endpoint
        self.json = json
        self.data = data