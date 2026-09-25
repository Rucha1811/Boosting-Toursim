import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.database import Base, SessionLocal, engine
from .models import CommunityReport  # noqa: F401  (register all models)
from .models import User  # noqa: F401
from .api.routes import assistant, auth, authority, businesses, discovery, map2, reports, ws  # noqa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("virsa")

settings = get_settings()

from .services.simulator import simulator_loop  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.SEED_ON_STARTUP:
        from .seed.seed import seed_all, is_seeded

        if not is_seeded():
            logger.info("Seeding demonstration data for Vadodara…")
            seed_all()
            logger.info("Seed complete.")
    from .seed.seed import train_classifier_from_reports

    train_classifier_from_reports()

    stop = asyncio.Event()
    task = asyncio.create_task(simulator_loop(stop))
    app.state.simulator_task = task
    app.state.simulator_stop = stop
    logger.info("Virsa API ready 🚀 (%s)", settings.APP_VERSION)
    try:
        yield
    finally:
        stop.set()
        task.cancel()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Community-centric intelligent tourism ecosystem for Vadodara, Gujarat.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = settings.API_PREFIX

for router in (
    auth.router,
    discovery.router,
    map2.router,
    reports.router,
    businesses.router,
    authority.router,
    assistant.router,
    ws.router,
):
    app.include_router(router, prefix=API_PREFIX)


@app.get("/")
def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "ok", "demo": settings.DEMO_MODE}