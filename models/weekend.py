from sqlalchemy import (
    Column,
    Date,
    Integer,
)

from models.base import Base

class Weekend(Base):

    __tablename__ = 'Weekend'
    __tableargs__ = {
        'comment': 'Перечень праздничных и выходных дней'
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
