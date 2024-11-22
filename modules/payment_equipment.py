import os
import subprocess
import time
from contextlib import contextmanager

from modules import windows
from modules.config import Config
from modules.libfptr10 import IFptr
from modules.logger import logger, logger_wraps

config = Config()

try:
    fptr = IFptr("")
except Exception as e:
    logger.warning(f"Не установлен драйвер ККТ: {str(e)}")


# Константы для работы с результатами терминала
TERMINAL_SUCCESS_CODE: int = 0
TERMINAL_USER_CANCEL_CODE: int = 2000
TERMINAL_DATA_EXCHANGE: int = 4134
APPROVE: str = "ОДОБРЕНО"
COINCIDENCE: str = "совпали"
EMAIL: str = "test.check@pymasl.ru"
PAYMENT_CASH = 102
PAYMENT_ELECTRONIC = 101
PAYMENT_OFFLINE = 100


@contextmanager
def fptr_connection(device):
    """Контекстный менеджер для управления подключением к ККМ."""
    device.open()
    try:
        yield device  # передаем fptr внутрь контекста
    finally:
        device.close()


def run_terminal_command(command_params: str):
    """Запуск команды на терминале и возврат результата.

    Параметры:
        command_params (str): Параметры команды, которую нужно выполнить.

    Возвращаемое значение:
        subprocess.CompletedProcess или None:
            - Возвращает объект subprocess.CompletedProcess, если команда выполнена успешно.
            - Возвращает None, если произошла ошибка.
    """
    logger.info("Запуск функции run_terminal_command")
    pinpad_path: str = config.get("pinpad_path")  # Путь к директории
    pinpad_file: str = "loadparm.exe"  # Имя файла
    # Полный путь до исполняемого файла
    pinpad_run_path = os.path.join(pinpad_path, pinpad_file)
    pinpad_run: str = f"{pinpad_run_path} {command_params}"
    logger.info(f"Запуск команды: {pinpad_run}")
    try:
        # check=False позволяет самостоятельно обрабатывать коды возврата
        result = subprocess.run(pinpad_run, check=False)
        logger.info(f"Команда завершена с кодом: {result.returncode}")
        return result
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
    except UnicodeDecodeError as decode_error:
        logger.error(f"Ошибка декодирования файла {pinpad_file}: {decode_error}")
        return False


@logger_wraps()
def terminal_oplata(amount):
    """Операуия оплаты по банковскому терминалу.

    Параметры:
        amount (float):
            Сумма, которую необходимо оплатить.

    Возвращаемое значение:
        int:
            - Возвращает 1, если операция успешно завершена.
            - Возвращает 0, если произошла ошибка или операция была отменена.
    """
    logger.info("Запуск функции terminal_oplata")
    # Преобразуем сумму в целое число для корректного форматирования
    result = run_terminal_command(f"1 {amount}00")
    if result is None:
        logger.error("Ошибка при выполнении команды терминала")
        return 0
    logger.info(
        f"Статус проведения операции по банковскому терминалу: {result.returncode}"
    )
    if result.returncode == TERMINAL_USER_CANCEL_CODE:
        logger.warning("Оплата отменена пользователем")
        return 0
    elif result.returncode == TERMINAL_DATA_EXCHANGE:
        windows.info_window(
            "Ошибка при проведении оплаты",
            "Требуется сделать сверку итогов и после этого повторить операцию оплаты",
            "Команда завершена с кодом: 4134",
        )
        return 0
    elif result.returncode == TERMINAL_SUCCESS_CODE:
        try:
            return 1 if check_terminal_file(APPROVE) else 0
        except FileNotFoundError as not_found:
            logger.error(f"Файл не найден: {not_found}")
            return 0
    else:
        logger.error(f"Неизвестный код возврата: {result.returncode}")
        return 0


