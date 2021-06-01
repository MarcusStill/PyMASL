from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    SmallInteger,
    DateTime,
)
from sqlalchemy.orm import relationship
from models.base import Base


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
    #id_currency_type = Column(Integer, ForeignKey('currency_type.id'), comment='Id типа валюты')
    #id_status_sale = Column(Integer, ForeignKey('status_sale.id'), comment='Id статуса продажи')
    #id_discount = Column(Integer, ForeignKey('discount.id'), comment='Id скидки')
    price = Column(SmallInteger, comment='Цена')
    datetime = Column(DateTime, nullable=False, comment='Дата и время продажи')
    #pc_name = Column(Integer, ForeignKey('user_pc.id'), comment='Id РМ кассира')
    client = relationship('Client', backref='sale_client', lazy='subquery')
    #currency_type = relationship('currency_type', backref='sale_currency_type', lazy='subquery')
    #status_sale = relationship('status_sale', backref='sale_status_sale', lazy='subquery')
    #discount = relationship('discount', backref='sale_discount', lazy='subquery')
    #pc_name = relationship('pc_name', backref='sale_user_pc', lazy='subquery')
    user = relationship('User', backref='sale_user', lazy='subquery')


    def __str__(self):
        return f'{self.id} {self.price} {self.datetime} {self.id_client}{self.id_user}'

    def __repr__(self):
        return str(self)