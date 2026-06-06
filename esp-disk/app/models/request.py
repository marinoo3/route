class APIQueueRequest:

    def __init__(
            self,
            kind: str,
            endpoint: str,
            headers: dict|None = None,
            json: dict|None = None,
            data: bytes|None = None,
            ) -> None:
        self.kind = kind
        self.endpoint = endpoint
        self.headers = headers
        self.json = json
        self.data = data
