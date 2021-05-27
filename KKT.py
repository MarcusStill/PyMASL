from libfptr10 import IFptr


fptr = IFptr('')


def get_model():
	print('- - - Zapros modely KKT - - -')
	#Запрос информации о модели ККТ
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_MODEL_INFO)
	fptr.queryData()
	print('Model:', fptr.getParamInt(IFptr.LIBFPTR_PARAM_MODEL))
	print('ModelName:', fptr.getParamString(IFptr.LIBFPTR_PARAM_MODEL_NAME))
	print('FirmwareVersion:', fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION))
	fptr.beep()


def get_info():
	print('- - - Zapros info KKT - - - ')
	# Заводской номер ККТ
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SERIAL_NUMBER)
	fptr.queryData()
	print('Zavodskoy nomer KKT:', fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER))
	# РН ККТ
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
	fptr.fnQueryData()
	print('PH:', fptr.getParamString(1037))
	# Серийный номер ФН
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_FN_INFO)
	fptr.fnQueryData()
	print('Seriyniy nomer FN:', fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER))
	fptr.beep()


def get_status_obmena():
	print('- - - Statys inf obmena - - - ')
	# Статус информационного обмена
	fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_OFD_EXCHANGE_STATUS)
	fptr.fnQueryData()
	print('exchangeStatus:', fptr.getParamInt(IFptr.LIBFPTR_PARAM_OFD_EXCHANGE_STATUS))
	print('unsentCount:', fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENTS_COUNT))
	print('firstUnsentNumber:', fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER))
	print('ofdMessageRead:', fptr.getParamBool(IFptr.LIBFPTR_PARAM_OFD_MESSAGE_READ))
	print('Date FN:', fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME))
	fptr.beep()

def get_time():
	print('- - - Date time KKT - - - ')
	#Запрос текущих даты и времени ККТ
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_DATE_TIME)
	fptr.queryData()
	# Тип переменной datetime - datetime.datetime
	#date_Time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
	print('Date_TIME KKT:', fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME))
	fptr.beep()


def smena_info():
	print('- - - Sostoyanie smeny - - - - - - ')
	#Запрос состояния смены
	fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_SHIFT_STATE)
	fptr.queryData()
	print('Smena state:', fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_STATE))
	print('Smena number:', fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_NUMBER))
	# Тип переменной datetime - datetime.datetime
	print('Date_TIME KKT:', fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME))


def last_document():
	#Копия последнего документа
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_LAST_DOCUMENT)
	fptr.report()	


def report_payment():
	#Отчет о состоянии расчетов
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_OFD_EXCHANGE_STATUS)
	fptr.report()

def report_x():
	#X-отчет
	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_X)
	fptr.report()

def kassir_reg():
	#Регистрация кассира
	fptr.setParam(1021, "Кассир Иванов И.")
	fptr.setParam(1203, "123456789047")
	fptr.operatorLogin()
	fptr.beep()


def smena_open():
	#Открытие смены
	fptr.setParam(1021, "Кассир Иванов И.")
	fptr.setParam(1203, "123456789047")
	fptr.operatorLogin()

	fptr.openShift()

	fptr.checkDocumentClosed()
	fptr.beep()


def check_open():
	#Открытие печатного чека
	fptr.setParam(1021, "Кассир Иванов И.")
	fptr.setParam(1203, "123456789047")
	fptr.operatorLogin()

	fptr.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, IFptr.LIBFPTR_RT_SELL)
	fptr.openReceipt()

	#Регистрация позиции с указанием суммы налога
	fptr.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, "Товар")
	fptr.setParam(IFptr.LIBFPTR_PARAM_PRICE, 100)
	fptr.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, 1)
	fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
	fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_SUM, 20)
	fptr.registration()

	#Оплата чека
	fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH)
	fptr.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, 100.00)
	fptr.payment()

	#Регистрация налога на чек
	fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, IFptr.LIBFPTR_TAX_VAT20)
	fptr.setParam(IFptr.LIBFPTR_PARAM_TAX_SUM, 100.00)
	fptr.receiptTax()

	#Регистрация итога чека
	fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, 100.00)
	fptr.receiptTotal()
	#Закрытие полностью оплаченного чека
	fptr.closeReceipt()

	#Допечатывание документа
	fptr.continuePrint()
	fptr.beep()

def smena_close():
	#Закрытие смены
	fptr.setParam(1021, "Кассир Иванов И.")
	fptr.setParam(1203, "123456789047")
	fptr.operatorLogin()

	fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_CLOSE_SHIFT)
	fptr.report()

	fptr.checkDocumentClosed()
	fptr.beep()


def main():
	# Подключение к устройству
	settings = {
	    IFptr.LIBFPTR_SETTING_MODEL: IFptr.LIBFPTR_MODEL_ATOL_AUTO,
	    IFptr.LIBFPTR_SETTING_PORT: str(IFptr.LIBFPTR_PORT_USB),
	    # IFptr.LIBFPTR_SETTING_COM_FILE: "COM6",
	    # IFptr.LIBFPTR_SETTING_BAUDRATE: IFptr.LIBFPTR_PORT_BR_115200
	}
	fptr.setSettings(settings)

	# IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_USB)

	# Открытие соединения с устройствомs
	fptr.open()
	get_model()
	get_info()
	#get_status_obmena()
	#get_time()
	#get_status_obmena()
	#smena_info()
	
	#last_document()
	#report_payment()
	#report_x()
	
	#kassir_reg()
	#smena_open()
	#check_open()

	# Закрытие соединения с устройством
	fptr.close()
	
if __name__ == '__main__':
	main()