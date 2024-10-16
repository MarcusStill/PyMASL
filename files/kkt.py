import subprocess
from typing import Any

from files import windows
from files.libfptr10 import IFptr
from files.logger import *

try:
    fptr = IFptr("")
except (Exception,) as e:
    info = "Не установлен драйвер ККТ!"
    windows.info_window(info, "", "")
    logger.warning(info)


# Константы для работы с результатами терминала
TERMINAL_SUCCESS_CODE: int = 0
TERMINAL_USER_CANCEL_CODE: int = 2000
APPROVE: str = "ОДОБРЕНО"
COINCIDENCE: str = "совпали"
EMAIL: str = "test.check@pymasl.ru"


def run_terminal_command(
    command_params: Any, pinpad_file: str = r"C:\sc552\loadparm.exe"
):
    """Запуск оплаты по банковскому терминалу и возврат кода результата."""
    pinpad_run: str = f"{pinpad_file} {command_params}"
    logger.info(f"Запуск команды: {pinpad_run}")
    try:
        result = subprocess.run(
            pinpad_run, check=False
        )  # check=False позволяет самостоятельно обрабатывать коды возврата
        logger.info(f"Команда завершена с кодом: {result.returncode}")
        return result
    except subprocess.SubprocessError as e:
        logger.error(f"Ошибка выполнения команды: {e}")
        return None  # Или обрабатывайте ошибку по-своему


def check_terminal_file(word: str, pinpad_file: str = r"C:\sc552\p"):
    """Проверка файла с результатом работы терминала."""
    try:
        with open(pinpad_file, encoding="IBM866") as file:
            text: str = file.read()
        logger.debug(f"Содержимое файла терминала: {text}")
        if word in text:
            logger.info("Проверка файла успешно завершена")
            return True
        else:
            logger.warning(f'Ожидаемый текст "{word}" не найден.')
            return False
    except FileNotFoundError as not_found:
        logger.error(f"Файл {pinpad_file} не найден: {not_found}")
        return False


@logger_wraps()
def terminal_oplata(amount):
    """Операуия оплаты по банковскому терминалу"""
    logger.info("Запуск функции terminal_oplata")
    status: int = 0
    while status != 1:
        plat_code = run_terminal_command(f"1 {amount}00")  # Добавляем '00' для копеек
        if plat_code is None:
            logger.error("Ошибка при выполнении команды терминала")
            return 0  # Обрабатываем ошибку
        logger.info(
            f"Статус проведения операции по банковскому терминалу: {plat_code.returncode}"
        )
        if plat_code.returncode == TERMINAL_SUCCESS_CODE:
            return 1 if check_terminal_file(APPROVE) else 0
        elif plat_code.returncode == TERMINAL_USER_CANCEL_CODE:
            logger.warning("Оплата отменена пользователем")
            status = 1  # Завершаем цикл и возвращаем ошибку
        else:
            # Произошла ошибка, предлагаем повторить операцию
            dialog = windows.info_dialog_window(
                "Внимание! Произошла ошибка при проведении платежа по банковской карте.",
                "Хотите повторить операцию?",
            )
            if dialog == 0:  # Пользователь выбрал "Нет"
                status = 1
    return 0


@logger_wraps()
def terminal_return(amount):
    """Операуия возврата по банковскому терминалу"""
    logger.info("Запуск функции terminal_return")
    logger.debug(f"В функцию была передана следующая сумма: {amount}")
    result = run_terminal_command(f"3 {amount}00")  # Добавляем '00' для копеек
    logger.debug(f"Терминал вернул следующий код операции: {result}")
    # if result == TERMINAL_SUCCESS_CODE: # TODO: проверить статус-код
    #     return 1 if check_terminal_file() else 0
    return 1 if check_terminal_file() else 0


@logger_wraps()
def terminal_canceling(amount):
    """Операуия отмены по банковскому терминалу"""
    logger.info("Запуск функции terminal_canceling")
    logger.debug(f"В функцию была передана следующая сумма: {amount}")
    result = run_terminal_command(f"8 {amount}00")  # Добавляем '00' для копеек
    logger.debug(f"Терминал вернул следующий код операции: {result}")
    # if result == TERMINAL_SUCCESS_CODE: # TODO: проверить статус-код
    #     return 1 if check_terminal_file() else 0
    return 1 if check_terminal_file() else 0


