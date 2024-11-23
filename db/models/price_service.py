from datetime import datetime

from sqlalchemy import Boolean, Integer, String, Text, Date, Interval
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class PriceService(Base):
    __tablename__ = "price_service"
    __tableargs__ = {
        "comment": "Таблица с прайс-листом для продажи дополнительных услуг"
    }

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="ID услуги",
    )
    price: Mapped[int] = mapped_column(Integer, nullable=False, comment="Цена услуги")
    updated_at: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        default=datetime.utcnow,
        comment="Дата последнего обновления",
    )
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Название услуги"
    )
    duration: Mapped[datetime] = mapped_column(
        Interval, nullable=True, comment="Продолжительность услуги"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Описание услуги"
    )
    min_visitors: Mapped[int] = mapped_column(
        Integer, default=0, nullable=True, comment="Минимальное количество посетителей"
    )
    max_visitors: Mapped[int] = mapped_column(
        Integer, default=0, nullable=True, comment="Максимальное количество посетителей"
    )
    requires_ticket: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Нужен ли билет для услуги"
    )
    deleted_flg: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Флаг удаления услуги"
    )

    def __str__(self) -> str:
        return (
            f"{self.id} {self.name} {self.price} {self.updated_at} {self.duration} "
            f"{self.description} {self.min_visitors} {self.max_visitors} "
            f"{self.requires_ticket} {self.deleted_flg}"
        )

    def __repr__(self) -> str:
        return str(self)
