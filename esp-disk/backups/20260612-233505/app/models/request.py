class APIRequest:

    def __init__(
            self,
            endpoint: str,
            headers: dict|None = None,
            json: dict|None = None,
            data: bytes|None = None,
            post_action: "Callable"|None = None
            ) -> None:
        self.endpoint = endpoint
        self.headers = headers
        self.json = json
        self.data = data
        self.post_action = post_action