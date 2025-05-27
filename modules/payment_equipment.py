import os
import subprocess
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional

from modules import windows
from modules.config import Config
from modules.libfptr10 import IFptr
from modules.logger import logger, logger_wraps

config = Config()

# Получаем параметр available
try:
    kkt_available = config.get("available") == 'on'
except (KeyError, ValueError):
    kkt_available = False
    logger.info("Параметр 'available' не найден в конфигурации, ККТ считается отключенным")

# Инициализация драйвера ККТ
try:
    if kkt_available:
        fptr = IFptr("")
    else:
        fptr = None
        logger.info("ККТ отключен в конфигурации (available ≠ on)")
except Exception as e:
    logger.warning(f"Не установлен драйвер ККТ: {str(e)}")
    kkt_available = False
    fptr = None


# Константы для работы с кодами терминала
TERMINAL_SUCCESS_CODE: int = 0
TERMINAL_USER_CANCEL_CODE: int = 2000
TERMINAL_USER_TIMEOUT: int = 2002
TERMINAL_DATA_EXCHANGE: set[int] = {4134, 4332}
TERMINAL_NO_MONEY: set[int] = {4451, 521}
TERMINAL_KLK: set[int] = {4120, 4122, 4123, 4124, 4128}
TERMINAL_CARD_BLOCKED: set[int] = {
    2004,
    2005,
    2006,
    2007,
    2405,
    2406,
    2407,
    574,
    579,
    705,
    706,
    707,
    572,
}
TERMINAL_CARD_LIMIT: set[int] = {4113, 4114}
TERMINAL_INVALID_CURRENCY_CODE: int = 4336
TERMINAL_NO_ADDRESS_TO_CONTACT: int = 4139
TERMINAL_ERROR_PIN_CODE: set[int] = {4117, 4137, 403, 405, 708, 709, 4455}
TERMINAL_LIMIT_OPERATION: set[int] = {4150, 4113, 4114}
TERMINAL_BIOMETRIC_ERROR: set[int] = {
    4160,
    4161,
    4162,
    4163,
    4164,
    4165,
    4166,
    4167,
    4168,
    4169,
    4171,
}
TERMINAL_NO_CONNECTION_BANK: set[int] = {4100, 4119}
TERMINAL_NEED_CASH_COLLECTION: set[int] = {4101, 4102, 4110, 4111, 4112}
TERMINAL_CARD_ERROR: set[int] = {
    444,
    507,
    4148,
    4149,
    4313,
    4314,
    4334,
    4339,
    5002,
    4302,
    4108,
    584,
    585,
    4125,
}
TERMINAL_OPERATION_CANCELED: int = 4132
TERMINAL_SERVER_ROUTINE_MAINTENANCE: set[int] = {3019, 3020, 3021}
TERMINAL_PIN_PAD_ERROR: set[int] = {
    99,
    362,
    363,
    364,
    518,
    4103,
    4104,
    4121,
    4130,
    4131,
    4136,
    4139,
    4143,
    4144,
    4145,
    4146,
    4146,
    4202,
    4203,
    4208,
    4209,
    4211,
    4300,
    4303,
    4305,
    4306,
    4309,
}
TERMINAL_COMMAND_ERROR: set[int] = {4139, 4140, 4141, 4142, 4301, 4335}
TERMINAL_QR_ERROR: int = 21069
TERMINAL_OPERATION_AMOUNT_ERROR: int = 4319
TERMINAL_SUPPORT: str = "0321"
APPROVE: str = "ОДОБРЕНО"
COINCIDENCE: str = "совпали"
EMAIL: str = "test.check@pymasl.ru"
PAYMENT_CASH = 102
PAYMENT_ELECTRONIC = 101
PAYMENT_OFFLINE = 100


@contextmanager
def fptr_connection(device):
    """Контекстный менеджер для управления подключением к ККМ (Кассовому аппаратному устройству).

    Параметры:
        device (object): Объект устройства (например, кассового аппарата или фискального принтера),
                         который должен поддерживать методы `open()` и `close()` для открытия и закрытия соединения.

    Возвращаемое значение:
        object: Возвращает объект `device`, переданный в функцию. Этот объект доступен внутри блока `with`.
    """
    if not kkt_available or device is None:
        logger.debug("ККТ не доступен, пропускаем подключение")
        yield None
        return

    device.open()
    try:
        yield device  # передаем fptr внутрь контекста
    finally:
        device.close()


