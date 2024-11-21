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
)

# Константы для тестирования
TERMINAL_SUCCESS_CODE = 0  # Код успешной операции терминала
TERMINAL_USER_CANCEL_CODE = 1  # Код отмены операции пользователем
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
# Тестируем terminal_oplata
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


def test_terminal_oplata_success(mock_run_terminal_command, mock_check_terminal_file):
    # Успешный сценарий
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_check_terminal_file.return_value = True

    result = terminal_oplata(100.0)

    assert result == 1
    mock_run_terminal_command.assert_called_once_with(
        "1 10000"
    )  # Ожидаем 10000, а не 100.000
    mock_check_terminal_file.assert_called_once_with(
        "ОДОБРЕНО"
    )  # Проверка для 'ОДОБРЕНО' вместо 'APPROVE'


def test_terminal_oplata_run_command_failure(mock_run_terminal_command):
    # Ошибка выполнения команды
    mock_run_terminal_command.return_value = (
        None  # Моделируем ошибку выполнения команды
    )

    result = terminal_oplata(100.0)

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("1 10000")


@patch("modules.payment_equipment.run_terminal_command")
def test_terminal_oplata_user_cancel(mock_run_terminal_command):
    # Симуляция возврата кода отмены
    mock_terminal_response = MagicMock()
    mock_terminal_response.returncode = (
        TERMINAL_USER_CANCEL_CODE  # Симулируем отмену пользователем
    )

    # Настройка мока
    mock_run_terminal_command.return_value = mock_terminal_response

    # Вызов функции
    result = terminal_oplata(100.0)

    # Логгируем результат
    print(
        f"Test result: {result}"
    )  # Для отладки, чтобы увидеть, что возвращает функция

    # Проверка, что результат равен 0, так как операция была отменена пользователем
    assert result == 0


def test_terminal_oplata_file_not_found(
    mock_run_terminal_command, mock_check_terminal_file
):
    # Файл не найден (например, ошибка в check_terminal_file)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_check_terminal_file.return_value = False  # Не нашли нужное слово в файле

    result = terminal_oplata(100.0)

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("1 10000")
    mock_check_terminal_file.assert_called_once_with("ОДОБРЕНО")  # Ожидаем "ОДОБРЕНО"


def test_terminal_oplata_file_read_error(mock_run_terminal_command):
    # Ошибка при чтении файла (например, файл не существует)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE

    with mock.patch(
        "modules.payment_equipment.check_terminal_file", side_effect=FileNotFoundError
    ):
        result = terminal_oplata(100.0)

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("1 10000")


#######################################
# Тестируем terminal_return
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


def test_terminal_return_success(mock_run_terminal_command, mock_check_terminal_file):
    # Успешный сценарий
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_check_terminal_file.return_value = True

    result = terminal_return(100.0)

    assert result == 1
    mock_run_terminal_command.assert_called_once_with(
        "3 10000"
    )  # Ожидаем 10000, а не 100.000
    mock_check_terminal_file.assert_called_once_with(
        "ОДОБРЕНО"
    )  # Проверка для 'ОДОБРЕНО' вместо 'APPROVE'


def test_terminal_return_run_command_failure(mock_run_terminal_command):
    # Ошибка выполнения команды
    mock_run_terminal_command.return_value = (
        None  # Моделируем ошибку выполнения команды
    )

    result = terminal_return(100.0)

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("3 10000")


def test_terminal_return_file_not_found(
    mock_run_terminal_command, mock_check_terminal_file
):
    # Файл не найден (например, ошибка в check_terminal_file)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_check_terminal_file.return_value = False  # Не нашли нужное слово в файле

    result = terminal_return(100.0)

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("3 10000")
    mock_check_terminal_file.assert_called_once_with("ОДОБРЕНО")  # Ожидаем "ОДОБРЕНО"


def test_terminal_return_file_read_error(mock_run_terminal_command):
    # Ошибка при чтении файла (например, файл не существует)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE

    with mock.patch(
        "modules.payment_equipment.check_terminal_file", side_effect=FileNotFoundError
    ):
        result = terminal_return(100.0)

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("3 10000")


#######################################
# Тестируем terminal_canceling
# Мокируем функцию run_terminal_command
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


def test_terminal_canceling_success(
    mock_run_terminal_command, mock_check_terminal_file
):
    # Успешный сценарий
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_check_terminal_file.return_value = True

    result = terminal_canceling(100.0)

    assert result == 1
    mock_run_terminal_command.assert_called_once_with(
        "8 10000"
    )  # Ожидаем 10000, а не 100.000
    mock_check_terminal_file.assert_called_once_with(
        "ОДОБРЕНО"
    )  # Проверка для 'ОДОБРЕНО' вместо 'APPROVE'


def test_terminal_canceling_run_command_failure(mock_run_terminal_command):
    # Ошибка выполнения команды
    mock_run_terminal_command.return_value = (
        None  # Моделируем ошибку выполнения команды
    )

    result = terminal_canceling(100.0)

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("8 10000")


def test_terminal_canceling_file_not_found(
    mock_run_terminal_command, mock_check_terminal_file
):
    # Файл не найден (например, ошибка в check_terminal_file)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE
    mock_check_terminal_file.return_value = False  # Не нашли нужное слово в файле

    result = terminal_canceling(100.0)

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("8 10000")
    mock_check_terminal_file.assert_called_once_with("ОДОБРЕНО")  # Ожидаем "ОДОБРЕНО"


def test_terminal_canceling_file_read_error(mock_run_terminal_command):
    # Ошибка при чтении файла (например, файл не существует)
    mock_run_terminal_command.return_value.returncode = TERMINAL_SUCCESS_CODE

    with mock.patch(
        "modules.payment_equipment.check_terminal_file", side_effect=FileNotFoundError
    ):
        result = terminal_canceling(100.0)

    assert result == 0
    mock_run_terminal_command.assert_called_once_with("8 10000")


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