@logger_wraps()
def terminal_return(amount):
    """Операуия возврата по банковскому терминалу

    Параметры:
        amount (float):
            Сумма, которую необходимо вернуть.

    Возвращаемое значение:
        int:
            - Возвращает 1, если возврат успешно завершен.
            - Возвращает 0, если произошла ошибка или файл не найден.
    """
    logger.info("Запуск функции terminal_return")
    logger.debug(f"В функцию была передана следующая сумма: {amount}")
    # Добавляем '00' для копеек
    result = run_terminal_command(f"1 {amount}00")
    logger.debug(f"Терминал вернул следующий код операции: {result}")
    if result is None:
        logger.error("Ошибка при выполнении команды терминала")
        return 0
    if result.returncode == TERMINAL_SUCCESS_CODE:
        try:
            return 1 if check_terminal_file(APPROVE) else 0
        except FileNotFoundError as not_found:
            logger.error(f"Файл не найден: {not_found}")
            return 0
    elif result.returncode == TERMINAL_DATA_EXCHANGE:
        windows.info_window(
            "Ошибка при проведении оплаты",
            "Требуется сделать сверку итогов и после этого повторить операцию оплаты",
            "Команда завершена с кодом: 4134",
        )
        return 0
    else:
        logger.error(f"Неизвестный код возврата: {result.returncode}")
        return 0


@logger_wraps()
def terminal_canceling(amount):
    """Операуия отмены по банковскому терминалу.

    Параметры:
        amount (float):
            Сумма, которую необходимо отменить.

    Возвращаемое значение:
        int:
            - Возвращает 1, если отмена успешно завершена.
            - Возвращает 0, если произошла ошибка или файл не найден.
    """
    logger.info("Запуск функции terminal_canceling")
    logger.debug(f"В функцию была передана следующая сумма: {amount}")
    # Добавляем '00' для копеек
    result = run_terminal_command(f"1 {amount}00")
    logger.debug(f"Терминал вернул следующий код операции: {result}")
    if result is None:
        logger.error("Ошибка при выполнении команды терминала")
        return 0
    if result.returncode == TERMINAL_SUCCESS_CODE:
        try:
            return 1 if check_terminal_file(APPROVE) else 0
        except FileNotFoundError as not_found:
            logger.error(f"Файл не найден: {not_found}")
            return 0
    elif result.returncode == TERMINAL_DATA_EXCHANGE:
        windows.info_window(
            "Ошибка при проведении оплаты",
            "Требуется сделать сверку итогов и после этого повторить операцию оплаты",
            "Команда завершена с кодом: 4134",
        )
        return 0
    else:
        logger.error(f"Неизвестный код возврата: {result.returncode}")
        return 0


