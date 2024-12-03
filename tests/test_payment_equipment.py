import os
from unittest import mock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from modules.config import Config
from modules.payment_equipment import (
    fptr_connection,
    run_terminal_command,
    check_terminal_file,
    terminal_oplata,
    terminal_return,
    terminal_canceling,
    terminal_check_itog,
    terminal_check_itog_window,
    terminal_control_lenta,
    terminal_print_file,
    terminal_copy_last_check,
    read_pinpad_file,
    register_tickets,
    handle_document_errors,
)

# Константы для тестирования
TERMINAL_SUCCESS_CODE: int = 0
TERMINAL_USER_CANCEL_CODE: int = 2000
TERMINAL_DATA_EXCHANGE: int = 4134
TERMINAL_NO_MONEY: int = 4451
TERMINAL_KLK: int = 4120
TERMINAL_CARD_BLOCKED: set[int] = {2004, 2005, 2006, 2007, 2405, 2406, 2407}
TERMINAL_INVALID_CURRENCY_CODE: int = 4336
TERMINAL_NO_ADDRESS_TO_CONTACT: int = 4139
APPROVE = "APPROVE"  # Слово для проверки в файле


# Мок-объект для fptr
@pytest.fixture
def mock_fptr():
    mock = MagicMock()
    return mock


# Тестирование открытия и закрытия соединения
def test_fptr_connection_opens_and_closes(mock_fptr):
    # Тестируем, что при входе в контекст вызывается open, а при выходе - close
    with fptr_connection(mock_fptr):
        mock_fptr.open.assert_called_once()  # open должен быть вызван
        mock_fptr.close.assert_not_called()  # close еще не должен быть вызван

    # После выхода из контекста close должен быть вызван
    mock_fptr.close.assert_called_once()


# Тестирование с исключением в блоке контекста
def test_fptr_connection_with_exception(mock_fptr):
    # Тестируем, что при исключении в блоке контекста close все равно вызовется
    with pytest.raises(Exception):
        with fptr_connection(mock_fptr):
            mock_fptr.open.assert_called_once()
            raise Exception("Test exception")

    mock_fptr.close.assert_called_once()  # close должен быть вызван


#######################################
# Тестируем terminal_command_successful
# Фикстура для мока Config
@pytest.fixture
def mock_config():
    with patch.object(Config, "get") as mock_get:
        yield mock_get


# Фикстура для мока subprocess.run
@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_run:
        yield mock_run


# Тест успешного выполнения команды
def test_run_terminal_command_successful(mock_config, mock_subprocess_run):
    """Тестируем успешный запуск команды на терминале."""

    # Мокаем путь к терминалу, который вернется через метод get
    mock_config.return_value = "C:\\sc552"

    # Мокаем возврат команды для subprocess.run
    mock_run = mock_subprocess_run.return_value
    mock_run.returncode = 0  # Успешное выполнение команды

    # Параметры для теста
    command_params = "1 123"

    # Вызов функции
    result = run_terminal_command(command_params)

    # Проверяем, что subprocess.run был вызван с правильными аргументами
    mock_subprocess_run.assert_called_once_with(
        "C:\\sc552\\loadparm.exe 1 123", check=False
    )

    # Проверяем, что результат выполнения функции не является None
    assert result is not None
    assert result.returncode == 0


def test_run_terminal_command_with_error(mock_subprocess_run, mock_config):
    """Тестируем выполнение команды с ошибкой."""

    # Подготовка мока
    mock_run = mock_subprocess_run.return_value
    mock_run.returncode = 1  # Ошибка при выполнении команды

    # Мокаем конфигурацию, возвращаем путь к утилите
    mock_config.return_value = "C:\\sc552"  # Путь без имени файла

    # Параметры для теста
    command_params = "1 123"

    # Вызов функции
    result = run_terminal_command(command_params)

    # Проверяем, что subprocess.run был вызван с правильными параметрами
    mock_subprocess_run.assert_called_once_with(
        "C:\\sc552\\loadparm.exe 1 123",
        check=False,  # Путь должен быть без удвоенного имени файла
    )

    # Проверяем, что результат выполнения команды правильный (ошибка)
    assert result is not None
    assert result.returncode == 1


def test_run_terminal_command_with_invalid_command(mock_subprocess_run, mock_config):
    """Тестируем выполнение команды с некорректными параметрами."""

    # Подготовка мока
    mock_run = mock_subprocess_run.return_value
    mock_run.returncode = 0  # Симулируем успешное выполнение команды

    # Мокаем конфигурацию, возвращаем путь к утилите
    mock_config.return_value = "C:\\sc552"  # Путь без имени файла

    # Параметры для теста
    command_params = "99"  # Некорректные параметры

    # Вызов функции
    result = run_terminal_command(command_params)

    # Проверяем, что subprocess.run был вызван с правильными параметрами
    mock_subprocess_run.assert_called_once_with(
        "C:\\sc552\\loadparm.exe 99",
        check=False,  # Путь должен быть без повторного добавления имени файла
    )

    # Проверяем, что результат выполнения команды правильный
    assert result is not None
    assert result.returncode == 0


