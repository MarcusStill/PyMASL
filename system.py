import calendar
import datetime as dt
import json
import os
import socket
from configparser import (
    ConfigParser,
    NoSectionError,
    NoOptionError,
    MissingSectionHeaderError,
)
from datetime import date

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db.models import Holiday
from db.models import Workday
from db.models.price import Price
from db.models.user import User
from files.logger import logger, logger_wraps


@logger_wraps(entry=True, exit=True, level="DEBUG", catch_exceptions=True)
def read_config():
    """Функция для загрузки параметров из файла конфигурации.

    Параметры:
        None

    Возвращаемое значение:
        dict: Словарь с параметрами конфигурации, содержащий следующие ключи:
            - host (str): Хост базы данных.
            - port (str): Порт базы данных.
            - database (str): Имя базы данных.
            - user (str): Имя пользователя базы данных.
            - version (str): Версия программного обеспечения.
            - log_file (str): Путь к файлу журнала.
            - kol (str): Количество ПК.
            - pc_1 (str): Имя первого ПК.
            - pc_2 (str): Имя второго ПК.
            - pinpad_path (str): Путь к терминалу.
    """
    logger.info("Запуск функции read_config")
    config = ConfigParser()
    try:
        if not os.path.exists("config.ini"):
            logger.error("Файл конфигурации не найден: config.ini")
            raise FileNotFoundError("Файл конфигурации не найден.")
        config.read("config.ini")
        # Параметры для загрузки
        required_keys = {
            "host": "DATABASE",
            "port": "DATABASE",
            "database": "DATABASE",
            "user": "DATABASE",
            "version": "OTHER",
            "log_file": "OTHER",
            "kol": "PC",
            "pc_1": "PC",
            "pc_2": "PC",
            "pinpad_path": "TERMINAL",
        }
        # Загружаем параметры и проверяем наличие
        config_data = {}
        for key, section in required_keys.items():
            if not config.has_section(section):
                logger.error(f"Отсутствует секция: '{section}'")
                raise ValueError(f"Отсутствует секция: '{section}'")
            if not config.has_option(section, key):
                logger.error(f"Отсутствует параметр '{key}' в секции '{section}'")
                raise ValueError(f"Отсутствует параметр '{key}' в секции '{section}'")
            config_data[key] = config.get(section, key)
        return config_data
    except (NoSectionError, NoOptionError) as e:
        raise ValueError(f"Ошибка в файле конфигурации: {e}")
    except MissingSectionHeaderError:
        raise ValueError("Ошибка: отсутствует заголовок секции в файле конфигурации.")
    except Exception as e:
        raise RuntimeError(f"Неизвестная ошибка при чтении файла конфигурации: {e}")

# Чтение параметров из файла конфигурации
config_data = read_config()

# Загрузка переменных окружения из файла .env
load_dotenv()

# Проверка переменной окружения
pswrd: str | None = os.getenv("DB_PASSWORD")
if not pswrd:
    logger.error("Переменная окружения DB_PASSWORD не установлена!")
    raise ValueError("Переменная окружения DB_PASSWORD не установлена!")