def run_terminal_command(command_params: str, timeout: int = 120):
    """
    Выполняет команду на терминале и возвращает результат выполнения.

    Параметры:
        command_params (str): Параметры команды, которую необходимо выполнить.
        timeout (int): Таймаут в секундах, по истечении которого команда будет принудительно завершена.

    Возвращаемое значение:
        subprocess.CompletedProcess или None:
            - Возвращает объект `subprocess.CompletedProcess`, если команда выполнена успешно.
            - Возвращает `None`, если произошла ошибка выполнения команды.
    """
    logger.info("Запуск функции run_terminal_command")
    logger.debug(f"Переданные в функцию параметры: {command_params}")
    pinpad_path: str = config.get("pinpad_path")  # Путь к директории
    pinpad_file: str = "loadparm.exe"  # Имя файла
    # Полный путь до исполняемого файла
    pinpad_run_path = os.path.join(pinpad_path, pinpad_file)
    pinpad_run: str = f"{pinpad_run_path} {command_params}"

    if not os.path.isfile(pinpad_run_path):
        logger.error(f"Файл не найден: {pinpad_run_path}")
        raise FileNotFoundError(f"Файл не найден: {pinpad_run_path}")

    logger.info(f"Запуск команды: {pinpad_run}")
    try:
        process = subprocess.Popen(
            pinpad_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True  # Важно для строки команды
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            logger.warning(f"Процесс превысил таймаут {timeout} секунд. Завершается автоматически.")
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Процесс не завершился после terminate(). Используется kill().")
                process.kill()
                stdout, stderr = process.communicate()

        return subprocess.CompletedProcess(
            args=pinpad_run, returncode=process.returncode, stdout=stdout, stderr=stderr
        )
    except subprocess.SubprocessError as e:
        logger.error(f"Ошибка выполнения команды: {e}")
        return None


def check_terminal_file(word: str):
    """Проверка файла с результатом работы терминала.

    Параметры:
        word (str):
            Ожидаемое слово или текст, который необходимо найти в файле.

    Возвращаемое значение:
        bool:
            - Возвращает True, если ожидаемое слово найдено в файле.
            - Возвращает False, если слово не найдено или файл не существует.
    """
    logger.info("Запуск функции check_terminal_file")
    pinpad_path = config.get("pinpad_path")  # Передаем ключ "pinpad_path"
    pinpad_file = os.path.join(pinpad_path, "p")
    try:
        with open(pinpad_file, encoding="IBM866") as file:
            text = file.read()
        if word in text:
            logger.info("Проверка файла успешно завершена")
            return True
        else:
            logger.warning(f'Ожидаемый текст "{word}" не найден.')
            return False
    except FileNotFoundError as not_found:
        logger.error(f"Файл {pinpad_file} не найден: {not_found}")
        return False
    except UnicodeDecodeError as decode_error:
        logger.error(f"Ошибка декодирования файла {pinpad_file}: {decode_error}")
        return False


@logger_wraps()
def process_success_result():
    """Обработка успешного результата работы терминала.

    Функция проверяет наличие и корректность файла подтверждения транзакции,
    созданного терминалом.

    Возвращаемое значение:
        int:
            - Возвращает 1, если файл подтверждения существует и валиден.
            - Возвращает 0, если файл отсутствует, поврежден, либо возникла ошибка.
    """
    logger.info("Запуск функции process_success_result")
    try:
        if check_terminal_file(APPROVE):
            return 1
        else:
            logger.error("Файл подтверждения транзакции отсутствует или поврежден.")
    except FileNotFoundError as not_found:
        logger.error(f"Файл подтверждения транзакции не найден: {not_found}")
    return 0


@logger_wraps()
def handle_error(code, title, message, error_callback=None):
    """Универсальная обработка ошибок терминала.

    Параметры:
        code (int): Код ошибки
        title (str): Заголовок ошибки
        message (str): Текст ошибки
        error_callback (callable): Функция для обработки ошибки (title, message, code)
    """
    logger.warning(f"{title}: {message} (Код: {code})")

    # Явная проверка что callback передан и вызывается
    if error_callback is not None:
        logger.debug(f"Вызываю callback: {error_callback}")
        try:
            error_callback(title, message, code)
            return
        except Exception as e:
            logger.error(f"Ошибка в callback: {e}")

    # Fallback на GUI
    if hasattr(windows, 'info_window'):
        windows.info_window(title, message, f"Код: {code}")


@logger_wraps()
def process_terminal_error(returncode, error_callback=None):
    """Обработка ошибок терминала на основе возвращенного кода.

    Функция анализирует код возврата от терминала, выполняет соответствующую
    обработку ошибки и отображает информацию об ошибке пользователю.

    Параметры:
        returncode (int):
            Код возврата, полученный от терминала.
        error_callback (callable):
            Функция для обработки ошибки (title: str, message: str, code: int)

    Возвращаемое значение:
        int:
            - Возвращает 0 для всех обработанных ошибок.
            - Всегда возвращает 0, так как функция предназначена для обработки ошибок.
    """
    logger.info("Запуск функции process_terminal_error")
    logger.debug(f"Получен callback: {error_callback}")
    error_handlers = {
        TERMINAL_USER_CANCEL_CODE: (
            "Оплата отменена пользователем",
            f"Оплата отменена пользователем. Код возврата: {returncode}."
        ),
        TERMINAL_USER_TIMEOUT: (
            "Слишком долгий ввод ПИН-кода",
            f"Слишком долгий ввод ПИН-кода. Код возврата: {returncode}."
        ),
        TERMINAL_INVALID_CURRENCY_CODE: (
            "Указан неверный код валюты",
            f"Указан неверный код валюты. Обратитесь в банк. Телефон поддержки {TERMINAL_SUPPORT}. Код: {returncode}."
        ),
        TERMINAL_NO_ADDRESS_TO_CONTACT: (
            "Терминал потерял связь с банком",
            f"Терминал потерял связь с банком. Обратитесь в банк для выяснения причины. Телефон. тех.поддержки {TERMINAL_SUPPORT}. Код возврата: {returncode}.",
        ),
        TERMINAL_OPERATION_CANCELED: (
            "Операция отменена",
            f"Ошибка возникает тогда, когда карту достают из терминала быстрее, чем пройдет оплата. Необходимо повторить операцию.",
        ),
        TERMINAL_QR_ERROR: (
            "Ошибка операции по QR-коду",
            f"Необходимо провести возврат при помощи банковской карты. Если была попытка проведения операции оплаты, \n"
            f"то следует обратиться в банк для выяснения причины. Телефон. тех.поддержки {TERMINAL_SUPPORT}. Код возврата: {returncode}. ",
        ),
        TERMINAL_OPERATION_AMOUNT_ERROR: (
            "Ошибка в сумме операции",
            f"Сумма не должна превышать 42 млн. \n"
            f"Проведите операцию на меньшую сумму или уменьшите количество товара. Код возврата: {returncode}. ",
        ),
    }

    if returncode in TERMINAL_CARD_BLOCKED:
        handle_error(
            returncode,
            "Карта клиента заблокирована",
            f"Карта клиента заблокирована. Попробуйте произвести оплату другой картой или обратитесь в банк для выяснения причины.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_CARD_LIMIT:
        handle_error(
            returncode,
            "Превышен лимит операций",
            "Превышен лимит операций. Попробуйте произвести оплату другой картой или обратитесь в банк для выяснения причины.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_BIOMETRIC_ERROR:
        handle_error(
            returncode,
            "Ошибка в работе с биометрическими данными",
            f"Ошибка в работе с биометрическими данными. Обратитесь в банк для выяснения причины. Телефон. тех.поддержки {TERMINAL_SUPPORT}. Код возврата: {returncode}.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_ERROR_PIN_CODE:
        handle_error(
            returncode,
            "Ошибка при вводе ПИН-кода",
            "ПИН-код не был введен, либо введен неверно, либо вводимый ПИН-код заблокирован. Попробуйте повторить операцию оплаты.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_NO_CONNECTION_BANK:
        handle_error(
            returncode,
            "Нет связи с банком",
            f"Попробуйте повторить операцию через пару минут. При повторении ошибки необходимо обратиться в службу поддержки. Телефон. тех.поддержки {TERMINAL_SUPPORT}. Код возврата: {returncode}.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_NEED_CASH_COLLECTION:
        handle_error(
            returncode,
            "Необходимо произвести инкассацию",
            f"Необходимо произвести инкассацию. Обратитесь в службу поддержки. Телефон. тех.поддержки {TERMINAL_SUPPORT}. Код возврата: {returncode}.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_LIMIT_OPERATION:
        handle_error(
            returncode,
            "Превышен лимит операций",
            f"Превышен лимит операций. Обратитесь в службу поддержки. Телефон. тех.поддержки {TERMINAL_SUPPORT}. Код возврата: {returncode}.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_DATA_EXCHANGE:
        handle_error(
            returncode,
            "Требуется сделать сверку итогов",
            "Требуется сделать сверку итогов и повторить операцию.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_KLK:
        handle_error(
            returncode,
            "Ошибка в работе терминала",
            f"Необходимо обратиться в службу поддержки банка. Телефон тех.поддержки {TERMINAL_SUPPORT}. Код возврата: {returncode}.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_CARD_ERROR:
        handle_error(
            returncode,
            "Операцию невозможно выполнить для этой карты",
            f"Необходимо повторить попытку. Если проблема сохраняется – использовать другую карту. Код возврата: {returncode}.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_SERVER_ROUTINE_MAINTENANCE:
        handle_error(
            returncode,
            "Сервера Сбербанка недоступны",
            f"Сервера Сбербанка находятся на обслуживании/ремонте/регламентных работах. Попробуйте повторить операцию позже. Если проблема сохраняется - обратитесь в службу поддержки. Телефон тех.поддержки {TERMINAL_SUPPORT}.Код возврата: {returncode}.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_NO_MONEY:
        handle_error(
            returncode,
            "Недостаточно средств на карте",
            f"Недостаточно средств на карте. Попробуйте произвести оплату другой картой.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_COMMAND_ERROR:
        handle_error(
            returncode,
            "Нет нужного варианта связи для операции",
            f"Нет нужного варианта связи для операции. Обратитесь в службу поддержки ПО. Код возврата: {returncode}.",
            error_callback
        )
        return 0
    if returncode in TERMINAL_PIN_PAD_ERROR:
        handle_error(
            returncode,
            "Проблема в работе ПИН-пада.",
            f"Необходимо обратиться в службу поддержки банка. Телефон тех.поддержки {TERMINAL_SUPPORT}. Код возврата: {returncode}.",
            error_callback
        )
        return 0
    # Общие ошибки
    if returncode in error_handlers:
        title, message = error_handlers[returncode]
        logger.debug(f"Передаю callback в handle_error: {error_callback}")
        # Явно передаём как позиционный аргумент
        handle_error(returncode, title, message, error_callback)
        return 0

    # Неизвестный код
    logger.error(f"Неизвестный код возврата: {returncode}")
    handle_error(
        returncode,
        "Ошибка терминала",
        f"Возвращен неизвестный код ошибки. Обратитесь в службу поддержки. Телефон тех.поддержки {TERMINAL_SUPPORT}. Код возврата: {returncode}.",
        error_callback
    )
    return 0


@logger_wraps()
def terminal_oplata(amount: float) -> int:
    """
    Выполняет операцию оплаты через терминал.

    Параметры:
        amount (float): Сумма операции в рублях.

    Возвращаемое значение:
        int: 1 — успех, 0 — ошибка.
    """
    return process_terminal_transaction("1", amount, "Оплата")


@logger_wraps()
def terminal_return(amount: float) -> int:
    """
    Выполняет операцию возврата через терминал.

    Параметры:
        amount (float): Сумма возврата в рублях.

    Возвращаемое значение:
        int: 1 — успех, 0 — ошибка.
    """
    return process_terminal_transaction("3", amount, "Возврат")


@logger_wraps()
def terminal_canceling(amount: float) -> int:
    """
    Выполняет операцию отмены через терминал.

    Параметры:
        amount (float): Сумма операции отмены в рублях.

    Возвращаемое значение:
        int: 1 — успех, 0 — ошибка.
    """
    return process_terminal_transaction("8", amount, "Отмена")

@logger_wraps()
def process_terminal_transaction(command_code: str, amount: float, operation_name: str, error_callback=None) -> int:
    """
    Обрабатывает операцию на банковском терминале.

    Параметры:
        command_code (str): Код команды терминала (например, "1" — оплата, "3" — возврат, "8" — отмена).
        amount (float): Сумма операции в рублях.
        operation_name (str): Название операции для логирования.

    Возвращаемое значение:
        int: 1 — успех, 0 — ошибка.
    """
    logger.info(f"Запуск операции: {operation_name}")
    logger.debug(f"Переданная сумма: {amount}")

    # Преобразуем сумму в формат копеек (например, 150.00 → "15000")
    command = f"{command_code} {int(amount * 100)}"
    result = run_terminal_command(command)

    if result is None:
        logger.error(f"Ошибка при выполнении команды терминала: {command}")
        handle_error(
            f"Нет ответа от терминала",
            f"{operation_name} не была выполнена. Проверьте устройство.",
            "Код ошибки: отсутствует",
            error_callback=error_callback
        )
        return 0

    logger.info(f"Код возврата от терминала ({operation_name}): {result.returncode}")

    if result.returncode == TERMINAL_SUCCESS_CODE:
        return process_success_result()

    if result.returncode != TERMINAL_SUCCESS_CODE:
        process_terminal_error(result.returncode, error_callback)
        return 0

    # Логируем stderr, если есть
    if result.stderr:
        try:
            err_output = result.stderr.decode("cp1251", errors="ignore").strip()
        except Exception:
            err_output = str(result.stderr)
        logger.error(f"Терминал вернул ошибку: {err_output}")

    return process_terminal_error(result.returncode)


def universal_terminal_operation(payment_type: int, amount: float, progress_signal, error_callback=None) -> tuple[int, int]:
    """
    Универсальный обработчик терминальных операций для оплаты или возврата.

    Параметры:
        payment_type (int): Тип оплаты (например, 1 — карта, 3 — оффлайн).
        amount (float): Сумма операции в рублях.
        progress_signal: Сигнал для обновления статуса прогресса.

    Возвращаемое значение:
        tuple:
            - bank (int): Результат операции по терминалу (1 — успех, 0 — ошибка).
            - payment_code (int): Код оплаты (1 — карта, 3 — оффлайн).
    """
    try:
        if payment_type == PAYMENT_ELECTRONIC:
            logger.info("Запускаем оплату по банковскому терминалу")
            progress_signal.emit("Запускаем оплату по банковскому терминалу...", 35)
            bank = process_terminal_transaction("1", amount, "Оплата", error_callback)
            if bank == 1:
                progress_signal.emit("Оплата успешна.", 45)
                return (bank, 1)  # bank, 1 — card
            elif bank == 0:
                progress_signal.emit("Ошибка оплаты.", 100)
                return 0, 1  # 0 — error, 1 — card
        elif payment_type == PAYMENT_OFFLINE:
            logger.info("Запускаем offline оплату по банковскому терминалу")
            progress_signal.emit("Запускаем offline оплату по банковскому терминалу...", 35)
            return 1, 3  # 1 — success, 3 — offline

        # Явный return, если ни одно из условий не выполнено
        progress_signal.emit("Неподдерживаемый тип оплаты", 100)
        return 0, 0
    except ValueError as ve:
        logger.error(f"Ошибка: {ve}")
        progress_signal.emit(f"Ошибка: {str(ve)}", 100)
        return 0, 0
    except Exception as exp:
        logger.error(f"Неизвестная ошибка при проведении операции: {exp}")
        progress_signal.emit(f"Неизвестная ошибка при проведении операции: {str(exp)}", 100)
        return 0, 0


@logger_wraps()
def terminal_check_itog():
    """Сверка итогов работы банковского терминала.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        int:
            - Возвращает 1, если сверка итогов завершена успешно.
            - Возвращает 0, если файл не найден.
    """
    logger.info("Запуск функции terminal_check_itog")
    result = run_terminal_command("7")
    logger.debug(f"Терминал вернул следующий код операции: {result}")
    if result is None:
        logger.error("Ошибка при выполнении команды терминала")
        return 0
    if result.returncode == TERMINAL_SUCCESS_CODE:
        try:
            return 1 if check_terminal_file(COINCIDENCE) else 0
        except FileNotFoundError as not_found:
            logger.error(f"Файл не найден: {not_found}")
            return 0
    else:
        logger.error(f"Неизвестный код возврата: {result.returncode}")
        return 0


def terminal_menu():
    """Вызов меню банковского терминала.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, просто вызывает команду терминала.
    """
    logger.info("Запуск функции terminal_menu")
    run_terminal_command("11")


def terminal_check_itog_window():
    """Сверка итогов работы банковского терминала с выводом результата в QMessageBox.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, просто выводит информацию в окно.
    """
    logger.info("Запуск функции terminal_check_itog_window")
    result = run_terminal_command("7")
    if result is None:
        logger.error("Ошибка при выполнении команды терминала")
        windows.info_window(
            "Ошибка выполнения команды терминала", "", "Команда не выполнена"
        )
        return
    if result.returncode == TERMINAL_SUCCESS_CODE:
        try:
            info = read_pinpad_file()
            logger.info("Сверка итогов завершена")
            windows.info_window("Смотрите подробную информацию.", "", info)
        except FileNotFoundError as not_found:
            logger.warning(f"Файл не найден: {not_found}")
            windows.info_window(
                "Ошибка сверки итогов по банковскому терминалу!", "", str(not_found)
            )
    else:
        logger.error(f"Неизвестный код возврата: {result.returncode}")
        windows.info_window(
            "Ошибка выполнения команды терминала",
            "",
            f"Неизвестный код возврата: {result.returncode}",
        )


@logger_wraps()
def terminal_svod_check():
    """Сводный чек без детализации.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, просто вызывает команду терминала.
    """
    logger.info("Запуск функции terminal_svod_check")
    run_terminal_command("9")
    try:
        print_pinpad_check(1)
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def terminal_control_lenta():
    """Печать контрольной ленты.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, просто вызывает команду терминала.
    """
    logger.info("Запуск функции terminal_control_lenta")
    result = run_terminal_command("9 1")
    if result is None:
        logger.error("Ошибка при выполнении команды терминала")
        return
    if result.returncode == TERMINAL_SUCCESS_CODE:
        try:
            print_pinpad_check(1)
        except FileNotFoundError as not_found:
            logger.warning(f"Файл не найден: {not_found.filename}")
    else:
        logger.error(f"Неизвестный код возврата: {result.returncode}")


@logger_wraps()
def terminal_print_file():
    """Печать файла-отчета.

    Параметры:
        None:
            Функция не принимает параметров.
    Возвращаемое значение:
        None:
            Функция не возвращает значений, просто вызывает команду терминала.
    """
    logger.info("Запуск функции terminal_print_file")
    try:
        print_pinpad_check(1)
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def terminal_file_in_window():
    """Показ банковского слип-чека в информационном окне.

    Параметры:
        None:
            Функция не принимает параметров.
    Возвращаемое значение:
        None:
            Функция не возвращает значений, просто выводит информацию в окно.
    """
    logger.info("Запуск функции terminal_file_in_window")
    try:
        print_pinpad_check(1)
    except FileNotFoundError as not_found:
        logger.warning(f"Файл не найден: {not_found.filename}")
    windows.info_window("Смотрите подробную информацию.", "FileNotFoundError", "")


@logger_wraps()
def terminal_copy_last_check():
    """Печать копии последнего чека.

    Параметры:
        None:
            Функция не принимает параметров.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но может вызывать исключения в случае ошибок.
    """
    logger.info("Запуск функции terminal_copy_last_check")
    result = run_terminal_command("12")
    if result is None:
        logger.error("Ошибка при выполнении команды терминала")
        return
    if result.returncode == TERMINAL_SUCCESS_CODE:
        try:
            print_pinpad_check(1)
        except FileNotFoundError as not_found:
            logger.warning(f"Файл не найден: {not_found.filename}")
    else:
        logger.error(f"Неизвестный код возврата: {result.returncode}")


@logger_wraps()
def read_pinpad_file(remove_newline=True):
    """Чтение банковского чека с опциональным удалением переноса строки.

    Параметры:
        remove_newline (bool):
            Этот параметр определяет, нужно ли удалять символы новой строки при чтении файла.

    Возвращаемое значение:
        str или None:
            - Возвращает содержимое файла как строку, если файл успешно прочитан.
            - Возвращает None, если файл не найден или конфигурация не загружена.
    """
    logger.info("Запуск функции read_pinpad_file")
    pinpad_path = config.get("pinpad_path")
    if not pinpad_path:
        logger.error("Конфигурация не загружена")
        return None
    pinpad_file = os.path.join(pinpad_path, "p")
    result_lines: list[str] = []
    try:
        with open(pinpad_file, "r", encoding="IBM866") as file:
            for line in file:
                # Убираем символ новой строки, если параметр remove_newline=True
                line: str = line.rstrip() if remove_newline else line
                result_lines.append(line)
                print_text(line)
    except FileNotFoundError as not_found:
        logger.warning("Файл не найден: %s", not_found.filename)
        return None
    except UnicodeDecodeError as decode_error:
        logger.error("Ошибка декодирования файла: %s", decode_error)
        return None
    return "".join(result_lines)


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
    with fptr_connection(fptr):
        try:
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
        except FileNotFoundError as not_found:
            logger.error(f"Файл не найден: {not_found.filename}")
        except Exception as e:
            logger.error(f"Ошибка при печати слип-чека: {e}")


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
        try:
            with fptr_connection(fptr):
                fptr.beginNonfiscalDocument()

                # Читаем чек из файла
                line = read_pinpad_file(remove_newline=False)
                if not line:
                    raise ValueError("Файл с чеком пуст или не может быть прочитан.")
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
        except Exception as e:
            logger.error(f"Ошибка при печати слип-чека: {e}")
            # Информируем пользователя о проблемах с печатью
            windows.info_window(
                "Ошибка при печати слип-чека.",
                "Пожалуйста, проверьте принтер и повторите попытку.",
                str(e),
            )
            break  # Останавливаем выполнение функции после ошибки

        count -= 1

def get_info(hide: bool = False) -> Optional[int]:
    """
    Запрос информации о ККТ.
    Запрашивает информацию о кассовом аппарате (модель, наименование и версия ПО).
    Если параметр `hide` равен `False`, отображает полученную информацию в окне приложения.
    Возвращает номер модели ККТ или `None`, если не удалось получить информацию.

    Параметры:
        hide: bool (по умолчанию False)
            Если `True`, информация о ККТ не отображается в окне, а только возвращается как результат выполнения.
            Если `False`, информация будет показана в интерфейсе.

    Возвращаемое значение:
        Optional[int]: Возвращает номер модели ККТ (если информация получена), или `None`, если не удалось получить данные.
    """
    if not kkt_available or fptr is None:
        logger.warning("ККТ отключен или не инициализирован.")
        return None
    try:
        with fptr_connection(fptr) as f:
            if not f:
                logger.warning("Не удалось подключиться к ККТ.")
                return None
            f.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_MODEL_INFO)
            f.queryData()
            model = f.getParamInt(IFptr.LIBFPTR_PARAM_MODEL)
            model_name = f.getParamString(IFptr.LIBFPTR_PARAM_MODEL_NAME)
            firmware_version = f.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)

        if not hide:
            info = f"Номер модели ККТ: {model}.\nНаименование ККТ: {model_name}.\nВерсия ПО ККТ: {firmware_version}"
            windows.info_window("Смотрите подробную информацию.", "", info)
        return model
    except (ConnectionError, AttributeError) as e:
        logger.error(f"Ошибка при получении данных о ККТ: {e}")
        windows.info_window("Ошибка", "Не удалось получить данные о ККТ.", "Проверьте настройки устройства.")
        return None
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        windows.info_window("Ошибка", "Произошла неизвестная ошибка.", "Попробуйте снова.")
        return None

def is_kkt_connected() -> bool:
    """
    Проверка физического подключения ККТ.
    Проверяет, подключен ли кассовый аппарат и доступен ли для взаимодействия.
    Возвращает `True`, если ККТ подключен, и `False`, если нет.

    Параметры:
        None

    Возвращаемое значение:
        bool: Возвращает `True`, если кассовый аппарат подключен и доступен для работы, иначе `False`.
    """
    if not kkt_available or fptr is None:
        return False
    try:
        with fptr_connection(fptr) as f:
            if f:
                f.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_STATUS)
                f.queryData()
                return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке подключения ККТ: {e}")
        return False

@logger_wraps()
def get_last_document(day: int = 7) -> None:
    """Запрос информации о последнем чеке в ФН и проверка даты.

    Параметры:
        day (int): Количество дней простоя кассового аппарата, после которого рекомендуется сделать обмен данными

    Возвращаемое значение:
        None: Функция не возвращает значений, только показывает сообщения об ошибках
    """
    logger.info("Запуск функции get_last_document")
    # Проверяем доступность ККТ из конфигурации
    if not kkt_available:
        return
    try:
        last_check = get_last_document_datetime()
        check_stale_document(last_check, day)
    except (ConnectionError, AttributeError) as e:
        logger.error(f"Ошибка при работе с ККТ: {e}")
        windows.info_window(
            "Ошибка", "Не удалось получить данные от ККТ.", "Проверьте подключение и настройки."
        )
    except Exception as e:
        logger.exception(f"Неизвестная ошибка в get_last_document: {e}")
        windows.info_window(
            "Ошибка", "Произошла неизвестная ошибка.", "Попробуйте снова."
        )

def get_last_document_datetime() -> datetime:
    """ Получает дату и время последнего зарегистрированного чека из фискального накопителя.

    Возвращаемое значение:
        datetime: Дата и время последнего документа в фискальном накопителе.

    Исключения:
        Генерирует исключение в случае ошибки соединения или некорректной работы оборудования.
    """
    logger.info("Запуск функции get_last_document_datetime")
    with fptr_connection(fptr):
        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_LAST_DOCUMENT)
        fptr.fnQueryData()
        last_check_datetime: datetime = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)

        return last_check_datetime

def check_stale_document(last_check: datetime, max_days: int = 7) -> None:
    """
    Проверяет, не превышает ли возраст последнего чека заданное количество дней.

    Параметры:
        last_check (datetime): Дата и время последнего зарегистрированного чека.
        max_days (int): Максимально допустимое количество дней с момента последнего чека (по умолчанию 7).

    Действие:
        Если разница между текущей датой и датой последнего чека больше max_days,
        отображается предупреждающее окно с рекомендацией провести сверку итогов.
    """
    logger.info("Запуск функции check_stale_document")
    current_date = datetime.now()
    if (current_date - last_check) <= timedelta(days=max_days):
        # Ранний выход, если чек не старый
        return
    info = f"Дата и время последнего чека в ФН: {last_check.strftime('%Y-%m-%d %H:%M:%S')}"
    windows.info_window(
        "Внимание",
        "Дата последнего документа, записанного в фискальном накопителе, старше 7 дней.\n\n"
        "Для корректного проведения платежей по банковскому терминалу "
        "необходимо сделать сверку итогов (вкладка \"Касса\" -> \"Сверка итогов\").\n",
        info
    )


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
    try:
        with fptr_connection(fptr):
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

        info = (
            f"Статус информационного обмена с ОФД: {exchange_status}.\n"
            f"Количество неотправленных документов: {unsent_count}.\n"
            f"Номер первого неотправленного документа: {first_unsent_number}.\n"
            f"Дата и время первого неотправленного документа: {date_time}.\n"
            f"Флаг наличия сообщения для ОФД: {ofd_message_read}.\n"
            f"Дата и время последнего успешного ОКП: {okp_time}."
        )
        windows.info_dialog_window("Смотрите подробную информацию.", info)
    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к ККТ: {ce}")
        windows.info_dialog_window(
            "Ошибка", "Не удалось подключиться к ККТ. Проверьте соединение."
        )
    except AttributeError as ae:
        logger.error(f"Ошибка при получении данных о статусе обмена: {ae}")
        windows.info_dialog_window(
            "Ошибка", "Не удалось получить данные о статусе обмена."
        )
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        windows.info_dialog_window(
            "Ошибка", "Произошла неизвестная ошибка при запросе статуса обмена."
        )


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
    try:
        with fptr_connection(fptr):
            fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_DATE_TIME)
            fptr.queryData()
            # Тип переменной datetime - datetime.datetime
            date_time = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)
        logger.debug(f"Текущие дата и время в ККТ: {date_time}")
        windows.info_window(str(date_time), "", "")
    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к ККТ: {ce}")
        windows.info_window(
            "Ошибка", "Не удалось подключиться к ККТ. Проверьте соединение.", ""
        )
    except AttributeError as ae:
        logger.error(f"Ошибка при получении данных времени: {ae}")
        windows.info_window("Ошибка", "Не удалось получить данные времени с ККТ.", "")

    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        windows.info_window(
            "Ошибка", "Произошла неизвестная ошибка при запросе времени.", ""
        )


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
    try:
        with fptr_connection(fptr):
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
        info = (
            f"Состояние смены: {result}.\n"
            f"Номер смены: {number}.\n"
            f"Дата и время истечения текущей смены: {date_time}"
        )
        windows.info_window(
            f"Состояние смены: {result}", "Смотрите подробную информацию.", info
        )
        return state

    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к ККТ: {ce}")
        windows.info_window(
            "Ошибка", "Не удалось подключиться к ККТ. Проверьте соединение.", ""
        )
        return -1

    except AttributeError as ae:
        logger.error(f"Ошибка при получении данных состояния смены: {ae}")
        windows.info_window(
            "Ошибка",
            "Не удалось получить состояние смены. Проверьте настройки ККТ.",
            "",
        )
        return -2

    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        windows.info_window(
            "Ошибка", "Произошла неизвестная ошибка при запросе состояния смены."
        )
        return -3


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
    try:
        with fptr_connection(fptr):
            fptr.setParam(
                IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_LAST_DOCUMENT
            )
            fptr.report()
    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к ККТ: {ce}")
        windows.info_window(
            "Ошибка", "Не удалось подключиться к ККТ. Проверьте соединение.", ""
        )
    except AttributeError as ae:
        logger.error(f"Ошибка при получении данных документа: {ae}")
        windows.info_window(
            "Ошибка",
            "Не удалось получить последний документ. Проверьте настройки ККТ.",
            "",
        )
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        windows.info_window(
            "Ошибка",
            "Произошла неизвестная ошибка при запросе последнего документа.",
            "",
        )


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
    try:
        with fptr_connection(fptr):
            fptr.setParam(
                IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_OFD_EXCHANGE_STATUS
            )
            fptr.report()
    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к фискальному принтеру: {ce}")
        windows.info_window(
            "Ошибка",
            "Не удалось подключиться к фискальному принтеру. Проверьте соединение.",
            "",
        )
    except AttributeError as ae:
        logger.error(f"Ошибка при выполнении отчета: {ae}")
        windows.info_window(
            "Ошибка",
            "Не удалось выполнить отчет. Проверьте настройки принтера или ОФД.",
            "",
        )
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        windows.info_window(
            "Ошибка",
            "Произошла неизвестная ошибка при попытке печати отчета о расчетах.",
            "",
        )


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
    try:
        with fptr_connection(fptr):
            fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_X)
            fptr.report()
    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к фискальному принтеру: {ce}")
        windows.info_window(
            "Ошибка",
            "Не удалось подключиться к фискальному принтеру. Проверьте соединение.",
            "",
        )
    except AttributeError as ae:
        logger.error(f"Ошибка при выполнении X-отчета: {ae}")
        windows.info_window(
            "Ошибка", "Не удалось выполнить X-отчет. Проверьте настройки принтера.", ""
        )
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        windows.info_window(
            "Ошибка", "Произошла неизвестная ошибка при печати X-отчета.", ""
        )


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
    try:
        with fptr_connection(fptr):
            # Параметры для регистрации кассира
            fptr.setParam(1021, f"{user.last_name} {user.first_name}")
            fptr.setParam(1203, user.inn)
            fptr.operatorLogin()
        logger.info(
            f"Кассир {user.last_name} {user.first_name} зарегистрирован успешно."
        )
    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к фискальному принтеру: {ce}")
        windows.info_window(
            "Ошибка",
            "Не удалось подключиться к фискальному принтеру. Проверьте соединение.",
            "",
        )
    except ValueError as ve:
        logger.error(f"Ошибка в данных пользователя: {ve}")
        windows.info_window(
            "Ошибка",
            "Некорректные данные пользователя. Проверьте фамилию, имя или ИНН.",
            "",
        )
    except Exception as e:
        logger.error(f"Неизвестная ошибка при регистрации кассира: {e}")
        windows.info_window(
            "Ошибка", "Произошла ошибка при регистрации кассира. Попробуйте снова.", ""
        )


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
    if amount <= 0:
        logger.error(
            f"Некорректная сумма для внесения: {amount}. Сумма должна быть положительной."
        )
        windows.info_window("Ошибка", "Сумма внесения должна быть положительной.")
        return
    try:
        with fptr_connection(fptr):
            fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, amount)
            fptr.cashIncome()
        logger.info(f"Сумма {amount} успешно внесена в кассу.")
    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к фискальному принтеру: {ce}")
        windows.info_window(
            "Ошибка",
            "Не удалось подключиться к фискальному принтеру. Проверьте соединение.",
            "",
        )
    except ValueError as ve:
        logger.error(f"Некорректное значение параметра: {ve}")
        windows.info_window(
            "Ошибка", "Некорректные данные для внесения. Проверьте введенную сумму.", ""
        )
    except Exception as e:
        logger.error(f"Неизвестная ошибка при внесении денег в кассу: {e}")
        windows.info_window(
            "Ошибка",
            "Произошла ошибка при внесении денег в кассу. Попробуйте снова.",
            "",
        )


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
    if amount <= 0:
        logger.error(
            f"Некорректная сумма для выплаты: {amount}. Сумма должна быть положительной."
        )
        windows.info_window("Ошибка", "Сумма выплаты должна быть положительной.", "")
        return
    try:
        with fptr_connection(fptr):
            fptr.setParam(IFptr.LIBFPTR_PARAM_SUM, amount)
            fptr.cashOutcome()

        logger.info(f"Сумма {amount} успешно выплачена из кассы.")
    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к фискальному принтеру: {ce}")
        windows.info_window(
            "Ошибка",
            "Не удалось подключиться к фискальному принтеру. Проверьте соединение.",
            "",
        )
    except ValueError as ve:
        logger.error(f"Некорректное значение параметра: {ve}")
        windows.info_window(
            "Ошибка", "Некорректные данные для выплаты. Проверьте введенную сумму.", ""
        )
    except Exception as e:
        logger.error(f"Неизвестная ошибка при выплате денег из кассы: {e}")
        windows.info_window(
            "Ошибка",
            "Произошла ошибка при выплате денег из кассы. Попробуйте снова.",
            "",
        )


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
    try:
        with fptr_connection(fptr):
            # Запрос баланса наличных денег
            fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_CASH_SUM)
            fptr.queryData()
            # Получаем баланс
            cashSum = fptr.getParamDouble(IFptr.LIBFPTR_PARAM_SUM)
            logger.info(f"Баланс наличных денег в кассе: {cashSum}")
            # Печать баланса
            fptr.beginNonfiscalDocument()
            fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, f"Баланс наличных денег: {cashSum}")
            fptr.printText()
            fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
            fptr.printText()  # Промотка на одну строку
            fptr.endNonfiscalDocument()
            fptr.report()
            fptr.setParam(IFptr.LIBFPTR_PARAM_CUT_TYPE, IFptr.LIBFPTR_CT_FULL)
            fptr.cut()
        return cashSum
    except ConnectionError as ce:
        # Ошибка подключения к фискальному принтеру
        logger.error(f"Ошибка подключения к фискальному принтеру: {ce}")
        windows.info_window(
            "Ошибка",
            "Не удалось подключиться к фискальному принтеру. Проверьте соединение.",
            "",
        )
    except ValueError as ve:
        # Ошибка при получении или обработке данных баланса
        logger.error(f"Ошибка при получении данных баланса: {ve}")
        windows.info_window(
            "Ошибка", "Не удалось получить баланс наличных средств.", ""
        )
    except Exception as e:
        # Общая ошибка
        logger.error(f"Неизвестная ошибка при проверке баланса: {e}")
        windows.info_window(
            "Ошибка", "Произошла ошибка при проверке баланса. Попробуйте снова.", ""
        )


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
    try:
        if payment_type == PAYMENT_ELECTRONIC:
            payment = 1
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
        elif payment_type == PAYMENT_OFFLINE:
            payment = 3
            # результат операции по терминалу
            logger.info("Запускаем offline оплату по банковскому терминалу")
            bank = 1
        else:
            raise ValueError(f"Неизвестный тип оплаты: {payment_type}")
        # Возвращаем результат
        return bank, payment
    except ValueError as ve:
        logger.error(f"Ошибка: {ve}")
        windows.info_window("Ошибка", f"Неверный тип операции или параметр: {ve}", "")
        return 0, 0
    except Exception as e:
        logger.error(f"Неизвестная ошибка при проведении операции: {e}")
        windows.info_window(
            "Ошибка", "Произошла ошибка при проведении операции. Попробуйте снова.", ""
        )
        return 0, 0


def register_item(device, name, price, quantity, tax_type=IFptr.LIBFPTR_TAX_VAT20):
    """Функция регистрирует товар в чеке с помощью переданных параметров: название, цена, количество и тип налога.

    Параметры:
        device (object): Объект устройства, поддерживающий метод `setParam()` для настройки параметров чека.
        name (str): Название товара, которое будет отображаться в чеке.
        price (float): Цена одного товара.
        quantity (int): Количество товара.
        tax_type (int, optional): Тип налога для товара (по умолчанию используется НДС 20%).

    Возвращаемое значение:
        None: Функция не возвращает значений, но выполняет регистрацию товара на устройстве.
    """
    logger.info("Запуск функции register_item")
    logger.info(f"В функцию переданы параметры: {name}, {price}, {quantity}")
    device.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, name)
    device.setParam(IFptr.LIBFPTR_PARAM_PRICE, price)
    device.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, quantity)
    device.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, tax_type)
    device.registration()