def test_run_terminal_command_missing_parameters(mock_subprocess_run, mock_config):
    """Тестируем выполнение команды без параметров (или с недостаточным количеством)."""

    # Подготовка мока
    mock_run = mock_subprocess_run.return_value
    mock_run.returncode = 0

    # Мокаем конфигурацию, возвращаем путь к утилите
    mock_config.return_value = "C:\\sc552"  # Путь без имени файла

    # Параметры для теста
    command_params = "1"  # Например, команда оплаты без суммы

    # Вызов функции
    result = run_terminal_command(command_params)

    # Проверяем, что subprocess.run был вызван с правильными параметрами
    mock_subprocess_run.assert_called_once_with(
        "C:\\sc552\\loadparm.exe 1",
        check=False,  # Путь должен быть без повторного добавления имени файла
    )

    # Проверяем, что результат выполнения команды правильный
    assert result is not None
    assert result.returncode == 0


def test_config_file_not_found(mock_subprocess_run):
    """Тестируем ситуацию, когда файл конфигурации не найден."""

    # Мокаем Config так, чтобы при попытке получить значение через get была выброшена ошибка
    with patch(
        "modules.config.Config.get",
        side_effect=FileNotFoundError("Файл конфигурации не найден"),
    ):
        with pytest.raises(FileNotFoundError):
            run_terminal_command("1 123")


def test_invalid_config(mock_subprocess_run):
    """Тестируем ситуацию с некорректной конфигурацией."""

    # Мокаем конфигурацию так, чтобы она выкидывала ошибку при получении пути
    with patch(
        "modules.config.Config.get", side_effect=ValueError("Ошибка в конфигурации")
    ):
        with pytest.raises(ValueError):
            run_terminal_command("1 123")


#######################################
# Тестируем check_terminal_file
# Фикстура для мокирования функции open
@pytest.fixture
def mock_file_open():
    with mock.patch("builtins.open", mock.mock_open()) as mock_file:
        yield mock_file


# Тест для случая, когда слово найдено в файле
@patch(
    "modules.config.Config.get", return_value="C:\\sc552"
)  # Мокаем Config.get с ключом 'pinpad_path'
@patch(
    "builtins.open",
    new_callable=mock.mock_open,
    read_data="Это тестовый файл, содержащий слово Success.",
)
def test_check_terminal_file_word_found(mock_file_open, mock_config_get):
    # Путь, который реально генерируется в системе
    file_path = "C:\\sc552\\p"  # Это путь, который должен быть передан в open()

    # Вызов тестируемой функции
    result = check_terminal_file("Success")

    # Проверка, что функция вернула True, потому что слово найдено
    assert result is True

    # Проверка, что open был вызван с правильным путем и кодировкой
    mock_file_open.assert_called_once_with(file_path, encoding="IBM866")


# Тест для случая, когда слово не найдено в файле
def test_check_terminal_file_word_not_found():
    # Мокаем содержимое файла
    with mock.patch(
        "builtins.open",
        mock.mock_open(read_data="Это тестовый файл без искомого слова."),
    ) as mock_file_open, mock.patch(
        "modules.config.Config.get", return_value="C:\\mock\\path"
    ) as mock_config:
        # Вызываем тестируемую функцию
        result = check_terminal_file("Success")

        # Проверки
        assert result is False

        # Ожидаемый путь для open
        expected_path = os.path.join("C:\\mock\\path", "p")

        # Нормализуем путь для текущей ОС
        normalized_expected_path = os.path.normpath(expected_path)

        # Создаем объект call с ожидаемым значением
        expected_call = mock.call(normalized_expected_path, encoding="IBM866")

        # Проверка, что open был вызван с правильным путем и кодировкой
        mock_file_open.assert_called_once_with(
            normalized_expected_path, encoding="IBM866"
        )  # Проверка вызова open


# Тест для случая, когда файл не найден
def test_check_terminal_file_file_not_found(mock_config):
    # Мокаем ошибку при открытии файла
    with mock.patch("builtins.open", side_effect=FileNotFoundError):
        result = check_terminal_file("Success")

    # Проверка результата
    assert result is False


# Тест для случая некорректной кодировки
def test_check_terminal_file_invalid_encoding(mock_config):
    # Мокаем ошибку с кодировкой
    with mock.patch(
        "builtins.open", side_effect=UnicodeDecodeError("IBM866", b"", 0, 1, "invalid")
    ):
        result = check_terminal_file("Success")

    # Проверка результата
    assert result is False


