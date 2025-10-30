# app/models/client_template.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship, declarative_base

ClientBase = declarative_base()


# ===========================================================
# 1️⃣ Пользователи клиента
# ===========================================================
class ClientUser(ClientBase):
    __tablename__ = "client_users"

    id = Column(Integer, primary_key=True, index=True)
    main_user_id = Column(Integer, nullable=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    login = Column(String(255), nullable=False)
    profile_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    accesses = relationship("ClientUserClientAccess", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClientUser(id={self.id}, login='{self.login}', email='{self.email}')>"


# ===========================================================
# 2️⃣ Клиенты (организации)
# ===========================================================
class Client(ClientBase):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    short_name = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    inn = Column(String(64), nullable=True)
    kpp = Column(String(64), nullable=True)
    ogrn = Column(String(64), nullable=True)
    address = Column(String(512), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Client(id={self.id}, full_name='{self.full_name}')>"


# ===========================================================
# 3️⃣ Права пользователей к клиентам
# ===========================================================
class ClientUserClientAccess(ClientBase):
    __tablename__ = "client_user_client_access"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("client_users.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    can_view_calendar = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("ClientUser", back_populates="accesses")
    client = relationship("Client")

    def __repr__(self):
        return f"<ClientUserClientAccess(user_id={self.user_id}, client_id={self.client_id}, can_view_calendar={self.can_view_calendar})>"


# ===========================================================
# 4️⃣ Электронные подписи
# ===========================================================
class DigitalSignature(ClientBase):
    __tablename__ = "digital_signatures"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    owner_name = Column(String(255), nullable=False)
    certificate_number = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client = relationship("Client")

    def __repr__(self):
        return f"<DigitalSignature(id={self.id}, owner='{self.owner_name}', end_date={self.end_date})>"


# ===========================================================
# 5️⃣ Настройки компании
# ===========================================================
class CompanySettings(ClientBase):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=True)
    logo_path = Column(String(512), nullable=True)
    currency = Column(String(16), nullable=True, default="RUB")
    timezone = Column(String(64), nullable=True, default="Europe/Moscow")
    fiscal_year_start = Column(String(16), nullable=True, default="01.01")
    report_email = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    address = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CompanySettings(company_name='{self.company_name}')>"


# ===========================================================
# 6️⃣ Периоды отчётности
# ===========================================================
class ReportPeriod(ClientBase):
    __tablename__ = "report_periods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ReportPeriod(name='{self.name}', start_date={self.start_date}, end_date={self.end_date})>"


# ===========================================================
# 7️⃣ Шаблоны отчётов
# ===========================================================
class ReportTemplate(ClientBase):
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ReportTemplate(id={self.id}, name='{self.name}')>"


# ===========================================================
# 8️⃣ Отчёты
# ===========================================================
class Report(ClientBase):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("report_templates.id"))
    period_id = Column(Integer, ForeignKey("report_periods.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    created_by = Column(Integer, ForeignKey("client_users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(64), nullable=True)
    file_path = Column(String(512), nullable=True)

    template = relationship("ReportTemplate")
    creator = relationship("ClientUser")
    client = relationship("Client")
    report_period = relationship("ReportPeriod")

    def __repr__(self):
        return f"<Report(id={self.id}, client_id={self.client_id}, status='{self.status}')>"


# ===========================================================
# 9️⃣ История отчётов
# ===========================================================
class ClientReportHistory(ClientBase):
    __tablename__ = "client_report_history"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"))
    changed_by = Column(Integer, ForeignKey("client_users.id"))
    change_type = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    report = relationship("Report")
    user = relationship("ClientUser")

    def __repr__(self):
        return f"<ClientReportHistory(report_id={self.report_id}, change_type='{self.change_type}')>"


# ===========================================================
# 🔟 Справочник календаря (CalendarHandbook)
# ===========================================================
class CalendarHandbook(ClientBase):
    __tablename__ = "calendar_handbook"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    default_day = Column(Integer, nullable=True)  # день месяца, если повторяется
    default_month = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CalendarHandbook(id={self.id}, name='{self.name}')>"


# ===========================================================
# 11️⃣ События календаря
# ===========================================================
class CalendarEvent(ClientBase):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    handbook_id = Column(Integer, ForeignKey("calendar_handbook.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client")
    handbook = relationship("CalendarHandbook")

    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, title='{self.title}', date={self.date})>"


# ===========================================================
# 12️⃣ Совместимость: Organization
# ===========================================================
Organization = Client
