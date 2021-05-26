from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
)

from models.base import Base


class User(Base):

    __tablename__ = 'user'
    __tableargs__ = {
        'comment': 'Информация о пользователях'
    }

    id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    last_name = Column(String(64), nullable=False, comment='Фамилия')
    first_name = Column(String(64), nullable=False, comment='Имя')
    middle_name = Column(String(64), comment='Отчество')
    login = Column(String(15), comment='Логин')
    password = Column(String(15), comment='Пароль')
    created_at = Column(Date, nullable=False, comment='Дата создания')


    def __repr__(self):
        return f'{self.id} {self.first_name} {self.last_name} {self.middle_name} {self.login} {self.password} {self.created_at}'
