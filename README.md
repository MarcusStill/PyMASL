# PyMASL
## _Программа для учета посетителей и выполнения кассовых операций_

PyMASL это небольшая программа, позволяющая вести учет посетителей детского центра и производить реализацию услуг с использованием торгового оборудования.

## Реализованный функционал

- учет сведений о клиентах: внесение, изменение, поиск;
- соблюдение правил посещения детского центра при оформлении заказов;
- Учет продаж билетов: формирование заказов, сохранение заказов для оплаты в будущем периоде, “привязка” продажи к сопровождающему, механизм применения скидки с шагом 5%;
- ведение статистики продаж и посещений;
- выполнение операций с торговым оборудованием: ведение денежных операций при помощи ККМ АТОЛ, работа с эквайринговым терминалом Сбербанка, генерация и печать входных билетов;

> Планируется расширение возможностей программы.


## Используемые технологии

PyMASL написан на Python и использует ряд проектов с открытым исходным кодом:
- [Docker](https://www.docker.com/) - is a set of platform as a service (PaaS) products that use OS-level virtualization to deliver software in packages called containers.
- [Docker Compose](https://docs.docker.com/compose/) - is a tool for defining and running multi-container Docker applications.  
- [SQLAlchemy](https://www.sqlalchemy.org/) - the Python SQL Toolkit and Object Relational Mapper.
- [PostgreSQL](https://www.postgresql.org/) - the World's Most Advanced Open Source Relational Database
- [Alembic](https://alembic.sqlalchemy.org/) - is a lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python.
- [PySide6](https://pypi.org/project/PySide6/) - is the official Python module from the Qt for Python project, which provides access to the complete Qt 6.0+ framework.
- [ReportLab](https://www.reportlab.com/) - The ReportLab Toolkit. An Open Source Python library for generating PDFs and graphics.
- [Auto PY to EXE](https://pypi.org/project/auto-py-to-exe/) - A .py to .exe converter using a simple graphical interface and PyInstaller in Python.
- [SumatraPDF](https://www.sumatrapdfreader.org/) - Sumatra PDF is a free PDF, eBook (ePub, Mobi), XPS, DjVu, CHM, Comic Book (CBZ and CBR) viewer for Windows.
- [And other] - список дополняется.

И, конечно же, PyMASL это open source проект, размещенный в [публичном репозитории](https://github.com/MarcusStill/PyMASL) на GitHub.


## Установка
Зависимости указаны в requirements.txt. Для работы в ОС Windows проект конвертируется в exe при помощи [Auto PY to EXE](https://pypi.org/project/auto-py-to-exe/) - GUI к PyInstaller.

Процесс преобразования..

В дополнительные файлы нужно добавить содержимое каталога Files/platforms. состав Для корректног озапуска требуются следующие dll

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