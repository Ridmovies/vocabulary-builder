from random import choice, sample, shuffle

from fastapi import APIRouter, Query, HTTPException, UploadFile, File
from starlette import status

from app.api.deps import DBSession, UserDep
from app.crud.crud_words import word_crud
from app.schemas.typing import TypingCheckRequest
from app.schemas.words import WordCreate, WordRead, WordUpdate, WordQuiz
from app.services.favorites import FavoriteService
from app.services.image_storage_service import WordService
from app.services.typing import TypingService

router = APIRouter()


@router.get(
    "",
    response_model=list[WordRead],
    summary="Получить слова с фильтром и пагинацией",
    description=(
            "Фильтр по категориям. Можно указать список ID категорий. "
            "Возвращаются только слова из системных категорий (owner_id=None) и ваших категорий."
    ),
)
async def get_words(
    session: DBSession,
    current_user: UserDep,
    skip: int = Query(0, ge=0, description="Количество пропущенных слов"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество слов"),
    category_ids: list[int] | None = Query(
        None, description="Фильтр по категориям, список ID"
    ),
    is_favorite: bool = Query(
        False,
        description="Только избранные слова"
    ),
):
    """
    Получить слова с пагинацией и фильтром по категориям.
    """
    return await word_crud.get_multi_with_categories(
        db=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_favorite=is_favorite,
        category_ids=category_ids,
    )


@router.post(
    "",
    response_model=WordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое слово",
    description=(
        "Создаёт новое слово и связывает его с категориями текущего пользователя.\n\n"
        "- Пользователь может добавлять слово **только в свои категории**.\n"
        "- Системные или чужие категории использовать нельзя.\n"
        "- Возвращает созданное слово с его категориями."
    ),
)
async def create_words(
    session: DBSession,
    current_user: UserDep,
    word_in: WordCreate,
):
    """
    Создать слово с привязкой к категориям пользователя.
    """
    return await word_crud.create_with_categories(
        db=session,
        obj_in=word_in,
        owner_id=current_user.id
    )

@router.get("/quiz")
async def get_quiz(
        session: DBSession,
        current_user: UserDep,
        skip: int = Query(0, ge=0, description="Количество пропущенных слов"),
        limit: int = Query(100, ge=1, le=1000, description="Максимальное количество слов"),
        is_favorite: bool | None = Query(None, description="Фильтр по избранным"),
        category_ids: list[int] | None = Query(
            None, description="Фильтр по категориям, список ID"
        ),
):
    words = await word_crud.get_multi_with_categories(
        db=session,
        skip=skip,
        limit=limit,
        is_favorite=is_favorite,
        user_id=current_user.id,
        category_ids=category_ids,
    )
    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В выбранной категории нет слов"
        )
    # Получаем рандомное слово
    quiz_word = choice(words)
    correct_answer = quiz_word.russian

    # Берём все остальные переводы, кроме правильного
    wrong_answers_pool = [
        word.russian
        for word in words
        if word.id != quiz_word.id
    ]

    # Проверка на крайний случай
    if len(wrong_answers_pool) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недостаточно слов для генерации вариантов ответа"
        )

    # Выбираем 3 неправильных варианта
    wrong_answers = sample(wrong_answers_pool, 3)

    # Собираем варианты и перемешиваем
    options = wrong_answers + [correct_answer]
    shuffle(options)

    return {
        "word_id": quiz_word.id,
        "english": quiz_word.english,
        "options": options
    }


@router.post("/quiz")
async def check_quiz_answer(
        session: DBSession,
        current_user: UserDep,
        answer_in: WordQuiz
):
    word = await word_crud.get_for_user(
        db=session,
        user_id=current_user.id,
        word_id=answer_in.id
    )
    # Приводим слова к одному регистру
    user_answer = answer_in.russian.strip().lower()
    correct_answer = word.russian.strip().lower()

    return {
        "is_correct": user_answer == correct_answer
    }



