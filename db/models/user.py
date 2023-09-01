from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class User(Base):
    __tablename__ = 'user'
    __tableargs__ = {
        'comment': 'Информация о пользователях'
    }

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, unique=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False, comment='Фамилия')
    first_name: Mapped[str] = mapped_column(String(64), nullable=False, comment='Имя')
    middle_name: Mapped[str | None] = mapped_column(String(64), comment='Отчество')
    login: Mapped[str] = mapped_column(String(15), nullable=False, comment='Логин')
    password: Mapped[str] = mapped_column(String(15), nullable=False, comment='Пароль')
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow, comment='Дата создания')
    inn: Mapped[str | None] = mapped_column(String(12), comment='ИНН')

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name} {self.middle_name} {self.login}'

    def __repr__(self) -> str:
        return str(self)
