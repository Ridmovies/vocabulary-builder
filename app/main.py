from fastapi import FastAPI

from app.api.v1.dev import router as dev_router
from app.api.v1.words import router as words_router

app = FastAPI()

app.include_router(router=dev_router, prefix="/dev", tags=["dev"])
app.include_router(router=words_router, prefix="/words", tags=["words"])