def setup_fptr(device, user, type_operation, print_check):
    """Функция настраивает параметры устройства для выполнения операции, включая данные оператора и тип чека.

    Параметры:
        device (object): Объект устройства, поддерживающий метод `setParam()` для настройки параметров чека.
        user (object): Объект пользователя с аттрибутами `last_name`, `first_name` и `inn`.
        type_operation (int): Тип операции. Может быть 1 (продажа), 2 (возврат) или 3 (другие операции).
        print_check (int): Флаг, указывающий, нужно ли печатать чек. Если 0, чек будет отправлен по электронной почте.

    Возвращаемое значение:
        None: Функция не возвращает значений, но выполняет настройку параметров устройства для проведения операции.

    """
    logger.info("Запуск функции setup_fptr")
    device.setParam(1021, f"{user.last_name} {user.first_name}")
    device.setParam(1203, user.inn)
    device.operatorLogin()
    receipt_types = {
        1: IFptr.LIBFPTR_RT_SELL,
        2: IFptr.LIBFPTR_RT_SELL_RETURN,
        3: IFptr.LIBFPTR_RT_SELL_RETURN,
    }
    device.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE, receipt_types.get(type_operation))
    if print_check == 0:
        device.setParam(IFptr.LIBFPTR_PARAM_RECEIPT_ELECTRONICALLY, True)
        device.setParam(1008, EMAIL)


