import socketio
from auth import auth_routers
from auth.utils.auth_utils import create_superuser
from config.database import database
from config.settings import settings
from fastapi import FastAPI
from meetups import meetups_routers
from meetups_logging import logger
from middlewares.auth_middleware import AuthMiddleware
from middlewares.request_middleware import RequestContextMiddleware
from sio_server import sio
from starlette.middleware.authentication import AuthenticationMiddleware
from worker.celery import create_celery

# Create FastAPI app
fastapi = FastAPI(title=settings.app_name)

# Create Celery app
fastapi.celery_app = create_celery()
celery = fastapi.celery_app

# Create socketio app
app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=fastapi)

# Adding fastapi routers
fastapi.include_router(auth_routers.router, prefix="/users",
                       tags=["Users auth"])
fastapi.include_router(meetups_routers.router, prefix="/meetups",
                       tags=["Meetups"])
fastapi.include_router(meetups_routers.router_admin, prefix="/meetups/admin",
                       tags=["Admin meetups"])


@fastapi.on_event("startup")
async def startup():
    logger.info("Python meetups has been started")
    fastapi.add_middleware(AuthenticationMiddleware, backend=AuthMiddleware())
    fastapi.add_middleware(RequestContextMiddleware)
    await database.connect()
    await create_superuser()


@fastapi.on_event("shutdown")
async def shutdown():
    logger.info("Python meetups stopped")
    await database.disconnect()
