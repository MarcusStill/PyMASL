from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class SaleService(Base):
    __tablename__ = 'sale_service'
    __tableargs__ = {
        'comment': 'Продажи_дополнительных_услуг'
    }

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)

    price: Mapped[int] = mapped_column(Integer, nullable=False, comment='Цена')
    datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow,
                                               comment='Дата и время продажи')
    discount: Mapped[int | None] = mapped_column(SmallInteger, comment='Скидка')
    status: Mapped[int | None] = mapped_column(SmallInteger, comment='Статус продажи')
    pc_name: Mapped[str | None] = mapped_column(String(16), comment='NetBIOS Name PC')
    payment_type: Mapped[int | None] = mapped_column(SmallInteger, comment='Валюта оплаты')
    bank_pay: Mapped[str | None] = mapped_column(Text, comment='Банковский чек оплаты')
    user_return: Mapped[int | None] = mapped_column(SmallInteger, comment='Id пользователя, оформившего возврат')
    datetime_return: Mapped[DateTime] = mapped_column(DateTime, comment='Дата и время возврата продажи')
    bank_return: Mapped[str | None] = mapped_column(Text, comment='Банковский чек возврата')

    id_client: Mapped[int] = mapped_column(ForeignKey("client.id"), comment='Id клиента')
    id_user: Mapped[int] = mapped_column(ForeignKey("user.id"), comment='Id пользователя')
    client = relationship('Client', backref='sale_service_client')
    user = relationship('User', backref='sale_service_user')

    def __str__(self) -> str:
        return f'id={self.id}, id_client={self.id_client}, id_user={self.id_user}, price={self.price}, ' \
               f'datetime={self.datetime}, discount={self.discount}, status={self.status}, pc_name={self.pc_name}, ' \
               f'payment_type={self.payment_type}, bank_pay={self.bank_pay}, user_return={self.user_return},' \
               f'datetime_return={self.datetime_return}, bank_return={self.bank_return}'

    def __repr__(self) -> str:
        return str(self)
