from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db_optional, db_available, db_error_message
from models import User
from auth import get_password_hash, verify_password, create_access_token, decode_token
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _get_token_payload(request: Request) -> Optional[dict]:
    token = request.cookies.get("access_token")
    if token:
        return decode_token(token)
    return None


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if _get_token_payload(request):
        return RedirectResponse(url="/tasks", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "db_available": db_available,
        "db_error": db_error_message if not db_available else "",
        "error": "",
    })


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Optional[Session] = Depends(get_db_optional),
):
    if db is None:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "db_available": False,
            "db_error": db_error_message,
            "error": "Banco de dados indisponível. Tente novamente mais tarde.",
        })

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "db_available": True,
            "db_error": "",
            "error": "E-mail ou senha incorretos.",
        })

    token = create_access_token({"sub": str(user.id), "name": user.name})
    response = RedirectResponse(url="/tasks", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=30 * 24 * 60 * 60,
        samesite="lax",
    )
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    if _get_token_payload(request):
        return RedirectResponse(url="/tasks", status_code=302)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "db_available": db_available,
        "db_error": db_error_message if not db_available else "",
        "error": "",
        "success": "",
    })


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Optional[Session] = Depends(get_db_optional),
):
    if db is None:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "db_available": False,
            "db_error": db_error_message,
            "error": "Banco de dados indisponível. Tente novamente mais tarde.",
            "success": "",
        })

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "db_available": True,
            "db_error": "",
            "error": "E-mail já cadastrado.",
            "success": "",
        })

    user = User(name=name, email=email, hashed_password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "name": user.name})
    response = RedirectResponse(url="/tasks", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=30 * 24 * 60 * 60,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
