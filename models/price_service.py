from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    String,
)

from models.base import Base

class Price_ticket(Base):

    __tablename__ = 'price_ticket'
    __tableargs__ = {
        'comment': 'Прайс-лист услуг'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    description = Column(String(64), comment='Описание')
    price = Column(SmallInteger, comment='Цена в будний день')


    def __repr__(self):
        return f'{self.id} {self.description} {self.price}'
