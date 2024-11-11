from contextlib import contextmanager

from modules import windows
from modules.config import Config
from modules.libfptr10 import IFptr
from modules.logger import logger, logger_wraps
from modules.terminal import (
    terminal_check_itog,
    terminal_oplata,
    terminal_return,
    terminal_canceling,
    read_pinpad_file,
)

config = Config()

try:
    fptr = IFptr("")
except (Exception,) as e:
    logger.warning("Не установлен драйвер ККТ!")


EMAIL: str = "test.check@pymasl.ru"


@contextmanager
def fptr_connection():
    """Контекстный менеджер для управления подключением к ККМ."""
    fptr.open()
    try:
        yield
    finally:
        fptr.close()


@logger_wraps()
def print_text(text: str):
    """Печать слип-чека.

    Параметры:
        text (str): Строка для печати.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но может вызывать исключения в случае ошибок при печати.
    """
    logger.info("Запуск функции print_text")
    # Устанавливаем параметры для печати строки
    fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, text)
    fptr.printText()
    # Устанавливаем перенос строки
    fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)


@logger_wraps()
def print_slip_check(kol: int = 2):
    """Печать слип-чека.

    Параметры:
        kol (int): Количество копий слип-чека для печати. По умолчанию 2.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но может вызывать исключения в случае ошибок при печати.
    """
    logger.info("Запуск функции print_slip_check")
    with fptr_connection():
        # Открытие нефискального документа
        fptr.beginNonfiscalDocument()
        line: str = read_pinpad_file(remove_newline=True)
        fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
        fptr.printText()
        # Перенос строки
        fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
        # Промотка чековой ленты на одну строку (пустую)
        fptr.printText()
        # Закрытие нефискального документа
        fptr.endNonfiscalDocument()
        # Печать документа
        fptr.report()
        # Частичная отрезка ЧЛ
        fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_PART)
        # Отрезаем чек
        fptr.cut()
        # Создание копии нефискального документа
        if kol == 2:
            # Печатаем копию слип-чека
            fptr.beginNonfiscalDocument()
            fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, "")
            fptr.printText()
            line = read_pinpad_file(remove_newline=True)
            fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
            fptr.printText()
            fptr.printText()
            fptr.endNonfiscalDocument()
            fptr.report()
            fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_FULL)
            fptr.cut()


@logger_wraps()
def print_pinpad_check(count: int = 2):
    """Печать слип-чека.

    Параметры:
        count (int):
            Количество копий слип-чека для печати (по умолчанию 2).

    Возвращаемое значение:
        None:
            Функция не возвращает значений."""
    logger.info("Запуск функции print_pinpad_check")
    while count != 0:
        logger.debug("Функция печати нефискального документа")
        with fptr_connection():
            fptr.beginNonfiscalDocument()
            # Читаем чек из файла
            line = read_pinpad_file(remove_newline=False)
            fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
            fptr.printText()
            # Перенос строки
            fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
            # Промотка чековой ленты на одну строку (пустую)
            fptr.printText()
            # Закрытие нефискального документа
            fptr.endNonfiscalDocument()
            # Печать документа
            fptr.report()
            # Полная отрезка ЧЛ
            fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_FULL)
            # Отрезаем чек
            fptr.cut()
        count -= 1


@logger_wraps()
def get_info():
    """Запрос информации о ККТ.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но может открывать окно с информацией о ККТ.
    """
    logger.info("Запуск функции get_info")
    with fptr_connection():
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_MODEL_INFO)
        fptr.queryData()
        model = fptr.getParamInt(IFptr.LIBFPTR_PARAM_MODEL)
        model_name = fptr.getParamString(IFptr.LIBFPTR_PARAM_MODEL_NAME)
        firmware_version = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)
    info = (
        f"Номер модели ККТ: {model}.\nНаименование ККТ: {model_name}.\n"
        f"Версия ПО ККТ: {firmware_version}"
    )
    windows.info_window("Смотрите подробную информацию.", "", info)


