from dataclasses import dataclass, field

from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class Session:
    device_id: str
    id: UUID = field(default=uuid4())
    create_time: datetime = field(default=datetime.now())