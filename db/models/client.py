from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class Client(Base):
    __tablename__ = 'client'
    __tableargs__ = {
        'comment': 'Информация о клиентах'
    }

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False, comment='Фамилия')
    first_name: Mapped[str] = mapped_column(String(64), nullable=False, comment='Имя')
    middle_name: Mapped[str | None] = mapped_column(String(64), comment='Отчество')
    birth_date: Mapped[date] = mapped_column(Date, nullable=False, comment='Дата рождения')
    gender: Mapped[str | None] = mapped_column(String(3), comment='Отчество')
    phone: Mapped[str] = mapped_column(String(11), nullable=False, comment='Телефон')
    email: Mapped[str | None] = mapped_column(String(20), comment='Адрес электронной почты')
    privilege: Mapped[str | None] = mapped_column(String(2), comment='Наличие льгот')

    def __str__(self) -> str:
        return (f'{self.id} {self.first_name} {self.last_name} {self.middle_name} {self.birth_date} {self.gender}'
                f'{self.phone} {self.email} {self.privilege}')

    def __repr__(self) -> str:
        return str(self)
