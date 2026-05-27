import os

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from routers import auth as auth_router
from routers import tasks as tasks_router
from database import db_available

app = FastAPI(title="TaskFlow", description="Gerenciador de Tarefas")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth_router.router)
app.include_router(tasks_router.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/login", status_code=302)


@app.get("/health")
async def health():
    if db_available:
        return {"status": "ok"}
    return JSONResponse(
        status_code=503,
        content={"status": "unhealthy", "detail": "Database unavailable"}
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    if "indisponível" in str(exc) or "not available" in str(exc).lower():
        return JSONResponse(
            status_code=503,
            content={"detail": "Banco de dados indisponível. Tente novamente mais tarde."},
        )
    raise exc
