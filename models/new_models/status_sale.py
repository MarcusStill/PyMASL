from sqlalchemy import (
    Column,
    Integer,
    String,
)

from models.base import Base

class Status_sale(Base):

    __tablename__ = 'status_sale'
    __tableargs__ = {
        'comment': 'Информация о статусе продажи'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    status = Column(String(16), nullable=False, comment='Описание')


    def __repr__(self):
        return f'{self.id} {self.description}'