@router.get("/quick", response_model=WordQuiz)
async def get_random_translation(
        session: DBSession,
        current_user: UserDep,
        skip: int = Query(0, ge=0, description="Количество пропущенных слов"),
        limit: int = Query(100, ge=1, le=1000, description="Максимальное количество слов"),
        is_favorite: bool | None = Query(None, description="Фильтр по избранным"),
        category_ids: list[int] | None = Query(
            None, description="Фильтр по категориям, список ID"
        )
):
    quick_translation = await word_crud.get_multi_with_categories(
        db=session,
        skip=skip,
        limit=limit,
        is_favorite=is_favorite,
        user_id=current_user.id,
        category_ids=category_ids,
    )
    if not quick_translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В выбранной категории нет слов"
        )

    random_quick = choice(quick_translation)
    return random_quick

@router.get(
    "/random",
    response_model=WordRead,
    description="""
    ### Фильтры (query-параметры):
    - **is_favorite** — фильтр по избранным (`true` или `false`).
    """
)
async def get_random_word(
        session: DBSession,
        current_user: UserDep,
        skip: int = Query(0, ge=0, description="Количество пропущенных слов"),
        limit: int = Query(100, ge=1, le=1000, description="Максимальное количество слов"),
        is_favorite: bool | None = Query(None, description="Фильтр по избранным"),
        category_ids: list[int] | None = Query(
            None, description="Фильтр по категориям, список ID"
        ),

):
    """
    Получить слова с пагинацией и фильтром по категориям.
    """
    words = await word_crud.get_multi_with_categories(
        db=session,
        skip=skip,
        limit=limit,
        is_favorite=is_favorite,
        user_id=current_user.id,
        category_ids=category_ids,
    )
    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В выбранной категории нет слов"
        )

    return choice(words)


@router.post("/check")
async def check_answer(
        session: DBSession,
        current_user: UserDep,
        request: TypingCheckRequest  # Получаем из body
):
    return await TypingService.check_answer(
        session=session,
        word_id=request.word_id,
        answer=request.answer,
    )

@router.get("/favorites", response_model=list[WordRead])
async def get_favorites(
    session: DBSession,
    current_user: UserDep,
):
    return await FavoriteService.get_favorites(
        session=session,
        user_id=current_user.id,
    )


@router.get("/{word_id}", response_model=WordRead)
async def get_word(
        session: DBSession,
        current_user: UserDep,
        word_id: int,
):
    return await word_crud.get(db=session, id=word_id)


@router.delete("/{word_id}", status_code=204)
async def delete_words(
        session: DBSession,
        current_user: UserDep,
        word_id: int,
):
    return await word_crud.remove(db=session, id=word_id)



@router.put("/{word_id}", response_model=WordRead)
async def update_words(
        session: DBSession,
        current_user: UserDep,
        word_id: int,
        word_in: WordUpdate,
):
    # Получаем слово
    word = await word_crud.get(db=session, id=word_id)
    return await word_crud.update_with_categories(db=session, obj_in=word_in, db_obj=word)


@router.post(
    path="/{word_id}/image",
    response_model=WordRead,
)
async def post_image(
        word_id: int,
        session: DBSession,
        current_user: UserDep,
        image: UploadFile = File(...),
):
    return await WordService.upload_word_image(
        db=session,
        word_id=word_id,
        image=image,
        user_id=current_user.id
    )


@router.delete(path="/{word_id}/image")
async def delete_image(
        word_id: int,
        session: DBSession,
        current_user: UserDep,
):
    return await WordService.delete_word_image(
        db=session,
        word_id=word_id,
        user_id=current_user.id
    )



@router.post("/favorites/{word_id}")
async def add_to_favorites(
    word_id: int,
    session: DBSession,
    current_user: UserDep,
):
    await FavoriteService.add_to_favorites(
        session=session,
        user_id=current_user.id,
        word_id=word_id,
    )
    return {"status": "added"}


@router.delete("/favorites/{word_id}")
async def remove_from_favorites(
    word_id: int,
    session: DBSession,
    current_user: UserDep,
):
    await FavoriteService.remove_from_favorites(
        session=session,
        user_id=current_user.id,
        word_id=word_id,
    )
    return {"status": "removed"}