# Тестируем check_terminal_file, когда файл пуст
@patch(
    "modules.payment_equipment.config.get"
)  # Мокаем config.get, чтобы вернуть нужный путь
@patch("builtins.open", new_callable=mock.mock_open, read_data="")
def test_check_terminal_file_empty_file(mock_file_open, mock_config):
    # Настроим mock_config.get(), чтобы он возвращал строку с правильным путем
    mock_config.return_value = "/mock/path"  # Мокаем правильный путь к каталогу

    # Формируем путь, как это делает функция check_terminal_file (используется os.path.join)
    expected_file_path = os.path.join(mock_config.return_value, "p")

    # Вызов тестируемой функции
    result = check_terminal_file("Success")

    # Проверки
    assert result is False  # Ожидаем, что результат будет False, так как файл пуст

    # Проверка, что open был вызван с правильным путем
    mock_file_open.assert_called_once_with(
        expected_file_path, encoding="IBM866"
    )  # Проверка вызова open
    mock_file_open.return_value.read.assert_called_once()  # Проверка вызова read


#######################################
# Тестируем terminal_check_itog
# Мокируем функцию run_terminal_command
@pytest.fixture
def mock_run_terminal_command():
    with mock.patch("modules.payment_equipment.run_terminal_command") as mock_run:
        yield mock_run


# Мокируем функцию check_terminal_file
@pytest.fixture
def mock_check_terminal_file():
    with mock.patch("modules.payment_equipment.check_terminal_file") as mock_check:
        yield mock_check


def test_terminal_check_itog_success(
    mock_run_terminal_command, mock_check_terminal_file
):
    # Успешный сценарий
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_check_terminal_file.return_value = True

    result = terminal_check_itog()

    assert result == 1
    mock_run_terminal_command.assert_called_once_with("7")
    mock_check_terminal_file.assert_called_once_with(
        "совпали"
    )  # Проверка для 'совпали' вместо 'СОВПАДЕНИЕ'


def test_terminal_check_itog_run_command_failure(mock_run_terminal_command):
    # Ошибка выполнения команды
    mock_run_terminal_command.return_value = (
        None  # Моделируем ошибку выполнения команды
    )

    result = terminal_check_itog()

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("7")


def test_terminal_check_itog_file_not_found(
    mock_run_terminal_command, mock_check_terminal_file
):
    # Файл не найден (например, ошибка в check_terminal_file)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_check_terminal_file.return_value = False  # Не нашли нужное слово в файле

    result = terminal_check_itog()

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("7")
    mock_check_terminal_file.assert_called_once_with("совпали")  # Ожидаем "совпали"


def test_terminal_check_itog_file_read_error(mock_run_terminal_command):
    # Ошибка при чтении файла (например, файл не существует)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE

    with mock.patch(
        "modules.payment_equipment.check_terminal_file", side_effect=FileNotFoundError
    ):
        result = terminal_check_itog()

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("7")


#######################################
# Тестируем terminal_check_itog_window
# Мокируем функцию run_terminal_command
@pytest.fixture
def mock_run_terminal_command():
    with mock.patch("modules.payment_equipment.run_terminal_command") as mock_run:
        yield mock_run


# Мокируем функцию read_pinpad_file
@pytest.fixture
def mock_read_pinpad_file():
    with mock.patch("modules.payment_equipment.read_pinpad_file") as mock_read:
        yield mock_read


# Мокируем функцию windows.info_window
@pytest.fixture
def mock_info_window():
    with mock.patch("modules.payment_equipment.windows.info_window") as mock_info:
        yield mock_info


def test_terminal_check_itog_window_success(
    mock_run_terminal_command, mock_read_pinpad_file, mock_info_window
):
    # Успешный сценарий
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_read_pinpad_file.return_value = "Информация о сверке итогов"

    terminal_check_itog_window()

    mock_run_terminal_command.assert_called_once_with("7")
    mock_read_pinpad_file.assert_called_once()
    mock_info_window.assert_called_once_with(
        "Смотрите подробную информацию.", "", "Информация о сверке итогов"
    )


def test_terminal_check_itog_window_run_command_failure(
    mock_run_terminal_command, mock_info_window
):
    # Ошибка выполнения команды
    mock_run_terminal_command.return_value = (
        None  # Моделируем ошибку выполнения команды
    )

    terminal_check_itog_window()

    mock_run_terminal_command.assert_called_once_with("7")
    mock_info_window.assert_called_once_with(
        "Ошибка выполнения команды терминала", "", "Команда не выполнена"
    )


def test_terminal_check_itog_window_file_not_found(
    mock_run_terminal_command, mock_read_pinpad_file, mock_info_window
):
    # Файл не найден (например, ошибка в read_pinpad_file)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_read_pinpad_file.side_effect = FileNotFoundError("Файл не найден")

    terminal_check_itog_window()

    mock_run_terminal_command.assert_called_once_with("7")
    mock_read_pinpad_file.assert_called_once()
    mock_info_window.assert_called_once_with(
        "Ошибка сверки итогов по банковскому терминалу!", "", "Файл не найден"
    )