@logger_wraps()
def get_status_obmena():
    """Статус информационного обмена.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но открывает окно с информацией о статусе обмена.
    """
    logger.info("Запуск функции get_status_obmena")
    with fptr_connection():
        fptr.setParam(
            IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_OFD_EXCHANGE_STATUS
        )
        fptr.fnQueryData()
        exchange_status = fptr.getParamInt(IFptr.LIBFPTR_PARAM_OFD_EXCHANGE_STATUS)
        unsent_count = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENTS_COUNT)
        first_unsent_number = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER)
        ofd_message_read = fptr.getParamBool(IFptr.LIBFPTR_PARAM_OFD_MESSAGE_READ)
        date_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
        okp_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_LAST_SUCCESSFUL_OKP)
    info: str = (
        f"Статус информационного обмена с ОФД: {exchange_status}.\n"
        f"Количество неотправленных документов: {unsent_count}.\n"
        f"Номер первого неотправленного документа: {first_unsent_number}.\n"
        f"Дата и время первого неотправленного документа: {date_time}.\n"
        f"Флаг наличия сообщения для ОФД: {ofd_message_read}.\n"
        f"Дата и время последнего успешного ОКП: {okp_time}."
    )
    windows.info_dialog_window("Смотрите подробную информацию.", info)


@logger_wraps()
def get_time():
    """Запрос текущих даты и времени ККТ.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но открывает окно с текущими датой и временем.
    """
    logger.info("Запуск функции get_time")
    with fptr_connection():
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_DATE_TIME)
        fptr.queryData()
        # Тип переменной datetime - datetime.datetime
        date_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
    logger.debug(f"Текущие дата и время в ККТ: {date_time}")
    windows.info_window(str(date_time), "", "")


@logger_wraps()
def smena_info():
    """Запрос состояния смены.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        int:
            Возвращает состояние смены (0 - закрыта, 1 - открыта, 2 - истекла).
    """
    logger.info("Запуск функции smena_info")
    with fptr_connection():
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SHIFT_STATE)
        fptr.queryData()
        state = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_STATE)
        number = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_NUMBER)
        date_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
    shift_states = {
        0: "закрыта",
        1: "открыта",
        2: "истекла (продолжительность смены больше 24 часов)",
    }
    result = shift_states.get(state, "неизвестное состояние")
    logger.debug(f"Состояние смены: {state} ({result})")
    info: str = (
        f"Состояние смены: {result}.\n"
        f"Номер смены: {number}.\n"
        f"Дата и время истечения текущей смены: {date_time}"
    )
    windows.info_window(
        f"Состояние смены: {result}", "Смотрите подробную информацию.", info
    )
    return state


@logger_wraps()
def last_document():
    """Копия последнего документа.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но выполняет печать последнего документа.
    """
    logger.info("Запуск функции last_document")
    with fptr_connection():
        fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_LAST_DOCUMENT)
        fptr.report()


@logger_wraps()
def report_payment():
    """Отчет о состоянии расчетов.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но выполняет печать отчета о состоянии расчетов.
    """
    logger.info("Запуск функции report_payment")
    with fptr_connection():
        fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_OFD_EXCHANGE_STATUS)
        fptr.report()


@logger_wraps()
def report_x():
    """X-отчет.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но выполняет печать X-отчета.
    """
    logger.info("Запуск функции report_x")
    with fptr_connection():
        fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_X)
        fptr.report()


@logger_wraps()
def kassir_reg(user):
    """Регистрация кассира.

    Параметры:
        user (object):
            Объект пользователя, содержащий информацию о кассире (фамилия, имя, ИНН).

    Возвращаемое значение:
        None:
            Функция не возвращает значений.
    """
    logger.info("Запуск функции kassir_reg")
    with fptr_connection():
        fptr.setParam(1021, f"{user.last_name} {user.first_name}")
        fptr.setParam(1203, user.inn)
        fptr.operatorLogin()


