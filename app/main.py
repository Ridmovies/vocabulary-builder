from fastapi import FastAPI

from app.api.v1.words import router as words_router
from app.api.v1.category import router as category_router

from app.api.v1.dev import router as dev_router

app = FastAPI()

app.include_router(router=dev_router, prefix="/dev", tags=["dev"])
app.include_router(router=words_router, prefix="/words", tags=["words"])
app.include_router(router=category_router, prefix="/categories", tags=["categories"])
