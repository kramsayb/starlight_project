from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1.routers import batches, products
from src.core.config import settings
from src.core.database import dispose_engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await dispose_engine()


app = FastAPI(title=settings.app_name,lifespan=lifespan)
app.include_router(batches.router, prefix=settings.api_v1_prefix)
app.include_router(products.router, prefix=settings.api_v1_prefix)