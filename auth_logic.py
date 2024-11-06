import datetime as dt
import logging

from system import System

logger = logging.getLogger(__name__)


def perform_pre_sale_checks(self, login: str, password: str) -> int:
    """
    Функция запускает предпродажные проверки и устанавливает системные параметры.

    Параметры:
        self: object
            Ссылка на экземпляр текущего объекта класса, необходимая для доступа к атрибутам и методам GUI.
        login: str
            Логин пользователя.
        password: str
            Пароль пользователя.

    Возвращаемое значение:
        int: 1 - успешно, 0 - неудача.
    """
    logger.info("Запуск функции starting_the_main_form_logic")
    if System.user_authorization(self, login, password) != 1:
        logger.warning(f"Неудачная авторизация пользователя: {login}")
        return 0
    System.get_price(self)
    day_today: int = System.check_day(self)
    System.what_a_day = day_today
    logger.info(
        f"Статус текущего дня: {'будний' if day_today == 0 else 'выходной'}. System.what_a_day = {System.what_a_day}"
    )
    # Устанавливаем номер дня недели и месяца
    today = dt.datetime.today()
    System.num_of_week = today.isoweekday()
    day_of_month = today.day
    logger.debug(
        f"Номер дня недели: {System.num_of_week}, номер дня месяца: {day_of_month}"
    )
    # Проверка дня многодетных (воскресенье и первая неделя месяца)
    if System.num_of_week == 7 and day_of_month <= 7:
        System.sunday = 1
        logger.info("Сегодня день многодетных")
    return 1