@logger_wraps()
def terminal_check_itog():
    """Сверка итогов работы банковского терминала"""
    logger.info("Запуск функции terminal_check_itog")
    result = run_terminal_command("7")
    logger.debug(f"Терминал вернул следующий код операции: {result}")
    return 1 if check_terminal_file(COINCIDENCE) else 0


def terminal_menu():
    """Вызов меню банковского терминала"""
    logger.info("Запуск функции terminal_menu")
    run_terminal_command("11")


def terminal_check_itog_window():
    """Сверка итогов работы банковского терминала
    ••••с выводом результата в QMessageBox"""
    logger.info("Запуск функции terminal_check_itog_window")
    run_terminal_command("7")
    try:
        info: str = read_pinpad_file()
        logger.info("Сверка итогов завершена")
        windows.info_window("Смотрите подробную информацию.", "", info)
    except FileNotFoundError as not_found:
        logger.warning(f"Файл не найден: {not_found.filename}")
        windows.info_window(
            "Ошибка сверки итогов по банковскому терминалу!", "", not_found.filename
        )


@logger_wraps()
def terminal_svod_check():
    """Сводный чек без детализации"""
    logger.info("Запуск функции terminal_svod_check")
    run_terminal_command("9")
    try:
        print_pinpad_check()
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def terminal_control_lenta():
    """Печать контрольной ленты"""
    logger.info("Запуск функции terminal_control_lenta")
    run_terminal_command("9 1")
    try:
        print_pinpad_check()
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def terminal_print_file():
    """Печать файла-отчета"""
    logger.info("Запуск функции terminal_print_file")
    try:
        print_pinpad_check()
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def terminal_file_in_window():
    """Показ банковского слип-чека в информационном окне"""
    logger.info("Запуск функции terminal_file_in_window")
    try:
        info: str = read_pinpad_file()
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)
    windows.info_window("Смотрите подробную информацию.", "", info)


@logger_wraps()
def terminal_copy_last_check():
    """Печать копии последнего чека"""
    logger.info("Запуск функции terminal_copy_last_check")
    run_terminal_command("12")
    try:
        print_pinpad_check()
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def read_pinpad_file(remove_newline=True, pinpad_file: str = r"C:\sc552\p"):
    """
    Чтение банковского чека с опциональным удалением переноса строки.

    Параметры:
    remove_newline (bool): Этот параметр определяет, нужно ли удалять символы новой строки при чтении файла.
    pinpad_file  (str): Путь к проверяемому файлу.
    """
    logger.info("Запуск функции read_pinpad_file")
    result_lines: list[str] = []
    try:
        with open(pinpad_file, "r", encoding="IBM866") as file:
            for line in file:
                # Убираем символ новой строки, если параметр remove_newline=True
                line: str = line.rstrip() if remove_newline else line
                result_lines.append(line)
                # Устанавливаем параметры для печати строки
                fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
                fptr.printText()
                # Устанавливаем перенос строки
                fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
    except FileNotFoundError as not_found:
        logger.warning("Файл не найден: %s", not_found.filename)
    return "".join(result_lines)


@logger_wraps()
def print_slip_check(kol: int = 2):
    """Печать слип-чека"""
    logger.info("Запуск функции print_slip_check")
    fptr.open()
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
    fptr.close()


@logger_wraps()
def print_pinpad_check(count: int = 2):
    """Печать слип-чека"""
    logger.info("Запуск функции print_pinpad_check")
    while count != 0:
        logger.debug("Функция печати нефискального документа")
        # Открываем соединение с ККМ
        fptr.open()
        # Открытие нефискального документа
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
        # Закрываем соединение с ККМ
        fptr.close()
        count -= 1


@logger_wraps()
def get_info():
    """Запрос информации о ККТ"""
    logger.info("Запуск функции get_info")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_MODEL_INFO)
    fptr.queryData()
    model = fptr.getParamInt(IFptr.LIBFPTR_PARAM_MODEL)
    model_name = fptr.getParamString(IFptr.LIBFPTR_PARAM_MODEL_NAME)
    firmware_version = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)
    fptr.close()
    info = (
        f"Номер модели ККТ: {model}.\nНаименование ККТ: {model_name}.\n"
        f"Версия ПО ККТ: {firmware_version}"
    )
    windows.info_window("Смотрите подробную информацию.", "", info)


