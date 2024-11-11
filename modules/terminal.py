import os
import subprocess
from typing import Any

from modules import windows, kkt
from modules.config import Config
from modules.logger import logger, logger_wraps

config = Config()


# Константы для обработки результатов работы терминала
TERMINAL_SUCCESS_CODE: int = 0
TERMINAL_USER_CANCEL_CODE: int = 2000
APPROVE: str = "ОДОБРЕНО"
COINCIDENCE: str = "совпали"


def run_terminal_command(command_params: str):
    """Запуск оплаты по банковскому терминалу и возврат кода результата.

    Параметры:
        command_params (str):
            Параметры для команды, которую необходимо выполнить на терминале.

    Возвращаемое значение:
        subprocess.CompletedProcess или None:
            - Возвращает объект subprocess.CompletedProcess, если команда выполнена успешно.
            - Возвращает None, если конфигурация не загружена или произошла ошибка выполнения команды.
    """
    logger.info("Запуск функции run_terminal_command")
    pinpad_path: str = config.get("pinpad_path")
    pinpad_file: str = os.path.join(pinpad_path, "loadparm.exe")
    pinpad_run: str = f"{pinpad_file} {command_params}"
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
    pinpad_path: Any = config.get("pinpad_path")
    pinpad_file: str = os.path.join(pinpad_path, "p")
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
    # Добавляем '00' для копеек
    plat_code = run_terminal_command(f"1 {amount}00")
    if plat_code is None:
        logger.error("Ошибка при выполнении команды терминала")
        logger.info(
            f"Статус проведения операции по банковскому терминалу: {plat_code.returncode}"
        )
        return 0  # Обрабатываем ошибку
    if plat_code.returncode == TERMINAL_SUCCESS_CODE:
        return 1 if check_terminal_file(APPROVE) else 0
    elif plat_code.returncode == TERMINAL_USER_CANCEL_CODE:
        logger.warning("Оплата отменена пользователем")
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
    result = run_terminal_command(f"3 {amount}00")
    logger.debug(f"Терминал вернул следующий код операции: {result}")
    # if result == TERMINAL_SUCCESS_CODE: # TODO: проверить статус-код
    #     return 1 if check_terminal_file() else 0
    return 1 if check_terminal_file(APPROVE) else 0


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
    result = run_terminal_command(f"8 {amount}00")
    logger.debug(f"Терминал вернул следующий код операции: {result}")
    # if result == TERMINAL_SUCCESS_CODE: # TODO: проверить статус-код
    #     return 1 if check_terminal_file() else 0
    return 1 if check_terminal_file(APPROVE) else 0


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
    return 1 if check_terminal_file(COINCIDENCE) else 0


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
    """Сводный чек без детализации.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, просто вызывает команду терминала.
    """
    logger.info("Запуск функции terminal_svod_check")
    run_terminal_command("9")
    try:
        kkt.print_pinpad_check(1)
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
    run_terminal_command("9 1")
    try:
        kkt.print_pinpad_check(1)
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


@logger_wraps()
def terminal_print_file():
    """Печать файла-отчета.

    Возвращаемое значение:
        None:
            Функция не возвращает значений, просто вызывает команду терминала.
    """
    logger.info("Запуск функции terminal_print_file")
    try:
        kkt.print_pinpad_check(1)
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
        info: str = read_pinpad_file()
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)
    windows.info_window("Смотрите подробную информацию.", "", info)


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
    run_terminal_command("12")
    try:
        kkt.print_pinpad_check(1)
    except FileNotFoundError as not_found:
        logger.warning(not_found.filename)


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
    pinpad_file = os.path.join(pinpad_path, "p")
    result_lines: list[str] = []
    try:
        with open(pinpad_file, "r", encoding="IBM866") as file:
            for line in file:
                # Убираем символ новой строки, если параметр remove_newline=True
                line: str = line.rstrip() if remove_newline else line
                result_lines.append(line)
                kkt.print_text(line)
    except FileNotFoundError as not_found:
        logger.warning("Файл не найден: %s", not_found.filename)
    return "".join(result_lines)
