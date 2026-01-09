from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.api.v1.words import router as words_router
from app.api.v1.category import router as category_router
from app.api.v1.typing import router as typing_router
from app.api.v1.dev import router as dev_router

from app.routers.typing import router as web_typing_router



app = FastAPI()

# Папка с HTML-шаблонами
templates = Jinja2Templates(directory="templates")

# Статика: CSS, JS, картинки
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router=dev_router, prefix="/api/dev", tags=["dev"])
app.include_router(router=words_router, prefix="/api/words", tags=["words"])
app.include_router(router=category_router, prefix="/api/categories", tags=["categories"])
app.include_router(router=typing_router, prefix="/api/typing", tags=["typing"])


app.include_router(router=web_typing_router)