class System:
    """Класс для хранения системной информации и функций"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(System, cls).__new__(cls, *args, **kwargs)
        return cls._instance


    host = config_data["host"]
    port = config_data["port"]
    database = config_data["database"]
    user = config_data["user"]
    software_version = config_data["version"]
    log_file = config_data["log_file"]
    kol_pc = config_data["kol"]
    pc_1 = config_data["pc_1"]
    pc_2 = config_data["pc_2"]
    engine = create_engine(f"postgresql+psycopg2://{user}:{pswrd}@{host}:{port}/{database}")
    # Данные успешно авторизованного пользователя
    user: User | None = None
    # Флаг для обновления клиента
    client_id: int | None = None
    client_update: int | None = None
    # Сохраняем фамилию нового клиента
    last_name: str = ""
    # Статус продажи: 0 - создана, 1 - оплачена, 2 - возвращена,
    # 3 - требуется повторный возврат по банковскому терминалу,
    # 4 - повторный возврат по банковскому терминалу,
    # 5 - требуется частичный возврат, 6 - частичный возврат
    # 7 - возврат по банковским реквизитам
    # 8 - отменена
    sale_status: int | None = None
    sale_id: int | None = None
    sale_discount: int | None = None
    sale_tickets = ()
    sale_tuple: tuple = ()
    sale_special: int | None = None
    # Номер строки с активным CheckBox для исключения взрослого из продажи
    sale_checkbox_row: int | None = None
    # Состояние CheckBox для искл. взрослого из продажи: 0 - есть, 1 - нет
    exclude_from_sale: int = 0
    # Какой сегодня день: 0 - будний, 1 - выходной
    what_a_day: int | None = None
    # Первое воскресенье месяца (день многодлетных): 0 - нет, 1 - да
    sunday: int | None = None
    today: date = date.today()
    # Номер дня недели
    num_of_week: int = 0
    pc_name: str = socket.gethostname()
    # Прайс-лист основных услуг
    price: dict = {
        "ticket_child_1": 0,
        "ticket_child_2": 0,
        "ticket_child_3": 0,
        "ticket_child_week_1": 0,
        "ticket_child_week_2": 0,
        "ticket_child_week_3": 0,
        "ticket_adult_1": 0,
        "ticket_adult_2": 0,
        "ticket_adult_3": 0,
        "ticket_free": 0,
    }
    price_service: dict = {}
    # Количество начисляемых талантов
    talent: dict = {"1_hour": 25, "2_hour": 35, "3_hour": 50}
    # Возраст посетителей
    age: dict = {"min": 5, "max": 15}
    # Информация о РМ
    kol_pc: int = 0
    pc_1: str = ""
    pc_2: str = ""
    sale_dict: dict = {
        "kol_adult": 0,
        "price_adult": 0,
        "kol_child": 0,
        "price_child": 0,
        "detail": [0, 0, 0, 0, 0, 0, 0, 0],
    }
    # Содержание detail: [kol_adult, price_adult, kol_child, price_child, discount, id_adult, time, sum]

    # Храним id нового клиента
    id_new_client_in_sale: int = 0
    # Флаг печати кассовых и банковских чеков
    print_check: int = 1
    # Сохраняем сумму для внесения или выплаты из кассы
    amount_to_pay_or_deposit: int = 0
    # Сохраняем баланс наличных денег в кассе
    amount_of_money_at_the_cash_desk: int = None
    # Словарь count_number_of_visitors -> Используем для подсчета количества посетителей: 'kol_adult', 'kol_child'
    # Используем для подсчета количества посетителей со скидкой: 'kol_sale_adult', 'kol_sale_child'
    # Используем для подсчета количества посетителей с категорией: 'kol_adult_many_child', 'kol_child_many_child',
    # 'kol_adult_invalid', 'kol_child_invalid' = 0
    # Запоминаем id для "привязки" продажи ко взрослому: 'id_adult'
    # Флаг "многодетные" (1 - два часа бесплатно, 2 - скидка 50%): 'many_child'
    # Считаем количество золотых талантов: 'talent'
    count_number_of_visitors: dict = {
        "kol_adult": 0,
        "kol_child": 0,
        "kol_sale_adult": 0,
        "kol_sale_child": 0,
        "kol_adult_many_child": 0,
        "kol_child_many_child": 0,
        "kol_adult_invalid": 0,
        "kol_child_invalid": 0,
        "id_adult": 0,
        "many_child": 0,
        "invalid": 0,
        "talent": 0,
    }

    def user_authorization(self, login, password) -> int:
        """
        Функция проверяет есть ли пользователь в БД с данными, указанными на форме авторизации.

        Параметры:
            login (str): Логин пользователя.
            password (str): Пароль пользователя.

        Возвращаемое значение:
            int: 1 - успешная авторизация, 0 - неуспешная.
        """
        logger.info("Запуск функции user_authorization")
        try:
            with Session(System.engine) as session:
                query = select(User).where(
                    User.login == login, User.password == password
                )
                kassir = session.execute(query).scalars().first()
            if kassir:
                System.user = kassir
                logger.info(f"Успешная авторизация: {kassir.last_name}")
                return 1
            else:
                logger.warning(
                    f"Неудачная попытка авторизации для пользователя {login}"
                )
                return 0
        except SQLAlchemyError as e:
            logger.error(f"Ошибка базы данных при авторизации пользователя: {e}")
            return 0
        except Exception as e:
            logger.error(f"Неизвестная ошибка при авторизации: {e}")
            return 0

    @logger_wraps(entry=True, exit=True, level="DEBUG", catch_exceptions=True)
    def get_price(self) -> None:
        """
        Функция загружает прайс-лист основных услуг из БД.

        Параметры:
        self: object
            Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            None: Функция не возвращает значений, вставляет фамилию в поле формы.
        """
        logger.info("Запуск функции get_price")

        # Словарь со значениями по умолчанию
        default_prices = {
            "ticket_child_1": 250,
            "ticket_child_2": 500,
            "ticket_child_3": 750,
            "ticket_child_week_1": 300,
            "ticket_child_week_2": 600,
            "ticket_child_week_3": 900,
            "ticket_adult_1": 150,
            "ticket_adult_2": 200,
            "ticket_adult_3": 250,
        }

        with Session(System.engine) as session:
            result = session.query(Price).order_by(Price.id).all()

        if result:
            logger.debug(f"result: {result}")
            # Словарь для хранения цен из БД
            db_prices = {
                "ticket_child_1": result[0],
                "ticket_child_2": result[1],
                "ticket_child_3": result[2],
                "ticket_child_week_1": result[3],
                "ticket_child_week_2": result[4],
                "ticket_child_week_3": result[5],
                "ticket_adult_1": result[6],
                "ticket_adult_2": result[7],
                "ticket_adult_3": result[8],
            }

            # Устанавливаем цены, используя значения из БД или по умолчанию
            for key, value in db_prices.items():
                System.price[key] = (
                    int(str(value)) if int(str(value)) != 0 else default_prices[key]
                )
        else:
            # Если результат запроса пуст, устанавливаем значения по умолчанию
            logger.info(f"Устанавливаем значения прайс-листа по умолчанию.")
            System.price.update(default_prices)
        logger.debug(f"System.price: {System.price}")

    def check_day(self) -> int:
        """
        Функция проверяет статус текущего дня.

        Параметры:
        self: object
            Ссылка на экземпляр текущего объекта класса, необходимая для доступа к элементам GUI.

        Возвращаемое значение:
            int: 1 - выходной день, 0 - будний день.
        """
        logger.info("Запуск функции check_day")
        day: list[str] = dt.datetime.now().strftime("%Y-%m-%d")
        # Проверяем есть ли текущая дата в списке дополнительных рабочих дней
        with Session(System.engine) as session:
            query = select(Workday).where(Workday.date == day)
            check_day: Workday | None = session.execute(query).scalars().first()
        if check_day:
            logger.info("Сегодня дополнительный рабочий день")
            status_day: int = 0
        else:
            # Преобразуем текущую дату в список
            day: list[str] = day.split("-")
            # Вычисляем день недели
            number_day: int = calendar.weekday(int(day[0]), int(day[1]), int(day[2]))
            # Проверяем день недели равен 5 или 6
            if number_day >= 5:
                status_day: int = 1
                System.what_a_day = 1
                logger.info("Сегодня выходной день")
            else:
                day: str = "-".join(day)
                # Проверяем есть ли текущая дата в списке дополнительных праздничных дней
                with Session(System.engine) as session:
                    query = select(Holiday).where(Holiday.date == day)
                    check_day: Holiday | None = session.execute(query).scalars().first()
                if check_day:
                    status_day: int = 1
                    System.what_a_day = 1
                    logger.info("Сегодня дополнительный выходной")
                else:
                    status_day: int = 0
        return status_day

    @staticmethod
    def calculate_age(born: date) -> int:
        """
        Функция вычисляет возраст посетителя.

        Параметры:
            born (date): Дата рождения.

        Возвращаемое значение:
            int: Возраст.
        """
        today: date = date.today()
        return (
            today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        )

    @staticmethod
    def calculate_ticket_type(age: int) -> str:
        """
        Функция определяет тип входного билета.

        Параметры:
            age (int): Возраст посетителя.

        Возвращаемое значение:
            str: Тип билета (бесплатный, детский, взрослый).
        """
        result: str = ""
        if age < System.age["min"]:
            result = "бесплатный"
        elif System.age["min"] <= age < System.age["max"]:
            result = "детский"
        elif age >= System.age["max"]:
            result = "взрослый"
        return result

    @logger_wraps(entry=True, exit=True, level="DEBUG", catch_exceptions=True)
    def load_coordinates(config_file):
        """Функция для проверки загрузки файла с координатами, необходимыми для генерации билетов.

        Параметры:
            config_file (str): Путь к файлу конфигурации, содержащему координаты.

        Возвращаемое значение:
            dict: Словарь с координатами, содержащий следующие ключи:
                - name (dict): Координаты имени с ключами 'x' и 'y'.
                - surname (dict): Координаты фамилии с ключами 'x' и 'y'.
                - age (dict): Координаты возраста с ключами 'x' и 'y'.
                - duration (dict): Координаты продолжительности с ключами 'x' и 'y'.
                - date (dict): Координаты даты с ключами 'x' и 'y'.
                - guest (dict): Координаты статуса "гость" с ключами 'x' и 'y'.
                - city (dict): Координаты города с ключами 'x' и 'y'.
                - place (dict): Координаты места с ключами 'x' и 'y'.
                - price (dict): Координаты цены с ключами 'x' и 'y'.
                - ticket_type (dict): Координаты типа билета с ключами 'x' и 'y'.
                - notes (dict): Координаты дополнительных отметок с ключами 'x' и 'y'.
                - talents (dict): Координаты талантов с ключами 'x' и 'y'.
                - qr_code (dict): Координаты QR-кода с ключами 'x' и 'y'.
        """
        logger.info("Запуск функции load_coordinates")
        if not os.path.isfile(config_file):
            raise FileNotFoundError(f"Файл конфигурации '{config_file}' не найден.")
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Проверка, что ключ 'coordinates' существует в загруженных данных
            if "coordinates" not in data:
                raise KeyError("В конфигурации отсутствует ключ 'coordinates'.")
            return data["coordinates"]
        except json.JSONDecodeError:
            raise ValueError(
                "Ошибка в формате файла конфигурации. Убедитесь, что файл является корректным JSON."
            )
        except Exception as e:
            raise RuntimeError(f"Ошибка при загрузке конфигурации: {e}")

    # Проверка загрузки файла с координатами
    try:
        coordinates = load_coordinates("files/ticket_param.json")
    except (FileNotFoundError, KeyError, ValueError, RuntimeError) as e:
        logger.error(str(e))
        raise FileNotFoundError(f"Файл конфигурации '{coordinates}' не найден.")
