from libfptr10 import IFptr


fptr = IFptr('')


def get_model():
	""""Запрос информации о модели ККТ"""
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_MODEL_INFO)
	fptr.queryData()
	print('модель: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_MODEL))
	print('Название: ', fptr.getParamString(IFptr.LIBFPTR_PARAM_MODEL_NAME))
	print('FirmwareVersion: ', fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION))
	fptr.close()


def get_info():
	"""Запрос информации о ККТ"""
	"""Заводской номер ККТ"""
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SERIAL_NUMBER)
	fptr.queryData()
	print('Заводской номер ККТ: ', fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER))
	"""РН ККТ"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
	fptr.fnQueryData()
	print('PH: ', fptr.getParamString(1037))
	"""Серийный номер ФН"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_FN_INFO)
	fptr.fnQueryData()
	print('Серийный номер ФН: ', fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER))
	fptr.close()

def get_status_obmena():
	"""Статус информационного обмена"""
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_OFD_EXCHANGE_STATUS)
	fptr.fnQueryData()
	print('ExchangeStatus: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_OFD_EXCHANGE_STATUS))
	print('UnsentCount: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENTS_COUNT))
	print('FirstUnsentNumber: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER))
	print('OfdMessageRead: ', fptr.getParamBool(IFptr.LIBFPTR_PARAM_OFD_MESSAGE_READ))
	print('Date FN: ', fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME))
	fptr.close()


def get_time():
	"""Запрос текущих даты и времени ККТ"""
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_DATE_TIME)
	fptr.queryData()
	print('Текущие дата и время ККТ: ', fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME))
	fptr.close()


def smena_info():
	"""Запрос состояния смены"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SHIFT_STATE)
	fptr.queryData()
	print('Состояние смены: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_STATE))
	print('Номер смены: ', fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_NUMBER))
	print('Текущие дата и время ККТ: ', fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME))


def last_document():
	"""Копия последнего документа"""
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_LAST_DOCUMENT)
	fptr.report()	
	fptr.close()

def report_payment():
	"""Отчет о состоянии расчетов"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_OFD_EXCHANGE_STATUS)
	fptr.report()

def report_x():
	"""X-отчет"""
	fptr.open()
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_X)
	fptr.report()
	fptr.slose()

def kassir_reg():
	"""Регистрация кассира"""
	fptr.setParam(1021, "Кассир Иванов И.")
	fptr.setParam(1203, "123456789047")
	fptr.operatorLogin()


def smena_open():
	"""Открытие смены"""
	fptr.setParam(1021, "Кассир Иванов И.")
	fptr.setParam(1203, "123456789047")
	fptr.operatorLogin()
	fptr.openShift()
	fptr.checkDocumentClosed()


def check_open():
	"""Открытие печатного чека"""
	fptr.setParam(1021, "Кассир Иванов И.")
	fptr.setParam(1203, "123456789047")
	fptr.operatorLogin()
	fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL)
	fptr.openReceipt()
	"""Регистрация позиции с указанием суммы налога"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, "Товар")
	fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, 100)
	fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, 1)
	fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
	fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_SUM, 20)
	fptr.registration()
	"""Оплата чека"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH)
	fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, 100.00)
	fptr.payment()
	"""Регистрация налога на чек"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
	fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_SUM, 100.00)
	fptr.receiptTax()
	"""Регистрация итога чека"""
	fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, 100.00)
	fptr.receiptTotal()
	"""Закрытие полностью оплаченного чека"""
	fptr.closeReceipt()
	"""Допечатывание документа"""
	fptr.continuePrint()


def smena_close():
	"""Закрытие смены"""
	fptr.open()
	fptr.setParam(1021, "Кассир Иванов И.")
	fptr.setParam(1203, "123456789047")
	fptr.operatorLogin()
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_CLOSE_SHIFT)
	fptr.report()
	fptr.checkDocumentClosed()
	fptr.close()