def test_terminal_check_itog_window_unknown_return_code(
    mock_run_terminal_command, mock_info_window
):
    # Неизвестный код возврата
    mock_run_terminal_command.return_value.returncode = 999  # Неизвестный код возврата

    terminal_check_itog_window()

    mock_run_terminal_command.assert_called_once_with("7")
    mock_info_window.assert_called_once_with(
        "Ошибка выполнения команды терминала", "", "Неизвестный код возврата: 999"
    )


#######################################
# Тестируем terminal_control_lenta
# Мокируем функцию run_terminal_command
@pytest.fixture
def mock_run_terminal_command():
    with mock.patch("modules.payment_equipment.run_terminal_command") as mock_run:
        yield mock_run


# Мокируем функцию print_pinpad_check
@pytest.fixture
def mock_print_pinpad_check():
    with mock.patch("modules.payment_equipment.print_pinpad_check") as mock_print:
        yield mock_print


def test_terminal_control_lenta_success(
    mock_run_terminal_command, mock_print_pinpad_check
):
    # Успешный сценарий
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE

    terminal_control_lenta()

    mock_run_terminal_command.assert_called_once_with("9 1")
    mock_print_pinpad_check.assert_called_once_with(1)


def test_terminal_control_lenta_run_command_failure(mock_run_terminal_command):
    # Ошибка выполнения команды
    mock_run_terminal_command.return_value = (
        None  # Моделируем ошибку выполнения команды
    )

    terminal_control_lenta()

    mock_run_terminal_command.assert_called_once_with("9 1")


def test_terminal_control_lenta_file_not_found(
    mock_run_terminal_command, mock_print_pinpad_check
):
    # Файл не найден (например, ошибка в print_pinpad_check)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_print_pinpad_check.side_effect = FileNotFoundError("Файл не найден")

    terminal_control_lenta()

    mock_run_terminal_command.assert_called_once_with("9 1")
    mock_print_pinpad_check.assert_called_once_with(1)


def test_terminal_control_lenta_unknown_return_code(mock_run_terminal_command):
    # Неизвестный код возврата
    mock_run_terminal_command.return_value.returncode = 999  # Неизвестный код возврата

    terminal_control_lenta()

    mock_run_terminal_command.assert_called_once_with("9 1")


#######################################
# Тестируем terminal_print_file
# Мокируем функцию print_pinpad_check
@pytest.fixture
def mock_print_pinpad_check():
    with mock.patch("modules.payment_equipment.print_pinpad_check") as mock_print:
        yield mock_print


def test_terminal_print_file_success(mock_print_pinpad_check):
    # Успешный сценарий
    terminal_print_file()

    mock_print_pinpad_check.assert_called_once_with(1)


def test_terminal_print_file_file_not_found(mock_print_pinpad_check):
    # Файл не найден (например, ошибка в print_pinpad_check)
    mock_print_pinpad_check.side_effect = FileNotFoundError("Файл не найден")

    terminal_print_file()

    mock_print_pinpad_check.assert_called_once_with(1)


#######################################
# Тестируем terminal_copy_last_check
# Мокируем функцию run_terminal_command
@pytest.fixture
def mock_run_terminal_command():
    with mock.patch("modules.payment_equipment.run_terminal_command") as mock_run:
        yield mock_run


# Мокируем функцию print_pinpad_check
@pytest.fixture
def mock_print_pinpad_check():
    with mock.patch("modules.payment_equipment.print_pinpad_check") as mock_print:
        yield mock_print


def test_terminal_copy_last_check_success(
    mock_run_terminal_command, mock_print_pinpad_check
):
    # Успешный сценарий
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE

    terminal_copy_last_check()

    mock_run_terminal_command.assert_called_once_with("12")
    mock_print_pinpad_check.assert_called_once_with(1)


def test_terminal_copy_last_check_run_command_failure(mock_run_terminal_command):
    # Ошибка выполнения команды
    mock_run_terminal_command.return_value = (
        None  # Моделируем ошибку выполнения команды
    )

    terminal_copy_last_check()

    mock_run_terminal_command.assert_called_once_with("12")


def test_terminal_copy_last_check_file_not_found(
    mock_run_terminal_command, mock_print_pinpad_check
):
    # Файл не найден (например, ошибка в print_pinpad_check)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_print_pinpad_check.side_effect = FileNotFoundError("Файл не найден")

    terminal_copy_last_check()

    mock_run_terminal_command.assert_called_once_with("12")
    mock_print_pinpad_check.assert_called_once_with(1)


def test_terminal_copy_last_check_unknown_return_code(mock_run_terminal_command):
    # Неизвестный код возврата
    mock_run_terminal_command.return_value.returncode = 999  # Неизвестный код возврата

    terminal_copy_last_check()

    mock_run_terminal_command.assert_called_once_with("12")


#######################################
# Тестируем read_pinpad_file
# Мокируем функцию config.get
@pytest.fixture
def mock_config_get():
    with mock.patch("modules.payment_equipment.config.get") as mock_get:
        yield mock_get


