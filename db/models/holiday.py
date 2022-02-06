from sqlalchemy import (
    Column,
    SmallInteger,
    Date,
)

from db.models.base import Base


class Holiday(Base):

    __tablename__ = 'holiday'
    __tableargs__ = {
        'comment': 'Информация о праздничных днях'
    }

    id = Column(
        SmallInteger,
        nullable=False,
        unique=True,
        primary_key=True,
    )
    date = Column(Date, nullable=False, comment='Праздничная дата')


    def __str__(self):
        return f'{self.id} {self.date}'


    def __repr__(self):
        return str(self)
