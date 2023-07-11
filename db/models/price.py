from datetime import date

from sqlalchemy import Date, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class Price(Base):
    __tablename__ = 'price'
    __tableargs__ = {
        'comment': 'Информация о ценах'
    }

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    price: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment='Цена')
    update: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата изменения')

    def __str__(self) -> str:
        return f'id={self.id}, price={self.price}, update={self.update}'

    def __repr__(self) -> str:
        return str(self)