@logger_wraps()
def deposit_of_money(amount):
    """Функция регистрации внесения денег в кассу.

    Параметры:
        amount (float):
            Сумма, которую необходимо внести в кассу.

    Возвращаемое значение:
        None:
            Функция не возвращает значений.
    """
    logger.info("Запуск функции cash_deposit")
    logger.info(f"Внесено в кассу: {amount}")
    with fptr_connection():
        fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, amount)
        fptr.cashIncome()


@logger_wraps()
def payment(amount):
    """Функция регистрации выплаты денег из кассы.

    Параметры:
        amount (float):
            Сумма, которую необходимо выплатить из кассы.

    Возвращаемое значение:
        None:
            Функция не возвращает значений.
    """
    logger.info("Запуск функции payment")
    logger.info(f"Выплачено из кассы: {amount}")
    with fptr_connection():
        fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, amount)
        fptr.cashOutcome()


@logger_wraps()
def balance_check():
    """Функция проверки баланса наличных денег в кассе.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        float:
            Возвращает баланс наличных денег в кассе.
    """
    logger.info("Запуск функции balance_check")
    with fptr_connection():  # Использование контекстного менеджера для работы с ККТ
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_CASH_SUM)
        fptr.queryData()
        cashSum = fptr.getParamDouble(IFptr.LIBFPTR_PARAM_SUM)
        logger.info(f"Баланс наличных денег в кассе: {cashSum}")
        # Открытие нефискального документа
        fptr.beginNonfiscalDocument()
        fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, f"Баланс наличных денег: {cashSum}")
        fptr.printText()
        # Перенос строки
        fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
        # Промотка чековой ленты на одну строку (пустую)
        fptr.printText()
        # Закрытие нефискального документа
        fptr.endNonfiscalDocument()
        # Печать документа
        fptr.report()
        # Полная отрезка ЧЛ
        fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_FULL)
        # Отрезаем чек
        fptr.cut()
    return cashSum


@logger_wraps()
def operation_on_the_terminal(payment_type, type_operation, price):
    """Проведение операции по банковскому терминалу.

    Параметры:
        payment_type (int):
            Тип оплаты (например, 101 - оплата картой, 100 - offline оплата).
        type_operation (int):
            Тип операции (например, 1 - оплата, 2 - возврат, 3 - отмена).
        price (float):
            Сумма, на которую выполняется операция.

    Возвращаемое значение:
        tuple:
            - bank (int): Результат операции по терминалу (1 - успех, 0 - ошибка).
            - payment (int): Код оплаты (1 - оплата, 3 - offline).
    """
    logger.info("Запуск функции operation_on_the_terminal")
    bank = None
    if payment_type == 101:
        payment = 1
        logger.debug("оплата банковской картой")
        if type_operation == 1:
            logger.info("Запускаем оплату по банковскому терминалу")
            # результат операции по терминалу
            bank = terminal_oplata(str(price))
            logger.debug(f"Результат операции по терминалу: {bank}")
            if bank != 1:
                info = "Оплата по банковскому терминалу завершена с ошибкой"
                logger.warning(info)
                windows.info_window(info, "", "")
                return 0, payment
        elif type_operation == 2:
            logger.info("Запускаем операцию возврата по банковскому терминалу")
            # результат операции по терминалу
            bank = terminal_return(str(price))
            logger.debug(f"Результат операции по терминалу: {bank}")
            if bank != 1:
                info = "Возврат по банковскому терминалу завершен с ошибкой"
                logger.warning(info)
                windows.info_window(info, "", "")
                return 0, payment
        elif type_operation == 3:
            logger.info("Запускаем операцию отмены по банковскому терминалу")
            # результат операции по терминалу
            bank = terminal_canceling(str(price))
            logger.debug(f"Результат операции по терминалу: {bank}")
            if bank != 1:
                info = "Отмена по банковскому терминалу завершена с ошибкой"
                logger.warning(info)
                windows.info_window(info, "", "")
                return 0, payment
    # если offline оплата банковской картой
    elif payment_type == 100:
        logger.debug("Продажа новая. Начинаем оплату")
        payment = 3
        # результат операции по терминалу
        logger.info("Запускаем offline оплату по банковскому терминалу")
        bank = 1
    return bank, payment


