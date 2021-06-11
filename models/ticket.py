from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    SmallInteger,
    DateTime,
    String,
)
from sqlalchemy.orm import relationship
from models.base import Base

class Ticket(Base):

    __tablename__ = 'ticket'
    __tableargs__ = {
        'comment': 'Билеты'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    id_client = Column(Integer, ForeignKey('client.id'), comment='Id клиента')
    id_sale = Column(Integer, ForeignKey('sale.id'), comment='Id продажи')
    client_age = Column(SmallInteger, comment='Возраст клиента')
    datetime = Column(DateTime, default=datetime.utcnow, comment='Дата и время')
    arrival_time = Column(SmallInteger, comment='Время пребывания')
    talent = Column(SmallInteger, comment='Количество золотых талантов')
    price = Column(SmallInteger, comment='Цена') #int!
    description = Column(String(64), comment='Примечание')
    #id_type_ticket = Column(Integer, ForeignKey('type_ticket.id'), comment='Id типа билета')
    client = relationship('Client', backref='ticket_client', lazy='subquery')
    sale = relationship('Sale', backref='ticket_sale', lazy='subquery')
    #type_ticket = relationship('type_ticket', backref='ticket_type_ticket', lazy='subquery')


    def __str__(self):
        return f'{self.id} {self.client_age} {self.datetime} {self.arrival_time} {self.talent} {self.price} {self.description} {self.id_client} {self.id_sale}'

    def __repr__(self):
        return str(self)