def register_tickets(device, sale_dict, type_operation):
    """Функция регистрирует различные типы билетов (взрослые, детские, с акцией и без) в чеке на основе переданных данных.

    Параметры:
        device (object): Объект устройства, поддерживающий метод `setParam()` для настройки параметров чека.
        sale_dict (dict): Словарь, содержащий данные о продаже, включая количество и цену билетов.
        type_operation (int): Тип операции. Например, 1 для продажи, для других операций могут быть другие типы.

    Возвращаемое значение:
        None: Функция не возвращает значений, но выполняет регистрацию билетов в чеке.
    """
    logger.info("Запуск функции register_tickets")
    logger.debug(f"В функцию переданы: device = {device}, payment_type = {sale_dict}, type_operation = {type_operation}")
    if type_operation == 1:
        time = sale_dict["detail"][6]
        # Взрослые билеты
        kol_adult_edit = sale_dict["kol_adult"] - sale_dict["detail"][0]
        if kol_adult_edit > 0:  # Регистрация только если есть билеты
            register_item(
                device,
                f"Билет взрослый {time} ч.",
                sale_dict["price_adult"],
                kol_adult_edit,
            )
        # Взрослые билеты со скидкой
        if (
            sale_dict["detail"][0] > 0
            and sale_dict["detail"][1] > 0
            and sale_dict["kol_adult"] > 0  # Проверяем общее количество взрослых
        ):  # Дополнительно проверяем количество обычных билетов
            register_item(
                device,
                f"Билет взрослый акция {time} ч.",
                sale_dict["detail"][1],
                sale_dict["detail"][0],
            )
        # Детские билеты
        kol_child_edit = sale_dict["kol_child"] - sale_dict["detail"][2]
        if kol_child_edit > 0:  # Регистрация только если есть билеты
            register_item(
                device,
                f"Билет детский {time} ч.",
                sale_dict["price_child"],
                kol_child_edit,
            )
        # Детские билеты со скидкой
        if (
            sale_dict["detail"][2] > 0
            and sale_dict["detail"][3] > 0
            and sale_dict["kol_child"] > 0  # Проверяем общее количество детей
        ):  # Дополнительно проверяем количество обычных детских билетов
            register_item(
                device,
                f"Билет детский акция {time} ч.",
                sale_dict["detail"][3],
                sale_dict["detail"][2],
            )
    else:
        # Для других типов операций, регистрация остальных товаров
        for item_name, item_data in sale_dict.items():
            if (
                isinstance(item_data, list) and item_data[0] > 0 and item_data[1] > 0
            ):  # Проверяем наличие количества и цены
                register_item(device, item_name, item_data[0], item_data[1])
            else:
                # Обработка других типов данных
                logger.error(f"Ошибка типа данных. Item_data - не список.")


