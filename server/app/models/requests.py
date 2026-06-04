from pydantic import BaseModel


class AuthRequest(BaseModel):
    api_key: str

class BonjourRequest(AuthRequest):
    device_id: str