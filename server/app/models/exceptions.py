

class DBError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class BufferError(Exception):
    def __init__(self, message: str, session_id: str) -> None:
        super().__init__(f"{message} - session {session_id}")

class InvalidIMUPayloadError(ValueError):
    """Raised when an IMU binary payload is malformed."""
    def __init__(
            self, 
            message: str
        ) -> None:
        super().__init__(message)