# app/main.py
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.database import _main_engine, check_and_create_tables, get_main_db
from app.routes import (
    auth,
    admin,
    client_auth,
    client_dashboard,
    client_clients,
    client_reports,
    client_users,
    calendar,
    calendar_handbook,
    client_settings,
    client_organizations,  # ✅ добавлен маршрут
)
from app.utils import templates

# ------------------------------------------------------------
# Настройки логирования
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Инициализация FastAPI
# ------------------------------------------------------------
app = FastAPI(title="CRM Accounting", version="2.0")

# ------------------------------------------------------------
# Middleware (CORS)
# ------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# Подключение статики
# ------------------------------------------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ------------------------------------------------------------
# Подключение маршрутов
# ------------------------------------------------------------
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Клиентская часть
app.include_router(client_auth.router, tags=["client_auth"])
app.include_router(client_dashboard.router, tags=["client_dashboard"])
app.include_router(client_clients.router, tags=["client_clients"])
app.include_router(client_reports.router, tags=["client_reports"])
app.include_router(client_users.router, tags=["client_users"])
app.include_router(calendar.router, tags=["calendar"])
app.include_router(calendar_handbook.router, tags=["calendar_handbook"])
app.include_router(client_settings.router, tags=["client_settings"])
app.include_router(client_organizations.router, tags=["client_organizations"])

# ------------------------------------------------------------
# События старта и завершения
# ------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    """
    Проверка и создание таблиц при старте.
    """
    try:
        logger.info("🚀 Проверка/создание таблиц основной БД...")
        check_and_create_tables()
        logger.info("✅ Основная БД готова.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("🛑 Завершение работы приложения.")


# ------------------------------------------------------------
# Главная страница
# ------------------------------------------------------------
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse  # необязательно, но для типов

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Отображает стартовую страницу (index.html)
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )



# ------------------------------------------------------------
# Точка входа
# ------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
