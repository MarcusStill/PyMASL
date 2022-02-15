from files.libfptr10 import IFptr
from files.logger import *
from files import windows
import subprocess


fptr = IFptr('')


@logger_wraps()
def terminal_oplata(sum):
    """Операуия оплаты по дбанковскому терминалу"""
    sum += '00'
    pinpad = 'C:\\sc552\\loadparm.exe'
    pay_param = ' 1 ' + sum
    pinpad_run = pinpad + pay_param
    subprocess.call(pinpad_run)
    """Проверка файла с результатом работы дбанковского терминала"""
    logger.info("Proverka file")
    pinpad_file = r"C:\sc552\p"
    """Проверяем одобрение операции"""
    file_result = 'ОДОБРЕНО'
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            text = file.read()
        if file_result in text:
            logger.info("Проверка файла успешно завершена")
            result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        logger.warning("Проверка файла завершилась с ошибкой")
        result = 0
    return result


@logger_wraps()
def terminal_vozvrat(sum):
    """Операуия возврата по дбанковскому терминалу"""
    pinpad_file = r"C:\sc552\p"
    sum += '00'
    pinpad = 'C:\\sc552\\loadparm.exe'
    pay_param = ' 8 ' + sum
    pinpad_run = pinpad + pay_param
    subprocess.call(pinpad_run)
    """Проверка файла с результатом работы дбанковского терминала"""
    logger.info("Proverka file")
    """Проверяем одобрение операции"""
    file_result = 'ОДОБРЕНО'
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            text = file.read()
        if file_result in text:
            logger.info("Проверка файла успешно завершена")
            result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        logger.warning("Проверка файла завершилась с ошибкой")
        result = 0
    return result


@logger_wraps()
def terminal_check_itog():
    """Сверка итогов работы дбанковского терминала"""
    logger.info("Proverka file")
    pinpad_file = r"C:\sc552\p"
    subprocess.call('C:\\sc552\\loadparm.exe 7')
    logger.debug('Check itog')
    lines = None
    """Выводим результат сверки итогов"""
    try:
        with open(pinpad_file, encoding='IBM866') as file:
            lines = file.readlines()[2:]
        logger.info(lines)
        logger.info("Сверка итогов успешно завершена")
        result = 1
    except FileNotFoundError as not_found:
        print('File not found:', not_found.filename)
        logger.info("File not found")
        result = 0
    return result, lines


@logger_wraps()
def read_slip_check():
    logger.info("Чтение слип-чека из файла")
    pinpad_file = r"C:\sc552\p"
    try:
        with open(pinpad_file, 'r', encoding='IBM866') as file:
            while (line := file.readline().rstrip()):
                print(line)
                fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, line)
                fptr.printText()
                # Перенос строки
                fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
    except FileNotFoundError as not_found:
        logger.warning("Проверка файла завершилась с ошибкой")
        logger.warning(not_found.filename)


@logger_wraps()
def print_slip_check():
    logger.info("Функция печати нефискального документа")
    logger.info("Открываем соединение с ККМ")
    fptr.open()
    logger.info("Открытие нефискального документа")
    fptr.beginNonfiscalDocument()
    logger.info("Читаем чек из файла")
    read_slip_check()
    logger.info("Промотка чековой ленты на одну строку (пустую)")
    fptr.printText()
    logger.info("Закрытие нефискального документа")
    fptr.endNonfiscalDocument()
    logger.info("Печать документа")
    fptr.report()
    #Частичная отрезка ЧЛ
    fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_PART)
    logger.info("Отрезаем чек")
    fptr.cut()
    logger.info("Создение копии нефискального документа")
    # Печатаем копию слип-чека
    fptr.beginNonfiscalDocument()
    fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, "Копия 1")
    fptr.printText()
    read_slip_check()
    logger.info("Промотка чековой ленты на одну строку (пустую)")
    fptr.printText()
    logger.info("Закрытие нефискального документа")
    fptr.endNonfiscalDocument()
    logger.info("Печать документа")
    fptr.report()
    # Частичная отрезка ЧЛ
    fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_PART)
    logger.info("Отрезаем чек")
    fptr.cut()
    logger.info("Закрываем соединение с ККМ")
    fptr.close()


