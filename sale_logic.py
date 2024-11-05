import logging
from datetime import date

logger = logging.getLogger(__name__)

# Возраст посетителей
age_client: dict = {"min": 5, "max": 15}


def calculate_age(birth_date: date) -> int:
    """
    Функция вычисляет возраст посетителя.

    Параметры:
        born (date): Дата рождения.

    Возвращаемое значение:
        int: Возраст.
    """
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def calculate_ticket_type(age: int) -> str:
    """
    Функция определяет тип входного билета.

    Параметры:
        age (int): Возраст посетителя.

    Возвращаемое значение:
        str: Тип билета (бесплатный, детский, взрослый).
    """
    result: str = ""
    if age < age_client["min"]:
        result = "бесплатный"
    elif age_client["min"] <= age < age_client["max"]:
        result = "детский"
    elif age >= age_client["max"]:
        result = "взрослый"
    return result


def calculate_discounted_price(row: int, price: int, type_ticket: str, count_visitors: dict,
                               sale_discount: int) -> dict:
    """
    Рассчитывает скидку для билета посетителя.

    Параметры:
        row (int): Номер строки.
        price (int): Цена до применения скидок.
        type_ticket (str): Тип билета (взрослый, детский).
        count_visitors (dict): Счетчик посетителей для категорий.
        sale_discount (int): Процент скидки.

    Возвращаемое значение:
        dict: Словарь с обновленной ценой и статусом особенной продажи.
    """
    new_price = price
    sale_special = 0

    logger.info("Применяем скидку")

    # Применяем скидку в зависимости от категории
    if count_visitors.get("many_child") == 1:
        logger.info("Скидка 100% в день многодетных")
        new_price = 0
        sale_special = 1
    elif count_visitors.get("many_child") == 2:
        logger.info("Скидка 50% многодетным в будни")
        new_price = round(price * 0.5)
    elif count_visitors.get("invalid") == 1:
        logger.info("Скидка 100% инвалидам")
        new_price = 0
        sale_special = 1

    # Применяем обычную скидку, если она активна
    if sale_discount > 0:
        new_price = int(price - (price * sale_discount / 100))

    # Подсчет продаж для категории билетов
    if type_ticket == "взрослый":
        count_visitors["kol_sale_adult"] += 1
    elif type_ticket == "детский":
        count_visitors["kol_sale_child"] += 1

    return {
        "new_price": new_price,
        "sale_special": sale_special,
        "updated_count_visitors": count_visitors,
    }