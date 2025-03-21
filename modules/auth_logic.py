import datetime as dt
import logging

from modules.system import System

logger = logging.getLogger(__name__)

system = System()


def perform_pre_sale_checks(login: str, password: str) -> int:
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
    # Выполняем авторизацию через экземпляр system
    if system.user_authorization(login, password) != 1:
        return 0
    # Загружаем прайс-лист
    system.get_price()
    # Проверяем день (будний/выходной)
    day_today: int = system.check_day()
    system.what_a_day = day_today
    logger.info(
        f"Статус текущего дня: {'будний' if day_today == 0 else 'выходной'}. system.what_a_day = {system.what_a_day}"
    )
    # Устанавливаем номер дня недели и месяца
    today = dt.datetime.today()
    system.num_of_week = today.isoweekday()
    day_of_month = today.day
    logger.debug(
        f"Номер дня недели: {system.num_of_week}, номер дня месяца: {day_of_month}"
    )
    # Проверка дня многодетных (воскресенье и первая неделя месяца)
    if system.num_of_week == 7 and day_of_month <= 7:
        system.sunday = 1
        logger.info("Сегодня день многодетных")

    return 1
