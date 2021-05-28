from sqlalchemy import (
    Column,
    String,
    Integer,
)

from models.base import Base

class Currency_type(Base):

    __tablename__ = 'currency_type'
    __tableargs__ = {
        'comment': 'Тип валюты'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    description = Column(String(16), comment='Описание')


    def __repr__(self):
        return f'{self.id} {self.description}'
