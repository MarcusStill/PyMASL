# PyMASL
## _Программа для учета посетителей и выполнения кассовых операций_

PyMASL это небольшая программа, позволяющая вести учет посетителей детского центра с кассовым модулем.

## Планируемый функционал

- Учет сведенией о клиентах: внесение, изменение, поиск
- Реализация правил посещения детского центра при оформлении заказов
- Учет продажи билетов:  формирование заказов, ведение статистики посещений, генерация и печать входных билетов 
- Проведение продажи: формирование кассового чека, генерация и печать входных билетов
- Выполнение базовых операций с ККМ: отчёт об открытии смены, кассовый чек коррекции, отчёт о закрытии смены, отчёт о текущем состоянии расчётов
- Работа с эквайрингом
- Формирование очетов о продажах и посещениях: отчет кассира и отчет администратора


> После реализации минимально необходимого функционала возможно расширение возможностей данной программы.


## Tech

PyMASL написан на Python и использует ряд проектов с открытым исходным кодом:
- [Alembic](https://alembic.sqlalchemy.org/) - is a lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python.
- [SQLAlchemy](https://www.sqlalchemy.org/) - the Python SQL Toolkit and Object Relational Mapper.
- [PySide6](https://pypi.org/project/PySide6/) - is the official Python module from the Qt for Python project, which provides access to the complete Qt 6.0+ framework.
- [PostgreSQL](https://www.postgresql.org/) - the World's Most Advanced Open Source Relational Database
- [And other] - список дополняется.

И, конечно же, PyMASL это open source проект, размещенный в [публичном репозитории](https://github.com/MarcusStill/PyMASL) на GitHub.

## Установка

> Примечание: `--раздел находится` в разработке.


## Разработка

> Примечание: `--раздел находится` в разработке.

## Docker

PyMASL для своей работы использует развернутую в Docker контейнере БД PostgreSQL. 
> Примечание: `--раздел находится` в разработке.
```sh
cd pymasl
docker build -t ...
```

This will create the PyMASL image and pull in the necessary dependencies.


```sh
docker run -d -p 8000:8080 --restart=always ...}
```

Verify the deployment by navigating to your server address in
your preferred browser.

```sh
127.0.0.1:8000
```

## Лицензия


**Free Software, Hell Yeah!**