@logger_wraps()
def check_open(sale_dict, payment_type, user, type_operation, print_check, price, bank):
    """Проведение операции оплаты.

    Параметры:
        sale_dict (dict):
            Словарь, содержащий информацию о продаже, включая количество и цены билетов.
        payment_type (int):
            Тип оплаты (например, 101 - оплата картой, 100 - offline оплата).
        user (object):
            Объект пользователя, содержащий информацию о кассире (фамилия, имя, ИНН).
        type_operation (int):
            Тип операции (например, 1 - продажа, 2 - возврат, 3 - отмена).
        print_check (int):
            Флаг, указывающий, нужно ли печатать чек (0 - не печатать, 1 - печатать).
        price (float):
            Сумма, на которую выполняется операция.
        bank (int):
            Результат операции по терминалу (например, 1 - успех).

    Возвращаемое значение:
        int:
            - 1, если операция выполнена успешно.
            - 0, если произошла ошибка.
    """
    logger.info("Запуск функции check_open")
    logger.debug(
        f"В функцию переданы: sale_dict = {sale_dict}, payment_type = {payment_type}, type_operation = {type_operation}, bank = {bank}"
    )
    if print_check == 0:
        logger.info("Кассовый чек не печатаем")
    elif print_check == 1:
        logger.info("Кассовый чек печатаем")
    logger.info(f"Тип оплаты: {payment_type}")
    # Открытие печатного чека
    logger.info("Открытие печатного чека")
    fptr.open()
    fptr.setParam(1021, f"{user.last_name} {user.first_name}")
    fptr.setParam(1203, user.inn)
    fptr.operatorLogin()
    if type_operation == 1:
        fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL)
    elif type_operation in (2, 3):
        fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL_RETURN)
    if print_check == 0:
        fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_ELECTRONICALLY, True)
        fptr.setParam(1008, EMAIL)
    fptr.openReceipt()
    # Регистрация позиции с указанием суммы налога
    # взрослый билет
    logger.info("Регистрация позиции: билет взрослый")
    if type_operation == 1:
        # проверяем есть ли билеты со скидкой
        kol_adult_edit = sale_dict["kol_adult"] - sale_dict["detail"][0]
        kol_child_edit = sale_dict["kol_child"] - sale_dict["detail"][2]
        time = sale_dict["detail"][6]
        if kol_adult_edit > 0:
            fptr.setParam(
                IFptr.LIBFPTR_PARAM_COMMODITY_NAME, f"Билет взрослый {time} ч."
            )
            fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale_dict["price_adult"])
            fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, kol_adult_edit)
            fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
            fptr.registration()
        # взрослый билет со скидкой
        logger.info("Регистрация позиции: билет взрослый со скидкой")
        if sale_dict["detail"][0] > 0 and sale_dict["detail"][1] > 0:
            fptr.setParam(
                IFptr.LIBFPTR_PARAM_COMMODITY_NAME, f"Билет взрослый акция {time} ч."
            )
            fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale_dict["detail"][1])
            fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, sale_dict["detail"][0])
            fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
            fptr.registration()
        # детский билет
        logger.info("Регистрация позиции: билет детский")
        if kol_child_edit > 0:
            fptr.setParam(
                IFptr.LIBFPTR_PARAM_COMMODITY_NAME, f"Билет детский {time} ч."
            )
            fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale_dict["price_child"])
            fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, kol_child_edit)
            fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
            fptr.registration()
        # детский билет со скидкой
        logger.info("Регистрация позиции: билет детский со скидкой")
        if sale_dict["detail"][2] > 0 and sale_dict["detail"][3] > 0:
            fptr.setParam(
                IFptr.LIBFPTR_PARAM_COMMODITY_NAME, f"Билет детский акция {time} ч."
            )
            fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale_dict["detail"][3])
            fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, sale_dict["detail"][2])
            fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
            fptr.registration()
    else:
        sale = sale_dict.items()
        for item in sale:
            fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, f"{item[0]}")
            fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, item[1][0])
            fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, item[1][1])
            fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
            fptr.registration()
    # Оплата чека
    logger.info("Оплата чека")
    if payment_type == 102:
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH)
        if type_operation == 1:
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sale_dict["detail"][7])
        elif type_operation in (2, 3):
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, price)
        fptr.payment()
        # Закрытие полностью оплаченного чека
        logger.info("Закрытие полностью оплаченного чека")
        fptr.closeReceipt()
    elif payment_type == 101:
        if bank == 1:
            fptr.setParam(
                IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_ELECTRONICALLY
            )
            if type_operation == 1:
                fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sale_dict["detail"][7])
            elif type_operation in (2, 3):
                fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, price)
            fptr.payment()
            # Закрытие полностью оплаченного чека
            logger.info("Закрытие полностью оплаченного чека")
            fptr.closeReceipt()
    elif payment_type == 100:
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_ELECTRONICALLY)
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sale_dict["detail"][7])
        fptr.payment()
        # Закрытие полностью оплаченного чека
        logger.info("Закрытие полностью оплаченного чека")
        fptr.closeReceipt()
    while fptr.checkDocumentClosed() < 0:
        # Не удалось проверить состояние документа.
        # Вывести пользователю текст ошибки, попросить устранить неполадку и повторить запрос
        logger.warning(
            f"Не удалось проверить состояние документа. Ошибка: {fptr.errorDescription()}"
        )
        windows.info_window(
            "Не удалось проверить состояние документа.\n"
            "Устраните неполадку и повторите запрос.",
            str(fptr.errorDescription()),
            "",
        )
        continue
    if print_check == 0:
        fptr.close()
    if not fptr.getParamBool(IFptr.LIBFPTR_PARAM_DOCUMENT_CLOSED):
        # Документ не закрылся. Требуется его отменить (если это чек) и сформировать заново
        logger.warning(
            f"Документ не закрылся.\n"
            f"Требуется его отменить и сформировать заново. Ошибка: {fptr.errorDescription()}"
        )
        windows.info_window(
            "Документ не закрылся. \n"
            "Требуется его отменить (если это чек) и сформировать заново.",
            str(fptr.errorDescription()),
            "",
        )
        fptr.cancelReceipt()
        fptr.close()
        return 0
    fptr.continuePrint()
    fptr.close()
    return 1


