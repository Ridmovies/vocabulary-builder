from fastapi import FastAPI

from app.api.v1.dev import router as dev_router

app = FastAPI()

app.include_router(router=dev_router, prefix="/dev", tags=["dev"])
