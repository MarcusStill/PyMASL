import subprocess

from files import windows
from files.libfptr10 import IFptr
from files.logger import *


try:
    fptr = IFptr('')
except (Exception,) as e:
    info = 'Не установлен драйвер ККТ!'
    windows.info_window(info, '', '')
    logger.warning(info)


GOOD = 'ОДОБРЕНО'
EMAIL = "test.check@pymasl.ru"


@logger_wraps()
def terminal_oplata(amount):
    """Операуия оплаты по банковскому терминалу"""
    logger.info("Запуск функции terminal_oplata")
    result = ''
    status = 0
    amount += '00'
    pinpad = 'C:\\sc552\\loadparm.exe'
    pay_param = ' 1 ' + amount
    pinpad_run = pinpad + pay_param
    # проверяем статус проведения операции по банковскому терминалу
    while status != 1:
        proc = subprocess.run(pinpad_run)
        plat = proc.returncode
        logger.info("Статус проведения операции по банковскому терминалу: %s" % plat)
        if plat == 0 or plat == 2000:
            # оплата прошла успешно (0) или отменена пользователем (2000)
            status = 1
        else:
            dialog = windows.info_dialog_window('Внимание! '
                                                'Произошла ошибка при проведении платежа по банковской карте.',
                                                'Хотите повторить операцию?')
            # пользователь нажал кнопку "нет"
            if dialog == 0:
                status = 1
    # Проверка файла с результатом работы банковского терминала
    logger.info("Proverka file")
    pinpad_file = r"C:\sc552\p"
    # Проверяем одобрение операции
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            text = file.read()
        if GOOD in text:
            logger.info("Проверка файла успешно завершена")
            result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        logger.warning("Проверка файла завершилась с ошибкой")
        result = 0
    return result


@logger_wraps()
def terminal_return(amount):
    """Операуия возврата по банковскому терминалу"""
    logger.info("Запуск функции terminal_return")
    result = ''
    pinpad_file = r"C:\sc552\p"
    amount += '00'
    pinpad = 'C:\\sc552\\loadparm.exe'
    pay_param = ' 3 ' + amount
    pinpad_run = pinpad + pay_param
    subprocess.call(pinpad_run)
    #  Проверка файла с результатом работы банковского терминала
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            text = file.read()
        if GOOD in text:
            logger.info("Проверка файла успешно завершена")
            result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        logger.warning("Проверка файла завершилась с ошибкой")
        result = 0
    return result


@logger_wraps()
def terminal_canceling(amount):
    """Операуия отмены по банковскому терминалу"""
    logger.info("Запуск функции terminal_canceling")
    result = ''
    pinpad_file = r"C:\sc552\p"
    amount += '00'
    pinpad = 'C:\\sc552\\loadparm.exe'
    pay_param = ' 8 ' + amount
    pinpad_run = pinpad + pay_param
    subprocess.call(pinpad_run)
    #  Проверка файла с результатом работы банковского терминала
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            text = file.read()
        if GOOD in text:
            logger.info("Проверка файла успешно завершена")
            result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        logger.warning("Проверка файла завершилась с ошибкой")
        result = 0
    return result


@logger_wraps()
def terminal_check_itog():
    """Сверка итогов работы банковского терминала"""
    logger.info("Запуск функции terminal_check_itog")
    result = ''
    pinpad_file = r"C:\sc552\p"
    subprocess.call('C:\\sc552\\loadparm.exe 7')
    logger.debug('Check itog')
    file_result = 'совпали'
    # Выводим результат сверки итогов
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            text = file.read()
        if file_result in text:
            logger.info("Проверка файла успешно завершена")
            result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        result = 0
    return result


@logger_wraps()
def terminal_check_itog_window():
    """Сверка итогов работы банковского терминала
••••с выводом результата в QMessageBox"""
    logger.info("Запуск функции terminal_check_itog_window")
    pinpad_file = r"C:\sc552\p"
    subprocess.call('C:\\sc552\\loadparm.exe 7')
    logger.debug('Check itog in QMessageBox')
    # Выводим результат сверки итогов
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            lines = file.readlines()[2:]
            logger.info("Сверка итогов завершена")
            windows.info_window(
                'Сверка итогов по банковскому терминалу '
                'завершена.', '', str(lines)
            )
    except FileNotFoundError as not_found:
        lines = 'File not found!'
        logger.warning(not_found.filename)
        windows.info_window(
            'Ошибка сверки итогов по банковскому '
            'терминалу!', '', str(lines)
        )