@logger_wraps()
def get_info():
	"""Запрос информации о ККТ"""
	logger.info("Inside the function def get_info")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_MODEL_INFO)
	fptr.queryData()
	model = fptr.getParamInt(IFptr.LIBFPTR_PARAM_MODEL)
	modelName = fptr.getParamString(IFptr.LIBFPTR_PARAM_MODEL_NAME)
	firmwareVersion = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)
	logger.info("Номер модели ККТ: %s" % (model))
	logger.info("Наименование ККТ: %s" % (modelName))
	logger.info("Версия ПО ККТ: %s" % (firmwareVersion))
	fptr.close()
	info = "Номер модели ККТ: " + str(model) + ".\nНаименование ККТ: " + str(
		modelName) + ".\nВерсия ПО ККТ: " + str(firmwareVersion)
	windows.info_window('Смотрите подробную информацию.', info)


@logger_wraps()
def get_status_obmena():
	"""Статус информационного обмена"""
	logger.info("Inside the function def get_status_obmena")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_OFD_EXCHANGE_STATUS)
	fptr.fnQueryData()
	exchangeStatus = fptr.getParamInt(IFptr.LIBFPTR_PARAM_OFD_EXCHANGE_STATUS)
	unsentCount = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENTS_COUNT)
	firstUnsentNumber = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER)
	ofdMessageRead = fptr.getParamBool(IFptr.LIBFPTR_PARAM_OFD_MESSAGE_READ)
	dateTime = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
	logger.info("ExchangeStatus: %s" % (exchangeStatus))
	logger.info("UnsentCount: %s" % (unsentCount))
	logger.info("FirstUnsentNumber: %s" % (firstUnsentNumber))
	logger.info("OfdMessageRead: %s" % (ofdMessageRead))
	logger.info("DateTime: %s" % (dateTime))
	fptr.close()
	info = "ExchangeStatus: " + str(exchangeStatus) + ".\nUnsentCount: " + str(unsentCount) + ".\nFirstUnsentNumber: " + str(firstUnsentNumber)+ ".\nOfdMessageRead: " + str(ofdMessageRead)+ ".\nDateTime: " + str(dateTime)
	windows.info_window('Смотрите подробную информацию.', info)


@logger_wraps()
def get_time():
	"""Запрос текущих даты и времени ККТ"""
	logger.info("Inside the function def get_time")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_DATE_TIME)
	fptr.queryData()
	# Тип переменной datetime - datetime.datetime
	dateTime = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
	logger.info("dateTime: %s" % (dateTime))
	windows.info_window(str(dateTime), '')
	fptr.close()


@logger_wraps()
def smena_info():
	"""Запрос состояния смены"""
	logger.info("Inside the function def smena_info")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SHIFT_STATE)
	fptr.queryData()
	state = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_STATE)
	number = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_NUMBER)
	# Тип переменной datetime - datetime.datetime
	dateTime = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
	logger.info("Состояние смены:  %s" % (state))
	logger.info("Номер смены: %s" % (number))
	logger.info("Дата и время истечения текущей смены: %s" % (dateTime))
	info = "Состояние смены:" + str(state) +".\nНомер смены: " + str(number) +".\nДата и время истечения текущей смены: " + str(dateTime)
	windows.info_window('Смотрите подробную информацию.', info)
	fptr.close()


@logger_wraps()
def last_document():
	"""Копия последнего документа"""
	logger.info("Inside the function def last_document")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_LAST_DOCUMENT)
	fptr.report()	
	fptr.close()


@logger_wraps()
def report_payment():
	"""Отчет о состоянии расчетов"""
	logger.info("Inside the function def report_payment")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_OFD_EXCHANGE_STATUS)
	fptr.report()
	fptr.close()


@logger_wraps()
def report_x():
	"""X-отчет"""
	logger.info("Inside the function def report_x")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_X)
	fptr.report()
	fptr.close()


@logger_wraps()
def kassir_reg(user):
	"""Регистрация кассира"""
	logger.info("Inside the function def kassir_reg")
	fptr.open()
	fptr.setParam(1021, f'{user[0]} {user[1]}')
	fptr.setParam(1203, user[2])
	fptr.operatorLogin()
	fptr.close()


