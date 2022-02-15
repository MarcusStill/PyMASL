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
    )
    id_client = Column(Integer, ForeignKey('client.id'), comment='Id клиента')
    id_user = Column(Integer, ForeignKey('user.id'), comment='Id пользователя')
    #id_currency_type = Column(Integer, ForeignKey('currency_type.id'), comment='Id типа валюты')
    #id_status_sale = Column(Integer, ForeignKey('status_sale.id'), comment='Id статуса продажи')
    #id_discount = Column(Integer, ForeignKey('discount.id'), comment='Id скидки')
    price = Column(SmallInteger, comment='Цена')
    #datetime = Column(DateTime, default=datetime.utcnow, comment='Дата и время продажи')
    datetime = Column(DateTime, comment='Дата и время продажи')
    datetime_save = Column(DateTime, comment='Дата и время сохранения продажи')
    discount = Column(SmallInteger, comment='Скидка')
    datetime_save = Column(DateTime, comment='Дата и время сохранения продажи')
    status = Column(SmallInteger, comment='Статус продажи')
    pc_name = Column(String(16), comment='NetBIOS Name PC')
    discount = Column(SmallInteger, comment='Скидка')
    payment_type = Column(SmallInteger, comment='Валюта оплаты')
    bank_pay = Column(Text, comment='Банковский чек оплаты')
    user_return = Column(Integer, comment='Id user return')
    datetime_return = Column(DateTime, comment='Дата и время возврата продажи')
    bank_return = Column(Text, comment='Банковский чек возврата')
    client = relationship('Client', backref='sale_client', lazy='subquery')
    #currency_type = relationship('currency_type', backref='sale_currency_type', lazy='subquery')
    #status_sale = relationship('status_sale', backref='sale_status_sale', lazy='subquery')
    #pc_name = relationship('pc_name', backref='sale_user_pc', lazy='subquery')
    user = relationship('User', backref='sale_user', lazy='subquery')
    # pc_name = Column(String(16), comment='Id РМ кассира')
    # status_sale = Column(SmallInteger, comment='Статус продажи')
    # datetime_save = Column(DateTime, default=datetime.utcnow, comment='Дата и время сохранения продажи')
    # discount = Column(SmallInteger, comment='Скидка')
    # datetime_save = Column(DateTime, default=datetime.utcnow, comment='Дата и время сохранения продажи')
    # status = Column(SmallInteger, comment='Статус продажи')
    # pc_name = Column(String(16), comment='NetBIOS Name PC')
    # discount = Column(SmallInteger, comment='Скидка')
    # payment_type = Column(SmallInteger, comment='Валюта оплаты')
    # bank_pay = Column(Text, comment='Банковский чек оплаты')
    # user_return = Column(Integer, comment='Id user return')
    # datetime_return = Column(DateTime, default=datetime.utcnow, comment='Дата и время возврата продажи')
    # bank_return = Column(Text, comment='Банковский чек возврата')

    def __str__(self):
        return f'{self.id} {self.price} {self.datetime} {self.id_client} {self.id_user} {self.datetime_save}' \
                f'{self.status} {self.pc_name} {self.discount} {self.payment_type} {self.bank_pay} {self.user_return}' \
                f'{self.datetime_return} {self.bank_return}'

    def __repr__(self):
        return str(self)
    # def __str__(self):
    #     return f'{self.id} {self.price} {self.datetime} {self.id_client} {self.id_user}'
    #
    # def __repr__(self):
    #     return str(self)

    # id_client = Column(Integer, ForeignKey('client.id'), comment='Id клиента')
    # id_user = Column(Integer, ForeignKey('user.id'), comment='Id пользователя')
    # price = Column(SmallInteger, comment='Цена')
    # datetime = Column(DateTime, default=datetime.utcnow, comment='Дата и время продажи')
    # client = relationship('Client', backref='sale_client', lazy='subquery')
    # user = relationship('User', backref='sale_user', lazy='subquery')
    # datetime_save = Column(DateTime, default=datetime.utcnow, comment='Дата и время сохранения продажи')
    # status = Column(SmallInteger, comment='Статус продажи')
    # pc_name = Column(String(16), comment='NetBIOS Name PC')
    # discount = Column(SmallInteger, comment='Скидка')
    # payment_type = Column(SmallInteger, comment='Валюта оплаты')
    # bank_pay = Column(Text, comment='Банковский чек оплаты')
    # user_return = Column(Integer, comment='Id user return')
    # datetime_return = Column(DateTime, default=datetime.utcnow, comment='Дата и время возврата продажи')
    # bank_return = Column(Text, comment='Банковский чек возврата')
    #
    #
    # def __str__(self):
    #     return f'{self.id} {self.price} {self.datetime} {self.id_client} {self.id_user} {self.datetime_save}' \
    #             f'{self.status} {self.pc_name} {self.discount} {self.payment_type} {self.bank_pay} {self.user_return}' \
    #             f'{self.datetime_return} {self.bank_return}'
    #
    # def __repr__(self):
    #     return str(self)