@logger_wraps()
def terminal_check_itog():
    """Сверка итогов работы банковского терминала.

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
            logger.debug("Функция печати нефискального документа")
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
    try:
        with fptr_connection(fptr):
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
    except ConnectionError as ce:
        logger.error(f"Ошибка подключения к ККТ: {ce}")
        windows.info_window(
            "Ошибка", "Не удалось подключиться к ККТ.", "Проверьте подключение."
        )
    except AttributeError as ae:
        logger.error(f"Ошибка при получении данных о ККТ: {ae}")
        windows.info_window(
            "Ошибка",
            "Не удалось получить данные о ККТ.",
            "Проверьте настройки устройства.",
        )
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        windows.info_window(
            "Ошибка", "Произошла неизвестная ошибка.", "Попробуйте снова."
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
        logger.info("Печать последнего документа успешно выполнена")
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
        logger.info("Отчет о состоянии расчетов успешно распечатан.")
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
        logger.info("X-отчет успешно распечатан.")
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
    logger.info(f"Внесено в кассу: {amount}")
    if amount <= 0:
        logger.error(
            f"Некорректная сумма для внесения: {amount}. Сумма должна быть положительной."
        )
        windows.info_window("Ошибка", "Сумма внесения должна быть положительной.")
        return
    logger.info(f"Внесено в кассу: {amount}")
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
    logger.info(f"Выплачено из кассы: {amount}")
    if amount <= 0:
        logger.error(
            f"Некорректная сумма для выплаты: {amount}. Сумма должна быть положительной."
        )
        windows.info_window("Ошибка", "Сумма выплаты должна быть положительной.", "")
        return
    logger.info(f"Выплачено из кассы: {amount}")
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
        elif payment_type == PAYMENT_OFFLINE:
            logger.debug("Продажа новая. Начинаем оплату")
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
    """Регистрация товара в чеке"""
    logger.info("Запуск функции register_item")
    device.setParam(IFptr.LIBFPTR_PARAM_COMMODITY_NAME, name)
    device.setParam(IFptr.LIBFPTR_PARAM_PRICE, price)
    device.setParam(IFptr.LIBFPTR_PARAM_QUANTITY, quantity)
    device.setParam(IFptr.LIBFPTR_PARAM_TAX_TYPE, tax_type)
    device.registration()


def setup_fptr(device, user, type_operation, print_check):
    """Настройка параметров ККМ."""
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
    """Регистрация позиций в чеке."""
    logger.info("Запуск функции register_tickets")
    if type_operation == 1:
        time = sale_dict["detail"][6]
        # Взрослые билеты
        kol_adult_edit = sale_dict["kol_adult"] - sale_dict["detail"][0]
        if kol_adult_edit > 0:
            register_item(
                device,
                f"Билет взрослый {time} ч.",
                sale_dict["price_adult"],
                kol_adult_edit,
            )
        # Взрослые билеты со скидкой
        if sale_dict["detail"][0] > 0 and sale_dict["detail"][1] > 0:
            register_item(
                device,
                f"Билет взрослый акция {time} ч.",
                sale_dict["detail"][1],
                sale_dict["detail"][0],
            )
        # Детские билеты
        kol_child_edit = sale_dict["kol_child"] - sale_dict["detail"][2]
        if kol_child_edit > 0:
            register_item(
                device,
                f"Билет детский {time} ч.",
                sale_dict["price_child"],
                kol_child_edit,
            )
        # Детские билеты со скидкой
        if sale_dict["detail"][2] > 0 and sale_dict["detail"][3] > 0:
            register_item(
                device,
                f"Билет детский акция {time} ч.",
                sale_dict["detail"][3],
                sale_dict["detail"][2],
            )
    else:
        for item_name, item_data in sale_dict.items():
            register_item(device, item_name, item_data[0], item_data[1])


def process_payment(device, payment_type, bank, sale_dict, price):
    """Обработка оплаты чека."""
    logger.info("Запуск функции process_payment")
    payment_amount = sale_dict["detail"][7] if payment_type == 1 else price
    if payment_type == PAYMENT_CASH:
        logger.info("Оплата наличными")
        device.setParam(IFptr.LIBFPTR_PARAM_PAYMENT_TYPE, IFptr.LIBFPTR_PT_CASH)
    elif payment_type == PAYMENT_ELECTRONIC and bank == 1:
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


def handle_document_errors(device, retry_count, max_retries):
    """Обработка ошибок закрытия документа."""
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
    windows.info_window(
        f"Документ не закрылся после {max_retries} попыток.", "Отмена чека.", ""
    )
    device.cancelReceipt()
    return False


def check_open(sale_dict, payment_type, user, type_operation, print_check, price, bank):
    """
    Проведение операции оплаты.

    Параметры:
        sale_dict (dict): Словарь с данными о продаже.
        payment_type (int): Тип оплаты.
        user (object): Информация о пользователе.
        type_operation (int): Тип операции (1 - продажа, 2 - возврат).
        print_check (int): Флаг печати чека.
        price (float): Сумма операции.
        bank (int): Результат операции по терминалу.

    Возвращает:
        int: 1 - успех, 0 - ошибка.
    """
    logger.info("Запуск функции check_open")
    retry_count = 0
    max_retries = 5
    logger.debug(
        f"В функцию переданы: sale_dict = {sale_dict}, payment_type = {payment_type}, type_operation = {type_operation}, bank = {bank}"
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
        if not process_payment(device, payment_type, bank, sale_dict, price):
            return 0
        # Проверка состояния документа
        if not handle_document_errors(device, retry_count, max_retries):
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
                logger.warning(f"Состояние смены: {state}")
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
        logger.info("Продолжение печати выполнено успешно.")
    except Exception as e:
        # Логирование ошибки
        logger.error(f"Ошибка при продолжении печати: {e}")
        # Уведомление пользователя
        windows.info_window(
            "Ошибка при продолжении печати.",
            "Пожалуйста, проверьте подключение к фискальному принтеру и повторите попытку.",
            str(e),
        )


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
