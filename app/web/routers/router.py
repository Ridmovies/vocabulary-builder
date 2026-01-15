from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.api.deps import UserDep, UserDepOptional

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")

@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        user: UserDepOptional,
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

@router.get("/my-words", response_class=HTMLResponse)
async def words_page(
    request: Request,
    current_user: UserDep,
    category_ids: list[int] | None = Query(
        None, description="Фильтр по категориям"
    )
):
    """Страница со списком слов."""
    return templates.TemplateResponse(
        "words.html",
        {
            "request": request,
            "current_user": current_user,
            "initial_category_ids": category_ids or []
        }
    )


@router.get("/typing-exercise", response_class=HTMLResponse)
async def typing_exercise_page(request: Request):
    """
    Страница с упражнениями на набор текста
    """
    return templates.TemplateResponse(
        "typing_exercise.html",
        {"request": request}
    )