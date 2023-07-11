from datetime import date

from sqlalchemy import Date
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class Holiday(Base):
    __tablename__ = 'holiday'
    __tableargs__ = {
        'comment': 'Информация о праздничных днях'
    }

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, comment='Праздничная дата')

    def __str__(self) -> str:
        return f'id={self.id}, date={self.date}'

    def __repr__(self) -> str:
        return str(self)
