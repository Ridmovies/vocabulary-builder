import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()



THEORY_PATH = Path("app/theory/")


@router.get(
    "/topics",
    summary="Список тем",
    description="Возвращает список всех доступных тем из JSON."
)
async def get_topics():
    with open(THEORY_PATH / "topics.json", encoding="utf-8") as f:
        return json.load(f)


@router.get(
    "/topics/{slug}",
    summary="Получить тему",
    description="Возвращает тему по slug вместе с содержимым в формате Markdown."
)
async def get_topic(slug: str):
    file_path = THEORY_PATH / "cards" / f"{slug}.md"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Topic not found")

    return {
        "slug": slug,
        "title": slug.replace("-", " ").title(),
        "markdown": file_path.read_text(encoding="utf-8")
    }