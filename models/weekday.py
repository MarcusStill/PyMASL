from sqlalchemy import (
    Column,
    Date,
    Integer,
)

from models.base import Base


class Weekday(Base):
    __tablename__ = 'Weekday'
    __tableargs__ = {
        'comment': 'Перечень рабочих дней'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    date = Column(Date, nullable=False, comment='Дата')


    def __repr__(self):
        return f'{self.id} {self.date}'
