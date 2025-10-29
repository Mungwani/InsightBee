from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String, Integer, Date, func

class Base(DeclarativeBase): pass

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    corp_code:  Mapped[str] = mapped_column(String(8), unique=True, index=True)
    name_ko:    Mapped[str] = mapped_column(String(120))
    name_en:    Mapped[str | None] = mapped_column(String(160))
    stock_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
)