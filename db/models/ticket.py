from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class Ticket(Base):

    __tablename__ = 'ticket'
    __tableargs__ = {
        'comment': 'Билеты'
    }

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    id_client: Mapped[int] = mapped_column(ForeignKey("client.id"), comment='Id клиента')
    id_sale: Mapped[int] = mapped_column(ForeignKey("sale.id"), comment='Id продажи')
    client_age: Mapped[int | None] = mapped_column(SmallInteger, comment='Возраст клиента')
    datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow,
                                               comment='Дата и время')
    arrival_time: Mapped[int | None] = mapped_column(SmallInteger, comment='Время пребывания')
    talent: Mapped[int | None] = mapped_column(SmallInteger, comment='Количество золотых талантов')
    price: Mapped[int] = mapped_column(Integer, nullable=False, comment='Цена')
    description: Mapped[str | None] = mapped_column(String(64), comment='Примечание')
    ticket_type: Mapped[int | None] = mapped_column(SmallInteger,
                                                    comment='Тип билета: 0-взрослый, 1 - детский, 2 - бесплатный')
    print: Mapped[int | None] = mapped_column(SmallInteger, comment='Печатать билет: 0-нет, 1 - да')

    client = relationship('Client', backref='ticket_client')
    sale = relationship('Sale', backref='ticket_sale')

    def __str__(self) -> str:
        return (f'{self.id} {self.client_age} {self.datetime} {self.arrival_time} {self.talent} {self.price} '
                f'{self.description} {self.id_client} {self.id_sale} {self.ticket_type} {self.price}')

    def __repr__(self) -> str:
        return str(self)
