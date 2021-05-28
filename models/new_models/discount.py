from sqlalchemy import (
    Column,
    String,
    SmallInteger,
    Date,
    Boolean,
    Integer,
)

from models.base import Base

class Discount(Base):

    __tablename__ = 'discount'
    __tableargs__ = {
        'comment': 'скидки'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    description = Column(String(64), comment='Описание позиции')
    size = Column(SmallInteger, comment='Размер скидки в %')
    created_at = Column(Date, nullable=False, comment='Дата создания')
    status = Column(Boolean, comment='Статус')


    def __repr__(self):
        return f'{self.id} {self.description} {self.size} {self.created_at} {self.status}'
