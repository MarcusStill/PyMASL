from sqlalchemy import (
    Column,
    Integer,
    String,
)

from models.base import Base

class User_pc(Base):

    __tablename__ = 'user_pc'
    __tableargs__ = {
        'comment': 'Информация о РМ кассира'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    name = Column(String(16), nullable=False, comment='Имя РМ кассира')


    def __repr__(self):
        return f'{self.id} {self.name}'