# Мокируем функцию print_text
@pytest.fixture
def mock_print_text():
    with mock.patch("modules.payment_equipment.print_text") as mock_print:
        yield mock_print


def test_read_pinpad_file_success(mock_config_get, mock_print_text):
    # Успешный сценарий
    mock_config_get.return_value = "/mock/path"
    with mock.patch(
        "builtins.open", mock.mock_open(read_data="Line1\nLine2\n")
    ) as mock_file_open:
        result = read_pinpad_file()

    assert result == "Line1Line2"
    mock_config_get.assert_called_once_with("pinpad_path")


def test_read_pinpad_file_success_with_newline(mock_config_get, mock_print_text):
    # Успешный сценарий с сохранением переноса строки
    mock_config_get.return_value = "/mock/path"
    with mock.patch(
        "builtins.open", mock.mock_open(read_data="Line1\nLine2\n")
    ) as mock_file_open:
        result = read_pinpad_file(remove_newline=False)

    assert result == "Line1\nLine2\n"
    mock_config_get.assert_called_once_with("pinpad_path")


def test_read_pinpad_file_config_not_loaded(mock_config_get):
    # Конфигурация не загружена
    mock_config_get.return_value = None

    result = read_pinpad_file()

    assert result is None
    mock_config_get.assert_called_once_with("pinpad_path")


def test_read_pinpad_file_file_not_found(mock_config_get, mock_print_text):
    # Файл не найден
    mock_config_get.return_value = "/mock/path"
    with mock.patch(
        "builtins.open", side_effect=FileNotFoundError("Файл не найден")
    ) as mock_file_open:
        result = read_pinpad_file()

    assert result is None
    mock_config_get.assert_called_once_with("pinpad_path")


def test_read_pinpad_file_decode_error(mock_config_get, mock_print_text):
    # Ошибка декодирования
    mock_config_get.return_value = "/mock/path"
    with mock.patch(
        "builtins.open", side_effect=UnicodeDecodeError("IBM866", b"", 0, 1, "invalid")
    ) as mock_file_open:
        result = read_pinpad_file()

    assert result is None
    mock_config_get.assert_called_once_with("pinpad_path")


def test_read_pinpad_file_no_remove_newline(
    mock_config_get, mock_print_text, mock_file_open
):
    # Мокаем конфигурацию
    mock_config_get.return_value = "C:\\path\\to\\file"

    # Мокаем открытие файла с тестовыми данными
    with mock.patch(
        "builtins.open", mock.mock_open(read_data="Тестовый чек\n")
    ) as mock_file:
        result = read_pinpad_file(remove_newline=False)

    # Проверяем, что функция вернула правильное содержимое
    assert result == "Тестовый чек\n"

    # Проверяем, что конфигурация была получена
    mock_config_get.assert_called_once_with("pinpad_path")

    # Проверяем, что open был вызван с правильными параметрами
    mock_file.assert_called_once_with("C:\\path\\to\\file\\p", "r", encoding="IBM866")


#######################################
# Тестируем register_tickets
@pytest.fixture
def mock_register_item():
    """Мокируем функцию register_item."""
    return MagicMock()


@pytest.fixture
def mock_device():
    """Мокируем устройство."""
    device_mock = MagicMock()
    device_mock.setParam = MagicMock()  # Мокируем метод setParam
    return device_mock


@pytest.fixture
def sale_dict():
    """Подготовка тестового словаря sale_dict."""
    return {
        "kol_adult": 5,
        "price_adult": 100,
        "kol_child": 3,
        "price_child": 50,
        "detail": [
            2,
            80,
            1,
            40,
            0,
            0,
            12,
        ],  # Включаем информацию о скидках и количестве
    }


def test_register_tickets_adult_no_discount(mock_register_item, sale_dict, mock_device):
    """Проверка регистрации взрослых билетов без скидки."""
    # Убираем скидки и цену со скидкой для взрослых
    sale_dict["detail"][0] = 0  # Количество взрослых с скидкой
    sale_dict["detail"][1] = 0  # Цена со скидкой для взрослых

    # Убираем скидку для детских билетов, чтобы зарегистрировать их по полной цене
    sale_dict["detail"][2] = 0  # Количество детских билетов с скидкой
    sale_dict["detail"][3] = 0  # Цена со скидкой для детских

    with patch("modules.payment_equipment.register_item", mock_register_item):
        register_tickets(mock_device, sale_dict, 1)

    # Проверяем, что был вызван register_item для взрослого билета
    mock_register_item.assert_any_call(mock_device, "Билет взрослый 12 ч.", 100, 5)
    # Проверяем, что был вызван register_item для детского билета без скидки
    mock_register_item.assert_any_call(mock_device, "Билет детский 12 ч.", 50, 3)


