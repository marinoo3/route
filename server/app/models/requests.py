from app.models.exceptions import BufferError

from dataclasses import dataclass


@dataclass
class AuthRequest:
    api_key: str

@dataclass
class BonjourRequest(AuthRequest):
    device_id: str

@dataclass
class IMUBufferRequest:
    session_id: str
    window_id: str
    samples: bytes

    def decode_samples(self) -> list[dict]:
        """
        Decode binary encoded sample values

        Returns:
            list[dict]: Decoded sample
        """
        try:
            #TODO: decode binary
            pass
        except Exception:
            raise BufferError("Failed to decode buffer samples", self.session_id)
        
        return []