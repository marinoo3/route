

class DBError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

class BufferError(Exception):
    def __init__(self, message: str, session_id: str) -> None:
        super().__init__(f"{message} - session {session_id}")