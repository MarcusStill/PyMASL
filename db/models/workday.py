from sqlalchemy import (
    Column,
    SmallInteger,
    Date,
)

from db.models.base import Base


class Workday(Base):

    __tablename__ = 'workday'
    __tableargs__ = {
        'comment': 'Информация о рабочих днях'
    }

    id = Column(
        SmallInteger,
        nullable=False,
        unique=True,
        primary_key=True,
    )
    date = Column(Date, nullable=False, comment='Рабочий день')


    def __str__(self):
        return f'{self.id} {self.date}'


    def __repr__(self):
        return str(self)
