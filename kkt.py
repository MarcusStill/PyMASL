from libfptr10 import IFptr
from logger import *


fptr = IFptr('')


@logger_wraps()
def get_model():
	""""Запрос информации о модели ККТ"""
	logger.info("Inside the function def get_model_kkt")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_MODEL_INFO)
	fptr.queryData()
	print('модель: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_MODEL))
	print('Название: ', fptr.getParamString(IFptr.LIBFPTR_PARAM_MODEL_NAME))
	print('FirmwareVersion: ', fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION))
	fptr.close()


@logger_wraps()
def get_info():
	"""Запрос информации о ККТ"""
	logger.info("Inside the function def get_info")
	"""Заводской номер ККТ"""
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SERIAL_NUMBER)
	fptr.queryData()
	logger.info('Заводской номер ККТ: ', fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER))
	"""РН ККТ"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
	fptr.fnQueryData()
	logger.info('PH: ', fptr.getParamString(1037))
	"""Серийный номер ФН"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_FN_INFO)
	fptr.fnQueryData()
	logger.info('Серийный номер ФН: ', fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER))
	fptr.close()


@logger_wraps()
def get_status_obmena():
	"""Статус информационного обмена"""
	logger.info("Inside the function def get_status_obmena")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_OFD_EXCHANGE_STATUS)
	fptr.fnQueryData()
	logger.info('ExchangeStatus: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_OFD_EXCHANGE_STATUS))
	logger.info('UnsentCount: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENTS_COUNT))
	logger.info('FirstUnsentNumber: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER))
	logger.info('OfdMessageRead: ', fptr.getParamBool(IFptr.LIBFPTR_PARAM_OFD_MESSAGE_READ))
	logger.info('Date FN: ', fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME))
	fptr.close()

@logger_wraps()
def get_time():
	"""Запрос текущих даты и времени ККТ"""
	logger.info("Inside the function def get_time")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_DATE_TIME)
	fptr.queryData()
	logger.info('Текущие дата и время ККТ: ', fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME))
	fptr.close()


@logger_wraps()
def smena_info():
	"""Запрос состояния смены"""
	logger.info("Inside the function def smena_info")
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SHIFT_STATE)
	fptr.queryData()
	logger.info('Состояние смены: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_STATE))
	logger.info('Номер смены: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_NUMBER))
	logger.info('Текущие дата и время ККТ: ', fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME))
	fptr.beep()
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
def kassir_reg():
	"""Регистрация кассира"""
	logger.info("Inside the function def kassir_reg")
	fptr.open()
	fptr.setParam(1021, "Кассир Иванов И. И.")
	fptr.setParam(1203, "312329419227")
	fptr.operatorLogin()
	fptr.beep()
	fptr.close()


@logger_wraps()
def smena_open():
	"""Открытие смены"""
	logger.info("Inside the function def smena_open")
	fptr.open()
	fptr.setParam(1021, "Кассир Иванов И. И.")
	fptr.setParam(1203, "312329419227")
	fptr.operatorLogin()
	fptr.openShift()
	fptr.checkDocumentClosed()
	fptr.beep()
	fptr.close()


@logger_wraps()
def check_open():
	"""Открытие печатного чека"""
	logger.info("Inside the function def check_open")
	fptr.open()
	fptr.setParam(1021, "Кассир Иванов И. И.")
	fptr.setParam(1203, "312329419227")
	fptr.operatorLogin()
	fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL)
	fptr.openReceipt()
	"""Регистрация позиции с указанием суммы налога"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, "Товар")
	fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, 100)
	fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, 1)
	fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
	fptr.registration()
	"""Оплата чека"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH)
	fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, 100.00)
	fptr.payment()
	"""Регистрация налога на чек"""
	# fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
	# fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_SUM, 100.00)
	# fptr.receiptTax()
	"""Регистрация итога чека"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, 100.00)
	fptr.receiptTotal()
	"""Закрытие полностью оплаченного чека"""
	fptr.closeReceipt()
	"""Допечатывание документа"""
	fptr.continuePrint()
	fptr.close()


@logger_wraps()
def check_open_2(sale_tuple):
	logger.info("Inside the function def check_open_2")
	sale = sale_tuple
	state = 0
	"""Открытие печатного чека"""
	fptr.open()
	fptr.setParam(1021, "Кассир Иванов И. И.")
	fptr.setParam(1203, "312329419227")
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
	fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH)
	fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, sale[4])
	fptr.payment()
	"""Регистрация налога на чек"""
	# fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
	# fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_SUM, 100.00)
	# fptr.receiptTax()
	"""Регистрация итога чека"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, sale[4])
	fptr.receiptTotal()
	"""Закрытие полностью оплаченного чека"""
	fptr.closeReceipt()
	"""Допечатывание документа"""
	fptr.continuePrint()
	"""Оплата прошла, можно сохранять продажу"""
	if fptr.checkDocumentClosed() == 0:
		state = 1
	else:
		# Не удалось проверить состояние документа. Вывести пользователю текст ошибки, попросить устранить неполадку и повторить запрос
		print('Не удалось напечатать документ (Ошибка "%s"). Устраните неполадку и повторите.', fptr.errorDescription())
	fptr.close()
	return state


@logger_wraps()
def smena_close():
	"""Закрытие смены"""
	logger.info("Inside the function def smena_close")
	fptr.open()
	fptr.setParam(1021, "Кассир Иванов И. И.")
	fptr.setParam(1203, "312329419227")
	fptr.operatorLogin()
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_CLOSE_SHIFT)
	fptr.report()
	fptr.checkDocumentClosed()
	fptr.beep()
	fptr.close()


@logger_wraps()
def check_info():
	logger.info("Inside the function def check_info")
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_RECEIPT_STATE)
	fptr.queryData()

	receiptType = fptr.getParamInt(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE)
	receiptNumber = fptr.getParamInt(IFptr.LIBFPTR_PARAM_RECEIPT_NUMBER)
	documentNumber = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER)
	documentNumber = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER)
	sum = fptr.getParamDouble(IFptr.LIBFPTR_PARAM_RECEIPT_SUM)
	remainder = fptr.getParamDouble(IFptr.LIBFPTR_PARAM_REMAINDER)
	change = fptr.getParamDouble(IFptr.LIBFPTR_PARAM_CHANGE)


if __name__ == "__main__":
	fptr.open()
	fptr.enableOfdChannel()

	# fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_MODEL, str(IFptr.LIBFPTR_MODEL_ATOL_AUTO))
	# fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_USB))
	# fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_OFD_CHANNEL, str(IFptr.LIBFPTR_OFD_CHANNEL_AUTO))
	# fptr.applySingleSettings()


	#get_status_obmena()
	fptr.close()
	# last_document()
	# report_payment()
	# get_time()
	# smena_close()
	# kassir_reg()
	# smena_open()
	# smena_info()
	# check_open()
	#report_x()
	# # check_info()
	#smena_close()
	# # fptr.close()
