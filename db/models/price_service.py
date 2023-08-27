from datetime import date

from sqlalchemy import Date, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class PriceService(Base):
    __tablename__ = 'price_service'
    __tableargs__ = {
        'comment': 'Информация о ценах на доп. услуги'
    }

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment='Название')
    price: Mapped[int] = mapped_column(SmallInteger, nullable=False, comment='Цена')
    update: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата изменения')

    def __str__(self) -> str:
        return f'id={self.id}, name={self.name}, price={self.price}'

    def __repr__(self) -> str:
        return str(self)
