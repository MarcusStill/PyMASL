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
from db.models.base import Base

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
    arrival_time = Column(Integer, comment='Время пребывания')
    talent = Column(Integer, comment='Количество золотых талантов')
    price = Column(Integer, comment='Цена')
    description = Column(String(64), comment='Примечание')
    ticket_type = Column(SmallInteger, comment='Тип билета: 0-взрослый, 1 - детский, 2 - бесплатный')
    print = Column(SmallInteger, comment='Печатать билет: 0-нет, 1 - да')
    client = relationship('Client', backref='ticket_client', lazy='subquery')
    sale = relationship('Sale', backref='ticket_sale', lazy='subquery')


    def __str__(self):
        return f'{self.id} {self.client_age} {self.datetime} {self.arrival_time} {self.talent} {self.price}' \
               f'{self.description} {self.id_client} {self.id_sale} {self.ticket_type} {self.price}'

    def __repr__(self):
        return str(self)
