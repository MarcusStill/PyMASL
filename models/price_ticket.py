from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    Text,
)

from models.base import Base

class Price_ticket(Base):

    __tablename__ = 'price_ticket'
    __tableargs__ = {
        'comment': 'Прайс-лист билетов'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    price = Column(SmallInteger, comment='Стоимость')
    price_weekend = Column(SmallInteger, comment='Цена выходного дня')
    description = Column(Text, comment='Описание позиции')


    def __repr__(self):
        return f'{self.id} {self.price} {self.price_weekend} {self.description}'