@logger_wraps()
def terminal_svod_check():
    """Сводный чек без детализации"""
    logger.info("Запуск функции terminal_svod_check")
    subprocess.call('C:\\sc552\\loadparm.exe 9')
    try:
        print_pinpad_check()
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def terminal_control_lenta():
    """Печать контрольной ленты"""
    logger.info("Запуск функции terminal_control_lenta")
    subprocess.call('C:\\sc552\\loadparm.exe 9 1')
    try:
        print_pinpad_check()
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def terminal_copy_last_check():
    """Печать копии последнего чека"""
    logger.info("Запуск функции terminal_copy_last_check")
    subprocess.call('C:\\sc552\\loadparm.exe 12')
    try:
        print_pinpad_check()
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def read_slip_check():
    """Чтение слип-чека"""
    logger.info("Запуск функции read_slip_check")
    pinpad_file = r"C:\sc552\p"
    result = ''
    try:
        with open(pinpad_file, 'r', encoding='IBM866') as file:
            while line := file.readline().rstrip():
                result = result + line
                fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
                fptr.printText()
                # Перенос строки
                fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
    except FileNotFoundError as not_found:
        logger.warning("Проверка файла завершилась с ошибкой")
        logger.warning(not_found.filename)
    return result

@logger_wraps()
def read_pinpad_file():
    """Чтение банковского чека"""
    logger.info("Запуск функции read_pinpad_file")
    pinpad_file = r"C:\sc552\p"
    result = ''
    try:
        with open(pinpad_file, 'r', encoding='IBM866') as file:
            while line := file.readline():
                result = result + line
                fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
                fptr.printText()
                # Перенос строки
                fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
    except FileNotFoundError as not_found:
        logger.warning("Проверка файла завершилась с ошибкой")
        logger.warning(not_found.filename)
    return result


@logger_wraps()
def print_slip_check(kol=2):
    """Печать слип-чека"""
    logger.info("Запуск функции print_slip_check")
    logger.debug("Функция печати нефискального документа")
    logger.debug("Открываем соединение с ККМ")
    fptr.open()
    logger.debug("Открытие нефискального документа")
    fptr.beginNonfiscalDocument()
    logger.info("Читаем чек из файла")
    line = read_slip_check()
    fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
    fptr.printText()
    # Перенос строки
    fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
    # Промотка чековой ленты на одну строку (пустую)
    fptr.printText()
    logger.debug("Закрытие нефискального документа")
    fptr.endNonfiscalDocument()
    logger.debug("Печать документа")
    fptr.report()
    # Частичная отрезка ЧЛ
    fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_PART)
    logger.debug("Отрезаем чек")
    fptr.cut()
    logger.debug("Создание копии нефискального документа")
    if kol == 2:
        # Печатаем копию слип-чека
        fptr.beginNonfiscalDocument()
        fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, '')
        fptr.printText()
        line = read_slip_check()
        fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
        fptr.printText()
        # Промотка чековой ленты на одну строку (пустую)
        fptr.printText()
        logger.debug("Закрытие нефискального документа")
        fptr.endNonfiscalDocument()
        logger.debug("Печать документа")
        fptr.report()
        # Полная отрезка ЧЛ
        fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_FULL)
        logger.debug("Отрезаем чек")
        fptr.cut()
    logger.debug("Закрываем соединение с ККМ")
    fptr.close()


