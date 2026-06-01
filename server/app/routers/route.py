from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter(
    tags=["route"]
)



@router.get("/ping")
async def ping():
    """Simple health check endpoint."""
    return {"status": "ok"}

@router.get("/")
def root():
    return RedirectResponse(url="/docs")