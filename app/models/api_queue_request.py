from typing import Literal


class APIQueueRequest:
    
    def __init__(
            self, 
            endpoint: str,
            payload: dict,
            kind: Literal["upload", "predict"]
            ) -> None:
        self.endpoint = endpoint
        self.payload = payload
        self.kind = kind