@logger_wraps()
def get_status_obmena():
    """Статус информационного обмена"""
    logger.info("Запуск функции get_status_obmena")
    fptr.open()
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
    fptr.close()
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
    """Запрос текущих даты и времени ККТ"""
    logger.info("Запуск функции get_time")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_DATE_TIME)
    fptr.queryData()
    # Тип переменной datetime - datetime.datetime
    date_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
    logger.debug(f"Текущие дата и время в ККТ: {date_time}")
    windows.info_window(str(date_time), "", "")
    fptr.close()


@logger_wraps()
def smena_info():
    """Запрос состояния смены"""
    logger.info("Запуск функции smena_info")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SHIFT_STATE)
    fptr.queryData()
    state = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_STATE)
    number = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_NUMBER)
    date_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
    shift_states: dict[int, str] = {
        0: "закрыта",
        1: "открыта",
        2: "истекла (продолжительность смены больше 24 часов)"
    }
    result = shift_states.get(state, "неизвестное состояние")
    logger.debug(f"Состояние смены: {state} ({result})")
    info: str = (
        f"Состояние смены: {result}.\n"
        f"Номер смены: {number}.\n"
        f"Дата и время истечения текущей смены: {date_time}"
    )
    windows.info_window(f"Состояние смены: {result}", "Смотрите подробную информацию.", info)
    fptr.close()
    return state


@logger_wraps()
def last_document():
    """Копия последнего документа"""
    logger.info("Запуск функции last_document")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_LAST_DOCUMENT)
    fptr.report()
    fptr.close()


@logger_wraps()
def report_payment():
    """Отчет о состоянии расчетов"""
    logger.info("Запуск функции report_payment")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_OFD_EXCHANGE_STATUS)
    fptr.report()
    fptr.close()


@logger_wraps()
def report_x():
    """X-отчет"""
    logger.info("Запуск функции report_x")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_X)
    fptr.report()
    fptr.close()


@logger_wraps()
def kassir_reg(user):
    """Регистрация кассира"""
    logger.info("Запуск функции kassir_reg")
    fptr.open()
    fptr.setParam(1021, f"{user.last_name} {user.first_name}")
    fptr.setParam(1203, user.inn)
    fptr.operatorLogin()
    fptr.close()


@logger_wraps()
def deposit_of_money(amount):
    """Функция регистрация внесения денег в кассу"""
    logger.info("Запуск функции cash_deposit")
    logger.info(f"Внесено в кассу: {amount}")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, amount)
    fptr.cashIncome()
    fptr.close()


@logger_wraps()
def payment(amount):
    """Функция регистрация выплаты денег из кассы"""
    logger.info("Запуск функции payment")
    logger.info(f"Выплачено из кассы: {amount}")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, amount)
    fptr.cashOutcome()
    fptr.close()


@logger_wraps()
def balance_check():
    """Функция проверки баланса наличных денег в кассе"""
    logger.info("Запуск функции balance_check")
    fptr.open()
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
    # Закрываем соединение с ККМ
    fptr.close()
    return cashSum


@logger_wraps()
def operation_on_the_terminal(payment_type, type_operation, price):
    """Проведение операции по банковскому терминалу"""
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
    """Проведение операции оплаты"""
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
    """Закрытие кассовой смены"""
    logger.info("Запуск функции smena_close")
    state = smena_info()
    if state != 0:
        res = windows.info_dialog_window(
            "Внимание! Кассовая смена не закрыта",
            "Хотите сделать сверку итогов и" "снять отчет с гашением?",
        )
        if res == 1:
            result = terminal_check_itog()
            try:
                if result == 1:
                    fptr.open()
                    fptr.setParam(1021, f"{user.last_name} {user.first_name}")
                    fptr.setParam(1203, user.inn)
                    fptr.operatorLogin()
                    fptr.setParam(
                        IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_CLOSE_SHIFT
                    )
                    fptr.report()
                    fptr.checkDocumentClosed()
                    fptr.close()
            except FileNotFoundError as not_found:
                lines = "File not found!"
                logger.warning(not_found.filename)
                windows.info_window(
                    "Сверка итогов по банковскому" "терминалу завершена неудачно.",
                    "",
                    str(lines),
                )
        else:
            windows.info_window(
                "Сверка итогов по банковскому" "терминалу завершена неудачно.", "", ""
            )
            logger.warning(state)


def continue_print():
    """Допечатать документ"""
    logger.info("Запуск функции continue_print")
    fptr.continuePrint()