@logger_wraps()
def check_open(sale_tuple,  payment_type, user):
	logger.info("Inside the function def check_open")
	sale = sale_tuple
	logger.info("payment_type: %s" % (payment_type))
	state = 0
	"""Открытие печатного чека"""
	fptr.open()
	fptr.setParam(1021, f'{user[0]} {user[1]}')
	fptr.setParam(1203, user[2])
	fptr.operatorLogin()
	fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL)
	fptr.openReceipt()
	"""Регистрация позиции с указанием суммы налога"""
	if sale[0] > 0:
		fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, "Билет взрослый")
		fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale[1])
		fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, sale[0])
		fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
		fptr.registration()
	if sale[2] > 0:
		fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, "Билет детский")
		fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, sale[3])
		fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, sale[2])
		fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
		fptr.registration()
	"""Оплата чека"""
	if payment_type == 102:
		payment = 2
		fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH)
		fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sale[4])
		fptr.payment()
		"""Регистрация итога чека"""
		fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, sale[4])
		fptr.receiptTotal()
		"""Закрытие полностью оплаченного чека"""
		fptr.closeReceipt()
	elif payment_type == 101:
		payment = 1
		bank = terminal_oplata(str(sale[4]))
		logger.warning("BANK: %s" % (bank))
		if bank == 1:
			fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_ELECTRONICALLY)
			fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sale[4])
			fptr.payment()
			"""Регистрация итога чека"""
			fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, sale[4])
			fptr.receiptTotal()
			"""Закрытие полностью оплаченного чека"""
			fptr.closeReceipt()
		else:
			logger.warning("Оплата по банковскому терминалу не прошла")
			windows.info_window("Оплата по банковскому терминалу не прошла", "")
	"""Допечатывание документа"""
	fptr.continuePrint()
	#! проверить распечатался ли документ
	while fptr.checkDocumentClosed() < 0:
		# Не удалось проверить состояние документа. Вывести пользователю текст ошибки, попросить устранить неполадку и повторить запрос
		windows.info_window("fptr.errorDescription:", str(fptr.errorDescription()))
		logger.warning("fptr.errorDescription: %s" % (fptr.errorDescription()))
		continue
	if not fptr.getParamBool(IFptr.LIBFPTR_PARAM_DOCUMENT_CLOSED):
		# Документ не закрылся. Требуется его отменить (если это чек) и сформировать заново
		windows.info_window("Кассовый документ не закрылся!", "")
		logger.warning("Кассовый документ не закрылся!")
		fptr.cancelReceipt()
		return
	if not fptr.getParamBool(IFptr.LIBFPTR_PARAM_DOCUMENT_PRINTED):
		# Можно сразу вызвать метод допечатывания документа, он завершится с ошибкой, если это невозможно
		while fptr.continuePrint() < 0:
			# Если не удалось допечатать документ - показать пользователю ошибку и попробовать еще раз.
			windows.info_window('Не удалось напечатать документ.\n Устраните неполадку и повторите.', str(fptr.errorDescription()))
			logger.warning('Не удалось напечатать документ. Устраните неполадку и повторите.' % (fptr.errorDescription()))
			continue_print()
			continue
	"""Оплата прошла, можно сохранять продажу"""
	if fptr.checkDocumentClosed() == 0:
		state = 1
	else:
		# Не удалось проверить состояние документа. Вывести пользователю текст ошибки, попросить устранить неполадку и повторить запрос
		windows.info_window('Не удалось напечатать документ (Ошибка "%s").\nУстраните неполадку и повторите.', str(fptr.errorDescription()))
		logger.info('Не удалось напечатать документ (Ошибка "%s"). Устраните неполадку и повторите.', fptr.errorDescription())
	fptr.close()
	print_slip_check()
	return state, payment


@logger_wraps()
def smena_close(user):
	"""Закрытие смены"""
	logger.info("Inside the function def smena_close")
	result = terminal_check_itog()
	try:
		if result == 1:
			fptr.open()
			fptr.setParam(1021, f'{user[0]} {user[1]}')
			fptr.setParam(1203, user[2])
			fptr.operatorLogin()
			fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_CLOSE_SHIFT)
			fptr.report()
			fptr.checkDocumentClosed()
			fptr.close()
	except FileNotFoundError as not_found:
		lines = 'File not found!'
		logger.info("File not found")
		windows.info_window('Сверка итогов по банковскому терминалу завершена неудачно.', str(lines))


def continue_print():
	"""Допечатать документ"""
	logger.info("Inside the function def continue_print")
	fptr.continuePrint()


@logger_wraps()
def terminal_check_itog_in_window():
	"""Сверка итогов работы дбанковского терминала с выводом результата в QMessageBox"""
	logger.info("Proverka file")
	pinpad_file = r"C:\sc552\p"
	subprocess.call('C:\\sc552\\loadparm.exe 7')
	logger.debug('Check itog in QMessageBox')
	"""Выводим результат сверки итогов"""
	try:
		with open(pinpad_file, encoding='IBM866') as file:
			lines = file.readlines()[2:]
			logger.info("Сверка итогов успешно завершена")
			windows.info_window('Сверка итогов по банковскому терминалу успешно завершена.', str(lines))
	except FileNotFoundError as not_found:
		lines = 'File not found!'
		logger.info("File not found")
		windows.info_window('Ошибка сверки итогов по банковскому терминалу!', str(lines))
