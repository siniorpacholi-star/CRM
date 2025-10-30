# app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from app.core.database import get_main_db
from app.models.main_db import ClientOrganization
from app.managers.client_db_manager import client_db_manager
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()


# ------------------------------------------------------
# 1️⃣ Регистрация нового клиента через JSON (index.html)
# ------------------------------------------------------
@router.post("/clients")
async def create_client_organization(
    data: dict = Body(...),
    db: Session = Depends(get_main_db)
):
    """
    Регистрация клиента через JSON-запрос от фронтенда (index.html).
    Создаёт клиентскую организацию и БД client_{id}, а также пользователя-владельца.
    """
    try:
        # 1️⃣ Извлекаем данные из JSON
        company_name = data.get("company_name", "").strip()
        notes = data.get("notes", "").strip()
        email = data.get("email", "").strip()
        phone = data.get("phone", "").strip()
        contact_person = data.get("contact_person", "").strip()
        login = data.get("login", "").strip()
        password = data.get("password", "").strip()

        if not company_name:
            raise HTTPException(status_code=400, detail="Не указано название организации.")
        if not login or not password:
            raise HTTPException(status_code=400, detail="Не указан логин или пароль пользователя.")
        if not email:
            raise HTTPException(status_code=400, detail="Не указан email пользователя.")

        # 2️⃣ Создаём клиента (автоматически создаёт БД client_{id})
        client_org = UserService.create_client_organization(
            db=db,
            company_name=company_name,
            notes=notes
        )

        # 3️⃣ Создаём пользователя-владельца (основная БД + клиентская)
        UserService.create_client_user(
            db=db,
            client_organization_id=client_org.id,
            email=email,
            login=login,
            password=password,
            full_name=contact_person or login,
            phone=phone
        )

        logger.info(f"✅ Клиент зарегистрирован: {company_name} (DB: {client_org.database_name})")

        return JSONResponse(
            {
                "success": True,
                "message": f"Клиент '{company_name}' успешно зарегистрирован.",
                "client_id": client_org.id,
                "database_name": client_org.database_name
            },
            status_code=201
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка регистрации клиента: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка регистрации клиента: {e}")


# ------------------------------------------------------
# 2️⃣ Ручное создание БД клиента (через админку)
# ------------------------------------------------------
@router.post("/clients/{client_id}/create-database")
async def create_database_for_client(client_id: int, db: Session = Depends(get_main_db)):
    """
    Ручное создание клиентской базы данных (client_{id}).
    """
    logger.info(f"Создание БД для клиентской организации {client_id}")

    client = db.query(ClientOrganization).filter(ClientOrganization.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")

    try:
        desired_name = client.database_name or f"client_{client.id}"
        created_name = client_db_manager.create_client_database(client, database_name=desired_name)

        client.database_name = created_name
        db.commit()

        logger.info(f"✅ Клиентская БД '{created_name}' успешно создана.")
        return JSONResponse(
            {
                "success": True,
                "message": f"База данных '{created_name}' успешно создана.",
                "database_name": created_name
            }
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка создания БД для клиента: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания БД: {e}")