@logger_wraps()
def print_pinpad_check():
    """Печать слип-чека"""
    logger.info("Запуск функции print_pinpad_check")
    logger.debug("Функция печати нефискального документа")
    logger.debug("Открываем соединение с ККМ")
    fptr.open()
    logger.debug("Открытие нефискального документа")
    fptr.beginNonfiscalDocument()
    logger.info("Читаем чек из файла")
    line = read_pinpad_file()
    fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
    fptr.printText()
    # Перенос строки
    fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
    # Промотка чековой ленты на одну строку (пустую)
    fptr.printText()
    logger.debug("Закрытие нефискального документа")
    fptr.endNonfiscalDocument()
    logger.debug("Печать документа")
    fptr.report()
    # Полная отрезка ЧЛ
    fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_FULL)
    logger.debug("Отрезаем чек")
    fptr.cut()
    logger.debug("Закрываем соединение с ККМ")
    fptr.close()


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
    logger.debug("Номер модели ККТ: %s" % model)
    logger.debug("Наименование ККТ: %s" % model_name)
    logger.debug("Версия ПО ККТ: %s" % firmware_version)
    fptr.close()
    info = "Номер модели ККТ: " + str(model) + ".\nНаименование ККТ: " + str(
        model_name) + ".\nВерсия ПО ККТ: " + str(firmware_version)
    windows.info_window('Смотрите подробную информацию.', '', info)


@logger_wraps()
def get_status_obmena():
    """Статус информационного обмена"""
    logger.info("Запуск функции get_status_obmena")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE,
                  IFptr.LIBFPTR_FNDT_OFD_EXCHANGE_STATUS)
    fptr.fnQueryData()
    exchange_status = fptr.getParamInt(IFptr.LIBFPTR_PARAM_OFD_EXCHANGE_STATUS)
    unsent_count = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENTS_COUNT)
    first_unsent_number = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER)
    ofd_message_read = fptr.getParamBool(IFptr.LIBFPTR_PARAM_OFD_MESSAGE_READ)
    date_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
    logger.debug("ExchangeStatus: %s" % exchange_status)
    logger.debug("UnsentCount: %s" % unsent_count)
    logger.debug("FirstUnsentNumber: %s" % first_unsent_number)
    logger.debug("OfdMessageRead: %s" % ofd_message_read)
    logger.debug("DateTime: %s" % date_time)
    fptr.close()
    info = ("ExchangeStatus: " + str(exchange_status) + ".\nUnsentCount: "
            + str(unsent_count) + ".\nFirstUnsentNumber: "
            + str(first_unsent_number) + ".\nOfdMessageRead: "
            + str(ofd_message_read) + ".\nDateTime: " + str(date_time))
    windows.info_window('Смотрите подробную информацию.', '', info)


@logger_wraps()
def get_time():
    """Запрос текущих даты и времени ККТ"""
    logger.info("Запуск функции get_time")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_DATE_TIME)
    fptr.queryData()
    # Тип переменной datetime - datetime.datetime
    date_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
    logger.debug("Текущие дата и время в ККТ: %s" % date_time)
    windows.info_window(str(date_time), '', '')
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
    # Тип переменной datetime - datetime.datetime
    date_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
    logger.debug("Состояние смены:  %s" % state)
    if state == 0:
        result = 'закрыта'
    else:
        result = 'открыта'
    logger.debug("Номер смены: %s" % number)
    logger.debug("Дата и время истечения текущей смены: %s" % date_time)
    info = ("Состояние смены: " + result + ".\nНомер смены: " + str(number)
            + ".\nДата и время истечения текущей смены: " + str(date_time))
    windows.info_window("Состояние смены: " + result,
                        'Смотрите подробную информацию.', info)
    fptr.close()
    return state


@logger_wraps()
def last_document():
    """Копия последнего документа"""
    logger.info("Запуск функции last_document")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE,
                  IFptr.LIBFPTR_RT_LAST_DOCUMENT)
    fptr.report()
    fptr.close()


@logger_wraps()
def report_payment():
    """Отчет о состоянии расчетов"""
    logger.info("Запуск функции report_payment")
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE,
                  IFptr.LIBFPTR_RT_OFD_EXCHANGE_STATUS)
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
    fptr.setParam(1021, f'{user.last_name} {user.first_name}')
    fptr.setParam(1203, user.inn)
    fptr.operatorLogin()
    fptr.close()


@logger_wraps()
def deposit_of_money(amount):
    """Функция регистрация внесения денег в кассу"""
    logger.info("Запуск функции cash_deposit")
    logger.info(f'Внесено в кассу: {amount}')
    fptr.open()
    fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, amount)
    fptr.cashIncome()
    fptr.close()


