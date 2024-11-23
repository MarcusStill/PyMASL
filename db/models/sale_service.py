from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class SaleService(Base):
    __tablename__ = "sale_service"
    __tableargs__ = {"comment": "Продажи_дополнительных_услуг"}

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)

    price: Mapped[int] = mapped_column(Integer, nullable=False, comment="Цена")
    datetime: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Дата и время продажи",
    )
    discount: Mapped[int | None] = mapped_column(SmallInteger, comment="Скидка")
    status: Mapped[int | None] = mapped_column(SmallInteger, comment="Статус продажи")
    pc_name: Mapped[str | None] = mapped_column(String(16), comment="NetBIOS Name PC")
    payment_type: Mapped[int | None] = mapped_column(
        SmallInteger, comment="Валюта оплаты"
    )
    bank_pay: Mapped[str | None] = mapped_column(Text, comment="Банковский чек оплаты")
    user_return: Mapped[int | None] = mapped_column(
        SmallInteger, comment="Id пользователя, оформившего возврат"
    )
    datetime_return: Mapped[DateTime] = mapped_column(
        DateTime, comment="Дата и время возврата продажи"
    )
    bank_return: Mapped[str | None] = mapped_column(
        Text, comment="Банковский чек возврата"
    )

    id_client: Mapped[int] = mapped_column(
        ForeignKey("client.id"), comment="Id клиента"
    )
    id_user: Mapped[int] = mapped_column(
        ForeignKey("user.id"), comment="Id пользователя"
    )
    client = relationship("Client", backref="sale_service_client")
    user = relationship("User", backref="sale_service_user")

    def __str__(self) -> str:
        return (
            f"{self.id} {self.id_client} {self.id_user} {self.price} {self.datetime} {self.discount} {self.status}"
            f"{self.pc_name} {self.payment_type} {self.bank_pay} {self.user_return} {self.datetime_return}"
            f"{self.bank_return}"
        )

    def __repr__(self) -> str:
        return str(self)
