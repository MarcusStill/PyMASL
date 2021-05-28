from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from models.base import Base

class Service(Base):

    __tablename__ = 'service'
    __tableargs__ = {
        'comment': 'Услуги'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    id_price_service = Column(Integer, ForeignKey('price_service.id'),comment='Id услуги в прайс-листе')
    id_client = Column(Integer, ForeignKey('client.id'), comment='Id клиента')
    id_sale = Column(Integer, ForeignKey('sale.id'),comment='Id продажи')
    price_service = relationship('price_service', backref='service_price_service', lazy='subquery')
    client = relationship('client', backref='service_client', lazy='subquery')
    sale = relationship('sale', backref='service_sale', lazy='subquery')


    def __repr__(self):
        return f'{self.id} {self.id_price_service} {self.id_client} {self.id_sale}'
