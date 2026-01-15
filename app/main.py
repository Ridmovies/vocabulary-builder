from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


from app.api.v1.user import router as user_router
from app.api.v1.auth import router as auth_router
from app.api.v1.words import router as words_router
from app.api.v1.category import router as category_router
from app.api.v1.typing import router as typing_router
from app.api.v1.dev import router as dev_router
from app.core.seed import seed

from app.web.routers.router import router as web_typing_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic.
    print("🚀 Starting application...")
    await seed()
    yield



app = FastAPI(
    lifespan=lifespan
)

# Папка с HTML-шаблонами
templates = Jinja2Templates(directory="templates")

# Статика: CSS, JS, картинки
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router=user_router, prefix="/api/users", tags=["users"])
app.include_router(router=auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(router=dev_router, prefix="/api/dev", tags=["dev"])
app.include_router(router=words_router, prefix="/api/words", tags=["words"])
app.include_router(router=category_router, prefix="/api/categories", tags=["categories"])
app.include_router(router=typing_router, prefix="/api/web", tags=["web"])

app.include_router(router=web_typing_router)