def test_register_tickets_adult_with_discount(
    mock_register_item, sale_dict, mock_device
):
    """Проверка регистрации взрослых билетов с скидкой."""
    with patch("modules.payment_equipment.register_item", mock_register_item):
        register_tickets(mock_device, sale_dict, 1)

    # Проверка, что зарегистрированы взрослые билеты с обычной ценой и с скидкой
    mock_register_item.assert_any_call(mock_device, "Билет взрослый 12 ч.", 100, 3)
    mock_register_item.assert_any_call(mock_device, "Билет взрослый акция 12 ч.", 80, 2)


def test_register_tickets_child_no_discount(mock_register_item, sale_dict, mock_device):
    """Проверка регистрации детских билетов без скидки."""
    sale_dict["detail"][2] = 0  # Убираем скидки на детские билеты
    sale_dict["detail"][3] = 0  # Убираем цену со скидкой для детей

    with patch("modules.payment_equipment.register_item", mock_register_item):
        register_tickets(mock_device, sale_dict, 1)

    # Проверка, что зарегистрированы детские билеты по полной цене
    mock_register_item.assert_any_call(mock_device, "Билет детский 12 ч.", 50, 3)


def test_register_tickets_child_with_discount(
    mock_register_item, sale_dict, mock_device
):
    """Проверка регистрации детских билетов с скидкой."""
    with patch("modules.payment_equipment.register_item", mock_register_item):
        register_tickets(mock_device, sale_dict, 1)

    # Проверка, что зарегистрированы детские билеты с обычной ценой и с скидкой
    mock_register_item.assert_any_call(mock_device, "Билет детский 12 ч.", 50, 2)
    mock_register_item.assert_any_call(mock_device, "Билет детский акция 12 ч.", 40, 1)


def test_register_tickets_type_operation_not_1(
    mock_register_item, sale_dict, mock_device
):
    """Проверка работы функции для типа операции, не равного 1."""
    sale_dict["test_item"] = [
        100,
        2,
    ]  # Добавляем тестовый элемент в словарь для этого случая

    with patch("modules.payment_equipment.register_item", mock_register_item):
        register_tickets(
            mock_device, sale_dict, 2
        )  # Вызов с типом операции, не равным 1

    # Проверяем, что register_item был вызван с нужными параметрами
    mock_register_item.assert_any_call(mock_device, "test_item", 100, 2)


def test_register_tickets_type_operation_1_no_items(
    mock_register_item, sale_dict, mock_device
):
    """Проверка, когда нет элементов для регистрации."""
    sale_dict["kol_adult"] = 0  # Убираем всех взрослых
    sale_dict["kol_child"] = 0  # Убираем всех детей

    with patch("modules.payment_equipment.register_item", mock_register_item):
        register_tickets(mock_device, sale_dict, 1)

    # Убедимся, что ничего не было зарегистрировано
    mock_register_item.assert_not_called()  # Проверяем, что register_item не был вызван


#######################################
# Тестируем handle_document_errors


@pytest.fixture
def mock_device():
    """Фикстура для мока устройства."""
    return MagicMock()


def test_handle_document_errors_success_first_attempt(mock_device):
    """Тест для успешного закрытия документа на первой попытке."""
    # Настроим поведение устройства для успешного закрытия документа
    mock_device.checkDocumentClosed.return_value = (
        0  # Устройство сообщает, что документ закрыт
    )
    mock_device.getParamBool.return_value = True  # Параметр закрытого документа истинен

    # Вызов функции
    result = handle_document_errors(mock_device, retry_count=0, max_retries=3)

    # Проверяем, что возвращаемое значение True (успех)
    assert result is True
    # Проверяем, что cancelReceipt не был вызван
    mock_device.cancelReceipt.assert_not_called()


def test_handle_document_errors_success_after_retries(mock_device):
    """Тест для успешного закрытия документа после нескольких попыток."""
    # Настроим поведение устройства, чтобы сначала документ не закрыт, но через 2 попытки закрывается
    mock_device.checkDocumentClosed.side_effect = [
        1,
        1,
        0,
    ]  # первые две попытки - ошибка, на третьей успех
    mock_device.getParamBool.return_value = True  # Параметр закрытого документа истинен

    # Вызов функции
    result = handle_document_errors(mock_device, retry_count=0, max_retries=3)

    # Проверяем, что возвращаемое значение True (успех)
    assert result is True
    # Проверяем, что cancelReceipt не был вызван
    mock_device.cancelReceipt.assert_not_called()


#######################################
# Тестируем terminal_oplata


# Мокаем функции для тестирования
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.process_success_result")
@patch("modules.payment_equipment.process_terminal_error")
@patch("modules.payment_equipment.handle_error")
@patch("modules.payment_equipment.logger")
def test_terminal_oplata_success(
    mock_logger,
    mock_handle_error,
    mock_process_terminal_error,
    mock_process_success_result,
    mock_run_terminal_command,
):
    """Тест для успешного завершения операции оплаты."""

    # Настроим поведение mock-объектов
    mock_result = MagicMock()
    mock_result.returncode = TERMINAL_SUCCESS_CODE
    mock_run_terminal_command.return_value = mock_result
    mock_process_success_result.return_value = 1  # Успешный результат

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_oplata(amount)

    # Проверяем, что результат равен 1 (успех)
    assert result == 1

    # Проверяем, что логирование было вызвано
    mock_logger.info.assert_called_with(
        f"Статус проведения операции по банковскому терминалу: {TERMINAL_SUCCESS_CODE}"
    )
    mock_process_success_result.assert_called_once()


