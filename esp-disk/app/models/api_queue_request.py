



class APIQueueRequest:
    
    def __init__(
            self, 
            endpoint: str,
            payload: dict,
            kind: str
            ) -> None:
        self.endpoint = endpoint
        self.payload = payload
        self.kind = kind