def process_payment(device, payment_type, bank_status, sale_dict, price):
    """Функция обрабатывает оплату чека, в зависимости от типа оплаты (наличными, картой или оффлайн).

     Параметры:
        device (object): Объект устройства, поддерживающий метод `setParam()` для настройки параметров чека.
        payment_type (int): Тип оплаты (например, наличными, картой или оффлайн).
        bank_status (int): Флаг банка, необходимый для определения метода оплаты (например, 1 для картой).
        sale_dict (dict): Словарь с данными о продаже, включая сумму.
        price (float): Общая стоимость товаров в чеке.

    Возвращаемое значение:
        bool: Возвращает `True`, если оплата прошла успешно, иначе — `False`.
    """
    logger.info("Запуск функции process_payment")
    logger.debug(f"В функцию переданы: device = {device}, payment_type = {payment_type}, bank = {bank_status}, sale_dict = {sale_dict}, price = {price}")
    payment_amount = sale_dict["detail"][7] if payment_type == 1 else price
    if payment_type == PAYMENT_CASH:
        logger.info("Оплата наличными")
        device.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH)
    elif payment_type == PAYMENT_ELECTRONIC:
        if bank_status != 1:
            logger.error("Отсутствует подтверждение банковской операции")
            return False
        logger.info("Оплата картой")
        device.setParam(
            IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_ELECTRONICALLY
        )
    elif payment_type == PAYMENT_OFFLINE:
        logger.info("Оплата оффлайн")
        device.setParam(
            IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_ELECTRONICALLY
        )
    else:
        logger.error(f"Неверный тип оплаты: {payment_type}")
        return False
    device.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_SUM, payment_amount)
    device.payment()
    device.closeReceipt()
    return True


