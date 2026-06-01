from fastapi import APIRouter, Request

from app.models import BonjourRequest, IMUBufferRequest
from app.models.exceptions import DBError, BufferError
from app.services import DBService


router = APIRouter(
    prefix="/api",
    tags=["api"]
)


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
async def register_route_buffer(body: IMUBufferRequest, request: Request):
    """
    Create a route session

    Args:
        request (Request): Default request argument

    Returns:
        json: {
            success (bool): Successfully saved the buffer in database
        }
    """
    db_service: DBService = request.app.state.db_service
    success = False

    try:
        samples = body.decode_samples()
        db_service.register_samples(samples, body.session_id, body.window_id)
        success = True
    except (DBError, BufferError) as e:
        print(e)

    return {
        'success': success
    }