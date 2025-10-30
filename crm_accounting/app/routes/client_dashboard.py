# app/routes/client_dashboard.py
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import logging

from app.core.database import get_main_db
from app.utils import templates
from app.utils.client_utils import get_client_company_settings, get_today_date
from app.models.main_db import ClientOrganization
from app.managers.client_db_manager import client_db_manager
from app.models.client_template import CalendarHandbook, Client, Report

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/client/{client_id}/dashboard", response_class=HTMLResponse)
async def client_dashboard(
    client_id: int,
    request: Request,
    db: Session = Depends(get_main_db)
):
    """
    Клиентский дашборд — показывает отчёты, календарь и основную информацию.
    """
    org = db.query(ClientOrganization).filter(ClientOrganization.id == client_id).first()
    if not org or not org.database_name:
        raise HTTPException(status_code=404, detail="База клиента не найдена")

    session = client_db_manager.get_client_session(org.database_name)
    try:
        reports = session.query(Report).order_by(Report.id.desc()).limit(10).all()
        calendar = session.query(CalendarHandbook).order_by(CalendarHandbook.id.desc()).limit(10).all()
        clients_count = session.query(Client).count()
    except Exception as e:
        logger.error(f"Ошибка загрузки данных клиента {client_id}: {e}")
        reports, calendar, clients_count = [], [], 0
    finally:
        session.close()

    company_settings = get_client_company_settings(db, client_id)

    # Добавляем объект client (для client_base.html)
    client = {
        "id": client_id,
        "name": org.company_name or "Клиент"
    }

    # ⚙️ создаём структуру dashboard_data, как раньше использовалось в шаблонах
    dashboard_data = {
        "clients_count": clients_count,
        "reports": reports,
        "calendar": calendar,
        "today": get_today_date()
    }

    return templates.TemplateResponse(
        "client/dashboard.html",
        {
            "request": request,
            "client_id": client_id,
            "client": client,
            "company_settings": company_settings,
            "dashboard_data": dashboard_data,  # ✅ теперь шаблон получает dashboard_data.*
        }
    )