@logger_wraps()
def payment(amount):
    """Функция регистрация выплаты денег из кассы"""
    logger.info("Запуск функции payment")
    logger.info(f'Выплачено из кассы: {amount}')
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
    logger.info(f'Баланс наличных денег в кассе: {cashSum}')
    logger.debug("Открытие нефискального документа")
    fptr.beginNonfiscalDocument()
    fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, f'Баланс наличных денег: {cashSum}')
    fptr.printText()
    # Перенос строки
    fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
    # Промотка чековой ленты на одну строку (пустую)
    fptr.printText()
    logger.debug("Закрытие нефискального документа")
    fptr.endNonfiscalDocument()
    logger.debug("Печать документа")
    fptr.report()
    # Полная отрезка ЧЛ
    fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_FULL)
    logger.debug("Отрезаем чек")
    fptr.cut()
    logger.debug("Закрываем соединение с ККМ")
    fptr.close()
    return cashSum


@logger_wraps()
def check_open(sale_dict, payment_type, user, type_operation, print_check, price):
    """Проведение операции оплаты"""
    logger.info("Запуск функции check_open")
    logger.debug(f'В функцию переданы: sale_dict = {sale_dict}, итоговая сумма = {price}')
    time = sale_dict['detail'][6]
    bank, kkt_type, payment = None, None, None
    if print_check == 0:
        logger.info("Кассовый чек не печатаем")
    elif print_check == 1:
        logger.info("Кассовый чек печатаем")
    # если оплата банковской картой
    if payment_type == 101:
        if type_operation == 1:
            logger.info("Запускаем оплату по банковскому терминалу")
            payment = 1
            # результат операции по терминалу
            bank = terminal_oplata(str(sale_dict['detail'][7]))
            logger.debug("BANK: %s" % bank)
            if bank != 1:
                info = "Оплата по банковскому терминалу завершена с ошибкой"
                logger.warning(info)
                windows.info_window(info,'', "")
                return 0, payment
        elif type_operation == 2:
            logger.info("Запускаем операцию возврата по банковскому терминалу")
            payment = 1
            # результат операции по терминалу
            bank = terminal_return(str(price))
            logger.debug("BANK: %s" % bank)
            if bank != 1:
                info = "Возврат по банковскому терминалу завершен с ошибкой"
                logger.warning(info)
                windows.info_window(info,'', "")
                return 0, payment
        elif type_operation == 3:
            logger.info("Запускаем операцию отмены по банковскому терминалу")
            payment = 1
            # результат операции по терминалу
            bank = terminal_canceling(str(price))
            logger.debug("BANK: %s" % bank)
            if bank != 1:
                info = "Отмена по банковскому терминалу завершена с ошибкой"
                logger.warning(info)
                windows.info_window(info,'', "")
                return 0, payment
    # если offline оплата банковской картой
    elif payment_type == 100:
        payment = 3
        # результат операции по терминалу
        logger.info("Запускаем offline оплату по банковскому терминалу")
        bank = 1
    # проверяем есть ли билеты со скидкой
    kol_adult_edit = sale_dict['kol_adult'] - sale_dict['detail'][0]
    kol_child_edit = sale_dict['kol_child'] - sale_dict['detail'][2]
    logger.info("Тип оплаты: %s" % payment_type)
    # Открытие печатного чека
    logger.info("Открытие печатного чека")
    fptr.open()
    fptr.setParam(1021, f'{user.last_name} {user.first_name}')
    fptr.setParam(1203, user.inn)
    fptr.operatorLogin()
    if type_operation == 1:
        fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL)
        logger.info("Тип операции: покупка")
    elif type_operation in (2, 3):
        fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL_RETURN)
        logger.info("Тип операции: возврат")
    if print_check == 0:
        fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_ELECTRONICALLY, True)
        fptr.setParam(1008, EMAIL)
    fptr.openReceipt()
    # Регистрация позиции с указанием суммы налога
    # взрослый билет
    logger.info("Регистрация позиции: билет взрослый")
    if kol_adult_edit > 0:
        fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME,
                      f'Билет взрослый {time} ч.')
        fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale_dict['price_adult'])
        fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, kol_adult_edit)
        fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
        fptr.registration()
    # взрослый билет со скидкой
    logger.info("Регистрация позиции: билет взрослый со скидкой")
    if sale_dict['detail'][0] > 0 and sale_dict['detail'][1] > 0:
        fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME,
                      f'Билет взрослый акция {time} ч.')
        fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale_dict['detail'][1])
        fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, sale_dict['detail'][0])
        fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
        fptr.registration()
    # детский билет
    logger.info("Регистрация позиции: билет детский")
    if kol_child_edit > 0:
        fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME,
                      f'Билет детский {time} ч.')
        fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale_dict['price_child'])
        fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, kol_child_edit)
        fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
        fptr.registration()
    # детский билет со скидкой
    logger.info("Регистрация позиции: билет детский со скидкой")
    if sale_dict['detail'][2] > 0 and sale_dict['detail'][3] > 0:
        fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME,
                      f'Билет детский акция {time} ч.')
        fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale_dict['detail'][3])
        fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, sale_dict['detail'][2])
        fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
        fptr.registration()
    # Оплата чека
    logger.info("Оплата чека")
    if payment_type == 102:
        payment = 2
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH)
        if type_operation == 1:
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sale_dict['detail'][7])
        elif type_operation in (2, 3):
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, price)
        fptr.payment()
        # Закрытие полностью оплаченного чека
        logger.info("Закрытие полностью оплаченного чека")
        fptr.closeReceipt()
    elif payment_type == 101:
        if bank == 1:
            fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_ELECTRONICALLY)
            if type_operation == 1:
                fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sale_dict['detail'][7])
            elif type_operation in (2, 3):
                fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, price)
            fptr.payment()
            # Закрытие полностью оплаченного чека
            logger.info("Закрытие полностью оплаченного чека")
            fptr.closeReceipt()
    elif payment_type == 100:
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_ELECTRONICALLY)
        fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sale_dict['detail'][7])
        fptr.payment()
        # Закрытие полностью оплаченного чека
        logger.info("Закрытие полностью оплаченного чека")
        fptr.closeReceipt()
    while fptr.checkDocumentClosed() < 0:
        # Не удалось проверить состояние документа.
        # Вывести пользователю текст ошибки, попросить устранить неполадку и повторить запрос
        logger.warning("Не удалось проверить состояние документа (Ошибка %s" % str(fptr.errorDescription()))
        windows.info_window('Не удалось проверить состояние документа.\n'
                            'Устраните неполадку и повторите запрос.',
                            str(fptr.errorDescription()), '')
        continue
    if print_check == 0:
        fptr.close()
    if not fptr.getParamBool(IFptr.LIBFPTR_PARAM_DOCUMENT_CLOSED):
        # Документ не закрылся. Требуется его отменить (если это чек) и сформировать заново
        logger.warning("Документ не закрылся."
                       "Требуется его отменить и сформировать заново (Ошибка %s" % str(fptr.errorDescription()))
        windows.info_window('Документ не закрылся. \n'
                            'Требуется его отменить (если это чек) и сформировать заново.',
                            str(fptr.errorDescription()), '')
        fptr.cancelReceipt()
        fptr.close()
        return 0, payment
    fptr.continuePrint()
    fptr.close()
    return 1, payment


