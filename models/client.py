from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
)

from models.base import Base


class Client(Base):

    __tablename__ = 'client'
    __tableargs__ = {
        'comment': 'Информация о клиентах'
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
    birth_date = Column(Date, nullable=False, comment='Дата рождения')
    gender = Column(String(3), comment='Отчество')
    phone = Column(String(11), nullable=False, comment='Телефон')
    email = Column(String(20), comment='Адрес электронной почты')
    privilege = Column(String(1), comment='Наличие льгот')


    def __str__(self):
        return f'{self.id} {self.first_name} {self.last_name} {self.middle_name} {self.birth_date}' \
               f' {self.gender} {self.phone} {self.email} {self.privilege}'


    def __repr__(self):
        return str(self)
