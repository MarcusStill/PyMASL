from datetime import date

from sqlalchemy import Date
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class Workday(Base):

    __tablename__ = "workday"
    __tableargs__ = {"comment": "Информация о рабочих днях"}

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, comment="Рабочий день")

    def __str__(self) -> str:
        return f"{self.id} {self.date}"

    def __repr__(self) -> str:
        return str(self)