def handle_document_errors(device, retry_count, max_retries, on_error=None):
    """Функция пытается закрыть документ, повторяя попытки в случае ошибки до достижения максимального числа попыток.

    Параметры:
        device (object): Объект устройства для работы с чеками.
        retry_count (int): Текущее количество попыток.
        max_retries (int): Максимальное количество попыток закрытия документа.
        on_error (callable, optional): Функция для обработки ошибок, вызываемая при достижении максимального числа попыток.

    Возвращаемое значение:
        bool: Возвращает `True`, если документ был успешно закрыт, или `False`, если после всех попыток документ не закрылся.
    """
    logger.info("Запуск функции handle_document_errors")
    while retry_count < max_retries:
        if device.checkDocumentClosed() >= 0 and device.getParamBool(
            IFptr.LIBFPTR_PARAM_DOCUMENT_CLOSED
        ):
            return True
        retry_count += 1
        logger.warning(
            f"Не удалось проверить состояние документа. Попытка {retry_count}"
        )
        time.sleep(1)
    logger.error(f"Документ не закрылся после {max_retries} попыток. Отмена чека.")

    if on_error:
        on_error("Ошибка ККМ", "Документ не закрылся после 5 попыток. Отмена чека.")

    device.cancelReceipt()
    return False


def check_open(sale_dict, payment_type, user, type_operation, print_check, price, bank_status, on_error=None):
    """
    Проведение операции оплаты.

    Параметры:
        sale_dict (dict): Словарь с данными о продаже.
        payment_type (int): Тип оплаты.
        user (object): Информация о пользователе.
        type_operation (int): Тип операции (1 - продажа, 2 - возврат).
        print_check (int): Флаг печати чека.
        price (float): Сумма операции.
        bank_status (int): Результат операции по терминалу.

    Возвращает:
        int: 1 - успех, 0 - ошибка.
    """
    logger.info("Запуск функции check_open")
    retry_count = 0
    max_retries = 5
    logger.debug(
        f"В функцию переданы: sale_dict = {sale_dict}, payment_type = {payment_type}, type_operation = {type_operation}, bank_status = {bank_status}"
    )
    if print_check == 0:
        logger.info("Кассовый чек не печатаем")
    logger.info(f"Тип оплаты: {payment_type}")
    with fptr_connection(fptr) as device:
        # Настройка параметров ККМ
        setup_fptr(device, user, type_operation, print_check)
        # Открытие чека
        device.openReceipt()
        # Регистрация билетов
        register_tickets(device, sale_dict, type_operation)
        # Оплата
        if not process_payment(device, payment_type, bank_status, sale_dict, price):
            return 0
        # Проверка состояния документа
        if not handle_document_errors(device, retry_count, max_retries, on_error):
            return 0
        # Продолжение печати, если чек не печатается
        if print_check == 0:
            device.continuePrint()
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
    try:
        # Проверка состояния смены
        state = smena_info()
        if state != 0:
            res = windows.info_dialog_window(
                "Внимание! Кассовая смена не закрыта",
                "Хотите сделать сверку итогов и снять отчет с гашением?",
            )
            if res == 1:
                result = terminal_check_itog()  # Проведение сверки
                try:
                    if result == 1:
                        with fptr_connection(fptr):
                            fptr.setParam(1021, f"{user.last_name} {user.first_name}")
                            fptr.setParam(1203, user.inn)
                            fptr.operatorLogin()
                            fptr.setParam(
                                IFptr.LIBFPTR_PARAM_REPORT_TYPE,
                                IFptr.LIBFPTR_RT_CLOSE_SHIFT,
                            )
                            fptr.report()  # Отчет о закрытии смены
                            fptr.checkDocumentClosed()  # Проверка закрытия документа
                    else:
                        # Обработка ошибок при сверке итогов
                        logger.warning("Ошибка при сверке итогов.")
                        windows.info_window(
                            "Сверка итогов по банковскому терминалу завершена неудачно.",
                            "",
                            "",
                        )
                except FileNotFoundError as not_found:
                    # Обработка ошибки отсутствия файла
                    lines = "File not found!"
                    logger.warning(f"Файл не найден: {not_found.filename}")
                    windows.info_window(
                        "Сверка итогов по банковскому терминалу завершена неудачно.",
                        "",
                        f"Ошибка: {lines}",
                    )
                except Exception as e:
                    # Обработка других ошибок при работе с фискальным принтером
                    logger.error(f"Ошибка при выполнении отчета о закрытии смены: {e}")
                    windows.info_window(
                        "Произошла ошибка при закрытии смены.",
                        "Пожалуйста, попробуйте позже.",
                        str(e),
                    )
            else:
                windows.info_window(
                    "Сверка итогов по банковскому терминалу завершена неудачно.", "", ""
                )
                logger.info(f"Состояние смены: {state}")
        else:
            # Логирование успешного состояния
            logger.info("Смена уже закрыта.")
    except Exception as e:
        # Обработка ошибок на уровне основной функции
        logger.error(f"Ошибка при закрытии смены: {e}")
        windows.info_window(
            "Произошла ошибка при попытке закрытия смены.",
            "Пожалуйста, попробуйте позже.",
            str(e),
        )


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
    try:
        # Попытка продолжить печать
        fptr.continuePrint()
    except Exception as e:
        # Логирование ошибки
        logger.error(f"Ошибка при продолжении печати: {e}")
        # Уведомление пользователя
        windows.info_window(
            "Ошибка при продолжении печати.",
            "Пожалуйста, проверьте подключение к фискальному принтеру и повторите попытку.",
            str(e),
        )


def print_text(text: str):
    """Печать слип-чека.

    Параметры:
        text (str): Строка для печати.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, но может вызывать исключения в случае ошибок при печати.
    """
    try:
        # Устанавливаем параметры для печати строки
        fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT, text)
        # Печатаем текст
        fptr.printText()
        # Устанавливаем перенос строки
        fptr.setParam(IFptr.LIBFPTR_PARAM_TEXT_WRAP, IFptr.LIBFPTR_TW_WORDS)
    except Exception as e:
        # Логирование ошибки
        logger.error(f"Ошибка при печати текста: {e}")
        # Уведомление пользователя
        windows.info_window(
            "Ошибка при печати слип-чека.",
            "Пожалуйста, проверьте принтер и повторите попытку.",
            str(e),
        )
