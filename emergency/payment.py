import logging
import subprocess

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from modules import windows
from modules.libfptr10 import IFptr
from modules.logger import logger

# Константы для работы с результатами терминала
TERMINAL_SUCCESS_CODE: int = 0
TERMINAL_USER_CANCEL_CODE: int = 2000
GOOD: str = "ОДОБРЕНО"

Card: int = 101

try:
    fptr = IFptr("")
except (Exception,) as e:
    info = "Не установлен драйвер ККТ!"
    windows.info_window(info, "", "")
    logger.warning(info)


# Настройка логирования
log_file = "application.log"

# Создание логгера
logger = logging.getLogger()
logger.setLevel(
    logging.DEBUG
)

# Создание обработчика для записи в файл
file_handler = logging.FileHandler(
    log_file, mode="a", encoding="utf-8"
)  # Открытие файла в режиме добавления
file_handler.setLevel(logging.DEBUG)

# Формат записи логов
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(file_handler)


def terminal_menu():
    """Вызов меню банковского терминала"""
    logger.info("Запуск функции terminal_menu")
    pinpad = "C:\\sc552\\loadparm.exe"
    pay_param = ["11"]
    pinpad_run = [pinpad] + pay_param  # объединяем путь и параметры в список
    proc = subprocess.run(
        pinpad_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    # Логирование вывода
    logger.info(f"stdout: {proc.stdout}")
    logger.error(f"stderr: {proc.stderr}")

    plat = proc.returncode
    logger.info(f"Статус проведения операции по банковскому терминалу: {plat}")


def read_slip_check():
    """Чтение слип-чека"""
    logger.info("Запуск функции read_slip_check")
    pinpad_file = r"C:\sc552\p"
    result = ""
    try:
        with open(pinpad_file, "r", encoding="IBM866") as file:
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


def print_slip_check(kol=2):
    """Печать слип-чека"""
    logger.info("Запуск функции print_slip_check")
    fptr.open()
    # Открытие нефискального документа
    fptr.beginNonfiscalDocument()
    line = read_slip_check()
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
        line = read_slip_check()
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


def terminal_oplata(amount):
    """Операуия оплаты по банковскому терминалу"""
    logger.info("Запуск функции terminal_oplata")
    result = ""
    status = 0
    amount_str = str(
        int(float(amount) * 100)
    )  # Преобразуем amount в 100-кратную сумму (например, 1.00 -> 100)

    pinpad = "C:\\sc552\\loadparm.exe"
    pay_param = ["1", amount_str]  # Формируем команду с параметрами
    pinpad_run = [
        pinpad
    ] + pay_param  # Формируем полный список для передачи в subprocess.run

    # command_run = f'command run: {" ".join(pinpad_run)}'
    # logger.info(command_run)  # Логируем команду как строку
    # проверяем статус проведения операции по банковскому терминалу
    while status != 1:
        # proc = subprocess.run(command_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        proc = subprocess.run(
            pinpad_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # Логирование вывода
        logger.info(f"stdout: {proc.stdout}")
        logger.error(f"stderr: {proc.stderr}")

        plat = proc.returncode
        logger.info(f"Статус проведения операции по банковскому терминалу: {plat}")
        if plat == TERMINAL_SUCCESS_CODE:
            # Операция успешна
            status = 1
        elif plat == TERMINAL_USER_CANCEL_CODE:
            logger.warning("Оплата отменена пользователем")
            result = 0
            status = 1  # Завершаем цикл и возвращаем ошибку
        else:
            # Произошла ошибка, предлагаем повторить операцию
            dialog = windows.info_dialog_window(
                "Внимание! Произошла ошибка при проведении платежа по банковской карте.",
                "Хотите повторить операцию?",
            )
            if dialog == 0:  # Пользователь выбрал "Нет"
                status = 1
    # Проверка файла с результатом работы банковского терминала
    logger.info("Proverka file")
    pinpad_file = r"C:\sc552\p"
    # Проверяем одобрение операции
    try:
        with open(pinpad_file, encoding="IBM866") as file:
            text = file.read()
        if GOOD in text:
            logger.info("Проверка файла успешно завершена")
            result = 1
    except FileNotFoundError as not_found:
        print("File not found:", not_found.filename)
        logger.warning("Проверка файла завершилась с ошибкой")
        result = 0
    return result


def operation_on_the_terminal(payment_type, type_operation, price):
    """Проведение операции по банковскому терминалу"""
    logger.info("Запуск функции operation_on_the_terminal")
    bank = None
    payment = None
    payment_type = Card
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

    return bank, payment


def process_payment():
    amount = amount_input.text().strip()
    if not amount or not amount.replace(".", "", 1).isdigit():
        QMessageBox.warning(window, "Ошибка", "Введите корректную сумму")
        return

    amount = float(amount)
    if amount <= 0:
        QMessageBox.warning(window, "Ошибка", "Сумма должна быть больше нуля")
        return

    payment_type = 101  # Оплата банковской картой
    bank, payment = operation_on_the_terminal(payment_type, 1, amount)

    if bank == 0:
        logging.error("Операция на терминале не прошла.")
        QMessageBox.critical(
            window, "Ошибка", "Операция оплаты не удалась. Повторите попытку."
        )
    elif bank == 1:
        logging.debug("Операция прошла успешно.")
        print_slip_check()
        QMessageBox.information(window, "Успех", f"Оплата {amount:.2f} прошла успешно!")


app = QApplication([])
window = QWidget()
window.setWindowTitle("Оплата")
window.setGeometry(100, 100, 300, 150)

layout = QVBoxLayout()
amount_input = QLineEdit()
amount_input.setPlaceholderText("Введите сумму")
layout.addWidget(amount_input)

pay_button = QPushButton("Оплатить")
pay_button.clicked.connect(
    process_payment
)  # Исправленный момент: передаем саму функцию
layout.addWidget(pay_button)

# Добавляем кнопку для вызова меню терминала
menu_button = QPushButton("Меню Терминала")
menu_button.clicked.connect(terminal_menu)
layout.addWidget(menu_button)

window.setLayout(layout)
window.show()
app.exec()
