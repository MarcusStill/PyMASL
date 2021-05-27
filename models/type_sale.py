from sqlalchemy import (
    Column,
    Integer,
    String,
)

from models.base import Base

class Type_sale(Base):

    __tablename__ = 'type_sale'
    __tableargs__ = {
        'comment': 'Информация о типах продаж'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    description = Column(String(16), nullable=False, comment='Описание')


    def __repr__(self):
        return f'{self.id} {self.description}'
