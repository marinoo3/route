from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import api, route
from app.services import RagService, PlotService




@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup logic ---
    app.state.db_service = DBService()

    yield

    # --- shutdown logic ---
    del app.state.db_service


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(route.router)
app.include_router(api.router)