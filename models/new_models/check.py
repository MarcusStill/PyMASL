from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from models.base import Base

class Check(Base):

    __tablename__ = 'check'
    __tableargs__ = {
        'comment': 'Чеки'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    id_sale = Column(Integer, ForeignKey('sale.id'), comment='Id продажи')
    check_sale = Column(Text, comment='Чек продажи')
    check_return = Column(Text, comment='Чек возврата')
    bank_sale = Column(Text, comment='Чек банк')
    bank_return = Column(Text, comment='Чек возврата банк')
    sale = relationship('sale', backref='check_sale', lazy='subquery')


    def __repr__(self):
        return f'{self.id} {self.id_sale} {self.id_user} {self.check_sale} {self.check_return} {self.bank_sale} {self.bank_return}'
