from sqlalchemy import (
    Column,
    SmallInteger,
    Date,
)

from db.models.base import Base


class Price(Base):

    __tablename__ = 'price'
    __tableargs__ = {
        'comment': 'Информация о ценах'
    }

    id = Column(
        SmallInteger,
        nullable=False,
        unique=True,
        primary_key=True,
    )
    price = Column(SmallInteger, comment='Цена')
    update = Column(Date, nullable=False, comment='Дата изменения')


    def __str__(self):
        return f'{self.id} {self.price} {self.update}'


    def __repr__(self):
        return str(self)
