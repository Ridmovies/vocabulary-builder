from starlette import status
from starlette.responses import Response

from app.core.security import create_access_token, create_refresh_token, create_csrf_token, set_auth_cookies
from app.crud.crud_user import user_crud
from app.crud.crud_words import word_crud
from app.schemas.words import WordCreate

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.api.deps import DBSession, UserDep

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        user: UserDep,
):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user
        }
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """ТОЛЬКО отображение страницы."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/create-word", response_class=HTMLResponse)
async def create_word_page(
    request: Request,
    current_user: UserDep,  # если страница защищена
):
    """Страница создания слова."""
    return templates.TemplateResponse(
        "create_word.html",
        {"request": request, "current_user": current_user}
    )
