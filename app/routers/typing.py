from starlette import status
from starlette.responses import Response, RedirectResponse

from app.core.security import create_access_token, create_refresh_token, create_csrf_token, set_auth_cookies
from app.crud.crud_user import user_crud
from app.crud.crud_words import word_crud
from app.schemas.user import UserLogin
from app.schemas.words import WordCreate

from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.api.deps import DBSession, UserDep

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/typing", response_class=HTMLResponse)
async def typing_page(request: Request):
    return templates.TemplateResponse("typing.html", {"request": request})


# GET — отображение формы
@router.get("/create-word", response_class=HTMLResponse)
async def create_word_page(request: Request):
    return templates.TemplateResponse("create_word.html", {"request": request})


@router.post("/create-word", response_class=HTMLResponse)
async def create_word_form(
    request: Request,
    session: DBSession,          # ✅ БЕЗ Depends
    current_user: UserDep,       # ✅ БЕЗ Depends
    english: str = Form(...),
    russian: str = Form(...),
    category_ids: list[int] = Form([]),
):
    """
    Обработка формы создания слова.
    """
    word_in = WordCreate(
        english=english,
        russian=russian,
        category_ids=category_ids if category_ids else None
    )
    word = await word_crud.create_with_categories(
        db=session,
        obj_in=word_in,
        owner_id=current_user.id
    )
    return templates.TemplateResponse(
        "create_word.html",
        {"request": request, "created_word": word, "message": "Слово успешно создано!"}
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа."""
    # Если уже авторизован - перенаправляем
    from app.api.deps import get_current_user
    current_user = await get_current_user(request)

    if current_user:
        return RedirectResponse("/typing", status_code=303)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "current_user": None,
            "page_title": "Вход",
            "error": None
        }
    )