from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    SmallInteger,
    DateTime,
    String,
    Text,
)

from sqlalchemy.orm import relationship
from db.models.base import Base

class Sale(Base):

    __tablename__ = 'sale'
    __tableargs__ = {
        'comment': 'Продажи'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    id_client = Column(Integer, ForeignKey('client.id'), comment='Id клиента')
    id_user = Column(Integer, ForeignKey('user.id'), comment='Id пользователя')
    price = Column(Integer, comment='Цена')
    datetime = Column(DateTime, comment='Дата и время продажи')
    discount = Column(SmallInteger, comment='Скидка')
    status = Column(SmallInteger, comment='Статус продажи')
    pc_name = Column(String(16), comment='NetBIOS Name PC')
    payment_type = Column(SmallInteger, comment='Валюта оплаты')
    bank_pay = Column(Text, comment='Банковский чек оплаты')
    user_return = Column(Integer, comment='Id user return')
    datetime_return = Column(DateTime, comment='Дата и время возврата продажи')
    bank_return = Column(Text, comment='Банковский чек возврата')
    client = relationship('Client', backref='sale_client', lazy='subquery')
    user = relationship('User', backref='sale_user', lazy='subquery')


    def __str__(self):
        return f'{self.id} {self.id_client} {self.id_user} {self.price} {self.datetime} ' \
                f'{self.discount} {self.status} {self.pc_name} {self.payment_type} {self.bank_pay} {self.user_return}' \
                f'{self.datetime_return} {self.bank_return}'

    def __repr__(self):
        return str(self)
