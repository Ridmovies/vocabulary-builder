from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import FileResponse

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



@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """ТОЛЬКО отображение страницы."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/logout", response_class=HTMLResponse)
async def logout_page(
    request: Request,
    user: UserDepOptional,
):
    """
    Страница выхода из системы
    """
    return templates.TemplateResponse(
        "logout.html",
        {
            "request": request,
            "user": user
        }
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    user: UserDepOptional,
):
    """
    Страница регистрации нового пользователя
    """
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user": user
        }
    )

@router.get("/create-word", response_class=HTMLResponse)
async def create_word_page(
        request: Request,
        user: UserDep,  # Меняем current_user на user
):
    """Страница создания слова."""
    return templates.TemplateResponse(
        "create_word.html",
        {"request": request, "user": user}
    )

@router.get("/my-words", response_class=HTMLResponse)
async def words_page(
    request: Request,
    user: UserDep,
    category_ids: list[int] | None = Query(
        None, description="Фильтр по категориям"
    )
):
    """Страница со списком слов."""
    return templates.TemplateResponse(
        "words.html",
        {
            "request": request,
            "user": user,
            "initial_category_ids": category_ids or []
        }
    )


@router.get("/typing-exercise", response_class=HTMLResponse)
async def typing_exercise_page(
        request: Request,
        user: UserDep,
):
    """
    Страница с упражнениями на набор текста
    """
    return templates.TemplateResponse(
        "typing_exercise.html",
        {"request": request, "user": user}
    )


@router.get("/categories", response_class=HTMLResponse)
async def categories_page(
    request: Request,
    user: UserDep,
):
    """
    Страница управления категориями
    """
    return templates.TemplateResponse(
        "categories.html",
        {
            "request": request,
            "user": user
        }
    )


# @router.get("/grammar/{slug}", response_class=HTMLResponse)
# async def grammar_lesson_page(
#     request: Request,
#     user: UserDep,
# ):
#     """
#     Страница урока грамматики
#     Просто отображает шаблон, данные загружаются через API на фронте
#     """
#     return templates.TemplateResponse(
#         "grammar_lesson.html",
#         {
#             "request": request,
#             "user": user,
#             # lesson не передаем, он загружается через API на фронте
#         }
#     )

@router.get("/grammar/{slug}", response_class=HTMLResponse)
async def grammar_topic_page(
    request: Request,
    user: UserDep,
    slug: str
):
    """
    Страница темы грамматики (Markdown версия)
    """
    return templates.TemplateResponse(
        "grammar_topic.html",
        {
            "request": request,
            "user": user,
            "slug": slug  # Передаем slug для загрузки данных на фронте
        }
    )