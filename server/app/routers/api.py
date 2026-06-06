from fastapi import APIRouter, Request, Body

from app.models import BonjourRequest, IMUBuffer
from app.models.exceptions import DBError, BufferError
from app.services import DBService


router = APIRouter(
    prefix="/api",
    tags=["api"]
)

start_time = None


@router.post("/create_session", summary="Create a route session")
async def create_session(body: BonjourRequest, request: Request):
    """
    Create a route session

    Args:
        request (Request): Default request argument

    Returns:
        json: {
            session_id (str): The UUID of the created session
        }
    """
    db_service: DBService = request.app.state.db_service
    session = db_service.create_session(body.api_key, body.device_id)

    return {
        'session_id': session.id
    }

@router.post("/register_route_buffer", summary="Register IMU data buffer in a route")
async def register_route_buffer(
        session_id: str,
        data: bytes = Body(..., media_type="application/octet-stream"),
        request: Request = None
    ):
    """
    Register IMU data buffer in a route

    Args:
        session_id (str): Session ID
        data (bytes): Binary encoded payload (header + samples)
        request (Request): Default request argument
    """
    global start_time
    db_service: DBService = request.app.state.db_service

    buffer = IMUBuffer(
        session_id=session_id,
        binary=data
    )

    if start_time is not None:
        print(buffer.timestamp_start - start_time)
    start_time = buffer.timestamp_start

    try:
        db_service.register_samples(buffer.samples, buffer.session_id)
    except (DBError, BufferError) as e:
        print(e)