import base64
import calendar
import datetime as dt
import json
import os
import socket
from datetime import date

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db.models import Holiday, Workday, Price, User
from modules.config import Config
from modules.logger import logger, logger_wraps


class System:
    """Класс для хранения системной информации и функций"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(System, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Загружаем конфигурацию с использованием класса Config
        self.config = Config()

        # Инициализация переменных на основе конфигурации
        self.host = self.config.get("host")
        self.port = self.config.get("port")
        self.database = self.config.get("database")
        self.user = self.config.get("user")
        self.software_version = self.config.get("version")
        self.log_file = self.config.get("log_file")
        # Информация о РМ
        self.kol_pc = int(self.config.get("kol"))
        self.pcs = self.config.pcs  # список рабочих станций
        self.ticket_print = self.config.get("ticket")
        self.kkt_available = self.config.get("available")

        load_dotenv()  # Загружаем переменные окружения из .env файла
        pswrd = os.getenv("DB_PASSWORD")
        if not pswrd:
            logger.error("Переменная окружения DB_PASSWORD не установлена!")
            raise ValueError("Переменная окружения DB_PASSWORD не установлена!")

        self.engine = create_engine(
            f"postgresql+psycopg2://{self.user}:{pswrd}@{self.host}:{self.port}/{self.database}"
        )

        # Инициализация данных
        self.user = None  # Данные авторизованного пользователя
        self.client_id = None  # Флаг для обновления клиента
        self.client_update = None
        self.last_name = ""  # Сохраняем фамилию нового клиента
        # Статус продажи: 0 - создана, 1 - оплачена, 2 - возвращена,
        # 3 - требуется повторный возврат по банковскому терминалу,
        # 4 - повторный возврат по банковскому терминалу,
        # 5 - требуется частичный возврат, 6 - частичный возврат
        # 7 - возврат по банковским реквизитам
        # 8 - отменена
        self.sale_status = None
        self.sale_id = None
        self.sale_discount = None
        self.sale_tickets = ()
        self.sale_tuple = ()
        self.sale_special = None
        # Номер строки с активным CheckBox для исключения взрослого из продажи
        self.sale_checkbox_row = None
        # Состояние CheckBox для искл. взрослого из продажи: 0 - есть, 1 - нет
        self.exclude_from_sale = 0
        self.what_a_day = None
        # Первое воскресенье месяца (день многодлетных): 0 - нет, 1 - да
        self.sunday = None
        self.today = date.today()
        self.num_of_week = 0  # Номер дня недели
        self.pc_name = socket.gethostname()
        # Прайс-лист основных услуг
        self.price = {
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
        self.price_service = {}
        # Количество начисляемых талантов
        self.talent = {"1_hour": 25, "2_hour": 35, "3_hour": 50}
        self.age = {"min": 5, "max": 15}  # Возраст посетителей
        # Содержание detail: [kol_adult, price_adult, kol_child, price_child, discount, id_adult, time, sum]
        self.sale_dict = {
            "kol_adult": 0,
            "price_adult": 0,
            "kol_child": 0,
            "price_child": 0,
            "detail": [0, 0, 0, 0, 0, 0, 0, 0],
        }
        self.id_new_client_in_sale = 0  # Храним id нового клиента
        self.print_check = 1  # Флаг печати кассовых и банковских чеков
        # Сохраняем сумму для внесения или выплаты из кассы
        self.amount_to_pay_or_deposit = 0
        # Сохраняем баланс наличных денег в кассе
        self.amount_of_money_at_the_cash_desk = None
        # Словарь count_number_of_visitors -> Используем для подсчета количества посетителей: 'kol_adult', 'kol_child'
        # Используем для подсчета количества посетителей со скидкой: 'kol_sale_adult', 'kol_sale_child'
        # Используем для подсчета количества посетителей с категорией: 'kol_adult_many_child', 'kol_child_many_child',
        # 'kol_adult_invalid', 'kol_child_invalid' = 0
        # Запоминаем id для "привязки" продажи ко взрослому: 'id_adult'
        # Флаг "многодетные" (1 - два часа бесплатно, 2 - скидка 50%): 'many_child'
        # Считаем количество золотых талантов: 'talent'
        self.count_number_of_visitors = {
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
        # Накапливаем статистику по проданным билетам
        self.ticket_price_summary = {}

    @staticmethod
    def decode_password(encoded_password: str) -> str:
        """Декодирует пароль из Base64."""
        return base64.b64decode(encoded_password.encode()).decode()

    def user_authorization(self, login: str, password: str) -> int:
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
            with Session(self.engine) as session:
                query = select(User).where(User.login == login)
                kassir = session.execute(query).scalars().first()
            stored_password = System.decode_password(kassir.password)
            if stored_password == password:
                self.user = kassir
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

        # Словарь с дефолтными значениями
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

        # Инициализируем db_prices пустым словарем по умолчанию
        db_prices = {}

        with Session(self.engine) as session:
            result = session.query(Price).order_by(Price.id).all()

        if result:
            if len(result) >= 9:
                # Заполняем db_prices в случае наличия достаточного количества записей
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
            else:
                # Если записей меньше 9, используем дефолтные значения для отсутствующих элементов
                logger.warning(
                    f"Недостаточно записей в прайс-листе: {len(result)} вместо 9."
                )
                missing_keys = list(default_prices.keys())[len(result) :]
                for idx, key in enumerate(list(default_prices.keys())[: len(result)]):
                    db_prices[key] = result[idx]

                # Заполняем оставшиеся элементы дефолтными значениями
                for key in missing_keys:
                    db_prices[key] = default_prices[key]
        else:
            # Если записей нет, используем дефолтные значения для всех элементов
            logger.warning(f"Используем дефолтные значения для прайс-листа")
            db_prices = default_prices

        # Устанавливаем цены, используя данные из db_prices или дефолтные значения
        for key, value in db_prices.items():
            if isinstance(value, Price):
                price_value = value.price ^ 42
            else:
                # Если value — это просто число, берем его как цену
                price_value = value

            price_value = (
                price_value if price_value is not None else 0
            )  # Если вдруг None, ставим 0
            # Устанавливаем цену в словарь
            self.price[key] = (
                int(price_value) if price_value != 0 else default_prices[key]
            )

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
        day = dt.datetime.now().strftime("%Y-%m-%d")
        # Проверяем есть ли текущая дата в списке дополнительных рабочих дней
        with Session(self.engine) as session:
            query = select(Workday).where(Workday.date == day)
            check_day = session.execute(query).scalars().first()
        if check_day:
            status_day = 0
            logger.info("Сегодня дополнительный рабочий день")
        else:
            # Преобразуем текущую дату в список
            day: list[str] = day.split("-")
            number_day = calendar.weekday(int(day[0]), int(day[1]), int(day[2]))
            if number_day >= 5:
                status_day = 1
                self.what_a_day = 1
                logger.info("Сегодня выходной день")
            else:
                day: str = "-".join(day)
                # Проверяем есть ли текущая дата в списке дополнительных праздничных дней
                with Session(self.engine) as session:
                    query = select(Holiday).where(Holiday.date == day)
                    check_day: Holiday | None = session.execute(query).scalars().first()
                if check_day:
                    status_day = 1
                    self.what_a_day = 1
                    logger.info("Сегодня дополнительный выходной")
                else:
                    status_day = 0
                    logger.info("Сегодня обычный день")
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
        today = date.today()
        return (
            today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        )

    @staticmethod
    def calculate_ticket_type(self, age: int) -> str:
        """
        Функция определяет тип входного билета.

        Параметры:
            age (int): Возраст посетителя.

        Возвращаемое значение:
            str: Тип билета (бесплатный, детский, взрослый).
        """
        if age < self.age["min"]:
            return "бесплатный"
        elif self.age["min"] <= age < self.age["max"]:
            return "детский"
        elif age >= self.age["max"]:
            return "взрослый"
        return ""

    @logger_wraps(entry=True, exit=True, level="DEBUG", catch_exceptions=True)
    def load_coordinates(self, config: Config):
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
        coordinates_file = config.get("ticket_coordinates_file")
        # Проверка, что путь к файлу есть
        if not coordinates_file:
            raise KeyError("Не указан путь к файлу координат в конфигурации.")

        # Проверка, что путь к файлу является строкой
        if not isinstance(coordinates_file, str):
            raise TypeError("Путь к файлу координат должен быть строкой.")

        # Проверка, что файл существует
        if not os.path.isfile(coordinates_file):
            raise FileNotFoundError(
                f"Файл с координатами '{coordinates_file}' не найден."
            )
        # Загрузка данных из файла с координатами
        try:
            with open(coordinates_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "coordinates" not in data:
                    raise KeyError("В конфигурации отсутствует ключ 'coordinates'.")
                return data["coordinates"]
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при разборе JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Неизвестная ошибка при загрузке конфигурации: {e}")
            raise