@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.handle_error")
@patch("modules.payment_equipment.logger")
def test_terminal_oplata_no_response(
    mock_logger, mock_handle_error, mock_run_terminal_command
):
    """Тест для ситуации, когда терминал не отвечает."""

    # Настроим поведение mock-объектов
    mock_run_terminal_command.return_value = None

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_oplata(amount)

    # Проверяем, что результат равен 0 (ошибка)
    assert result == 0

    # Проверяем, что была вызвана обработка ошибки
    mock_handle_error.assert_called_once_with(
        "Нет ответа от терминала",
        "Команда терминала не была выполнена. Проверьте устройство.",
        "Код ошибки: отсутствует",
    )
    mock_logger.error.assert_called_with("Ошибка при выполнении команды терминала")


@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.process_terminal_error")
@patch("modules.payment_equipment.logger")
def test_terminal_oplata_error(
    mock_logger, mock_process_terminal_error, mock_run_terminal_command
):
    """Тест для ситуации, когда команда терминала завершается с ошибкой."""

    # Настроим поведение mock-объектов
    mock_result = MagicMock()
    mock_result.returncode = 2  # Ошибка терминала
    mock_run_terminal_command.return_value = mock_result
    mock_process_terminal_error.return_value = 0  # Код ошибки

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_oplata(amount)

    # Проверяем, что результат равен 0 (ошибка)
    assert result == 0

    # Проверяем, что обработка ошибки терминала была вызвана
    mock_process_terminal_error.assert_called_once_with(2)
    mock_logger.info.assert_called_with(
        f"Статус проведения операции по банковскому терминалу: 2"
    )


#######################################
# Тестируем terminal_return


# Тест для успешного возврата, когда команда выполнена успешно и файл найден
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.check_terminal_file")
@patch("modules.payment_equipment.logger")
def test_terminal_return_success(
    mock_logger, mock_check_terminal_file, mock_run_terminal_command
):
    """Тест для успешного возврата средств по банковскому терминалу."""

    # Настроим поведение mock-объектов
    mock_result = MagicMock()
    mock_result.returncode = TERMINAL_SUCCESS_CODE
    mock_run_terminal_command.return_value = mock_result
    mock_check_terminal_file.return_value = True  # Файл найден

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_return(amount)

    # Проверяем, что результат равен 1 (успех)
    assert result == 1

    # Проверяем, что логирование было вызвано
    mock_logger.info.assert_called_with("Запуск функции terminal_return")
    mock_logger.debug.assert_any_call(
        f"В функцию была передана следующая сумма: {amount}"
    )
    mock_check_terminal_file.assert_called_once_with("ОДОБРЕНО")


# Тест для ситуации, когда терминал не отвечает (result is None)
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.logger")
def test_terminal_return_no_response(mock_logger, mock_run_terminal_command):
    """Тест для случая, когда терминал не отвечает."""

    # Настроим поведение mock-объектов
    mock_run_terminal_command.return_value = None

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_return(amount)

    # Проверяем, что результат равен 0 (ошибка)
    assert result == 0

    # Проверяем, что ошибка была записана в лог
    mock_logger.error.assert_called_with("Ошибка при выполнении команды терминала")


# Тест для ситуации, когда файл не найден (FileNotFoundError)
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.check_terminal_file")
@patch("modules.payment_equipment.logger")
def test_terminal_return_file_not_found(
    mock_logger, mock_check_terminal_file, mock_run_terminal_command
):
    """Тест для случая, когда файл не найден."""

    # Настроим поведение mock-объектов
    mock_result = MagicMock()
    mock_result.returncode = TERMINAL_SUCCESS_CODE
    mock_run_terminal_command.return_value = mock_result
    mock_check_terminal_file.side_effect = FileNotFoundError(
        "Файл не найден"
    )  # Исключение при проверке файла

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_return(amount)

    # Проверяем, что результат равен 0 (ошибка)
    assert result == 0

    # Проверяем, что ошибка была записана в лог
    mock_logger.error.assert_called_with("Файл не найден: Файл не найден")