@logger_wraps()
def smena_close(user):
    """Закрытие кассовой смены"""
    logger.info("Запуск функции smena_close")
    state = smena_info()
    if state != 0:
        res = windows.info_dialog_window('Внимание! Кассовая смена не закрыта',
                                         'Хотите сделать сверку итогов и'
                                         'снять отчет с гашением?')
        if res == 1:
            result = terminal_check_itog()
            try:
                if result == 1:
                    fptr.open()
                    fptr.setParam(1021, f'{user.last_name} {user.first_name}')
                    fptr.setParam(1203, user.inn)
                    fptr.operatorLogin()
                    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE,
                                  IFptr.LIBFPTR_RT_CLOSE_SHIFT)
                    fptr.report()
                    fptr.checkDocumentClosed()
                    fptr.close()
            except FileNotFoundError as not_found:
                lines = 'File not found!'
                logger.warning(not_found.filename)
                windows.info_window('Сверка итогов по банковскому'
                                    'терминалу завершена неудачно.', '',
                                    str(lines))
        else:
            windows.info_window('Сверка итогов по банковскому'
                                'терминалу завершена неудачно.', '', '')
            logger.warning(state)


def continue_print():
    """Допечатать документ"""
    logger.info("Запуск функции continue_print")
    fptr.continuePrint()