@logger_wraps()
def smena_close(user):
    """Закрытие кассовой смены.

    Параметры:
        user (object):
            Объект пользователя, содержащий информацию о кассире (фамилия, имя, ИНН).

    Возвращаемое значение:
        None:
            Функция не возвращает значений.
    """
    logger.info("Запуск функции smena_close")
    state = smena_info()
    if state != 0:
        res = windows.info_dialog_window(
            "Внимание! Кассовая смена не закрыта",
            "Хотите сделать сверку итогов и снять отчет с гашением?",
        )
        if res == 1:
            result = terminal_check_itog()
            try:
                if result == 1:
                    with fptr_connection():
                        fptr.setParam(1021, f"{user.last_name} {user.first_name}")
                        fptr.setParam(1203, user.inn)
                        fptr.operatorLogin()
                        fptr.setParam(
                            IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_CLOSE_SHIFT
                        )
                        fptr.report()
                        fptr.checkDocumentClosed()
            except FileNotFoundError as not_found:
                lines = "File not found!"
                logger.warning(not_found.filename)
                windows.info_window(
                    "Сверка итогов по банковскому терминалу завершена неудачно.",
                    "",
                    str(lines),
                )
        else:
            windows.info_window(
                "Сверка итогов по банковскому терминалу завершена неудачно.", "", ""
            )
            logger.warning(state)


def continue_print():
    """Допечатать документ.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но продолжает печать текущего документа.
    """
    logger.info("Запуск функции continue_print")
    fptr.continuePrint()
