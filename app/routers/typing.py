from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/typing", response_class=HTMLResponse)
async def typing_page(request: Request):
    return templates.TemplateResponse("typing.html", {"request": request})