# Тест для обработки кода возврата TERMINAL_DATA_EXCHANGE (ошибка 4134)
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.windows.info_window")
@patch("modules.payment_equipment.logger")
def test_terminal_return_data_exchange_error(
    mock_logger, mock_info_window, mock_run_terminal_command
):
    """Тест для случая, когда терминал вернул ошибку с кодом 4134."""

    # Настроим поведение mock-объектов
    mock_result = MagicMock()
    mock_result.returncode = TERMINAL_DATA_EXCHANGE
    mock_run_terminal_command.return_value = mock_result

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_return(amount)

    # Проверяем, что результат равен 0 (ошибка)
    assert result == 0

    # Проверяем, что вызвано окно с информацией об ошибке
    mock_info_window.assert_called_once_with(
        "Ошибка при проведении оплаты",
        "Требуется сделать сверку итогов и после этого повторить операцию оплаты",
        "Команда завершена с кодом: 4134",
    )

    # Проверяем, что логирование было вызвано с нужным сообщением
    mock_logger.info.assert_any_call(
        f"Терминал вернул следующий код операции: {TERMINAL_DATA_EXCHANGE}"
    )


#######################################
# Тестируем terminal_canceling


# Тест для успешной операции отмены
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.check_terminal_file")
@patch("modules.payment_equipment.logger")
def test_terminal_canceling_success(
    mock_logger, mock_check_terminal_file, mock_run_terminal_command
):
    """Тест для успешной операции отмены."""

    # Настроим поведение mock-объектов
    mock_result = MagicMock()
    mock_result.returncode = TERMINAL_SUCCESS_CODE
    mock_run_terminal_command.return_value = mock_result
    mock_check_terminal_file.return_value = True  # Файл найден

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_canceling(amount)

    # Проверяем, что результат равен 1 (успех)
    assert result == 1

    # Проверяем, что логирование было вызвано
    mock_logger.info.assert_called_with("Запуск функции terminal_canceling")
    mock_logger.debug.assert_any_call(
        f"В функцию была передана следующая сумма: {amount}"
    )
    mock_check_terminal_file.assert_called_once_with("ОДОБРЕНО")


# Тест для случая, когда команда терминала вернула None (ошибка)
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.logger")
def test_terminal_canceling_command_error(mock_logger, mock_run_terminal_command):
    """Тест для ошибки при выполнении команды терминала."""

    # Настроим поведение mock-объекта
    mock_result = MagicMock()
    mock_result.returncode = None
    mock_run_terminal_command.return_value = mock_result

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_canceling(amount)

    # Проверяем, что результат равен 0 (ошибка)
    assert result == 0

    # Проверяем, что ошибка была записана в лог
    mock_logger.error.assert_called_with("Ошибка при выполнении команды терминала")


# Тест для случая, когда не найден файл
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.check_terminal_file")
@patch("modules.payment_equipment.logger")
def test_terminal_canceling_file_not_found(
    mock_logger, mock_check_terminal_file, mock_run_terminal_command
):
    """Тест для случая, когда файл не найден."""

    # Настроим поведение mock-объектов
    mock_result = MagicMock()
    mock_result.returncode = TERMINAL_SUCCESS_CODE
    mock_run_terminal_command.return_value = mock_result
    mock_check_terminal_file.side_effect = FileNotFoundError("Файл не найден")

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_canceling(amount)

    # Проверяем, что результат равен 0 (ошибка)
    assert result == 0

    # Проверяем, что ошибка была записана в лог
    mock_logger.error.assert_called_with("Файл не найден: Файл не найден")


# Тест для случая, когда терминал вернул код TERMINAL_DATA_EXCHANGE
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.windows.info_window")
@patch("modules.payment_equipment.logger")
def test_terminal_canceling_data_exchange(
    mock_logger, mock_info_window, mock_run_terminal_command
):
    """Тест для случая с кодом возврата TERMINAL_DATA_EXCHANGE."""

    # Настроим поведение mock-объектов
    mock_result = MagicMock()
    mock_result.returncode = TERMINAL_DATA_EXCHANGE
    mock_run_terminal_command.return_value = mock_result

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_canceling(amount)

    # Проверяем, что результат равен 0 (ошибка)
    assert result == 0

    # Проверяем, что была вызвана информационная панель
    mock_info_window.assert_called_once_with(
        "Ошибка при проведении оплаты",
        "Требуется сделать сверку итогов и после этого повторить операцию оплаты",
        "Команда завершена с кодом: 4134",
    )


# Тест для случая с неизвестным кодом возврата
@patch("modules.payment_equipment.run_terminal_command")
@patch("modules.payment_equipment.logger")
def test_terminal_canceling_unknown_error(mock_logger, mock_run_terminal_command):
    """Тест для случая с неизвестным кодом возврата терминала."""

    # Настроим поведение mock-объектов
    mock_result = MagicMock()
    mock_result.returncode = 999  # Неизвестный код возврата
    mock_run_terminal_command.return_value = mock_result

    amount = 100.0

    # Вызовем тестируемую функцию
    result = terminal_canceling(amount)

    # Проверяем, что результат равен 0 (ошибка)
    assert result == 0

    # Проверяем, что ошибка была записана в лог
    mock_logger.error.assert_called_with("Неизвестный код возврата: 999")
