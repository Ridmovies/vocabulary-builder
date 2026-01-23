import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()



THEORY_PATH = Path("app/theory/")


@router.get("/topics")
async def get_topics():
    with open(THEORY_PATH / "topics.json", encoding="utf-8") as f:
        return json.load(f)


@router.get("/topics/{slug}")
async def get_topic(slug: str):
    file_path = THEORY_PATH / "cards" / f"{slug}.md"
    # present-simple

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Topic not found")

    return {
        "slug": slug,
        "title": slug.replace("-", " ").title(),
        "markdown": file_path.read_text(encoding="utf-8")
    }
