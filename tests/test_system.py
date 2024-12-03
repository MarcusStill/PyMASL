import json
from unittest.mock import MagicMock, patch, mock_open

import pytest

from db.models import Price
from modules.system import System


# Фикстуры
@pytest.fixture
def mock_config_load_coordinates():
    """Фикстура для мокирования конфигурации."""
    config = MagicMock()
    return config


@pytest.fixture
def mock_session():
    """Фикстура для мокирования сессии базы данных."""
    with patch("modules.system.Session") as mock:  # Исправленный путь
        yield mock


@pytest.fixture
def mock_prices():
    """Фикстура для мокирования прайс-листа."""
    return [
        Price(price=100),
        Price(price=200),
        Price(price=300),
        Price(price=400),
        Price(price=500),
        Price(price=600),
        Price(price=700),
        Price(price=800),
        Price(price=900),
    ]


@pytest.fixture
def default_expected_prices():
    """Фикстура для ожидаемых значений по умолчанию."""
    return {
        "ticket_child_1": 100,
        "ticket_child_2": 200,
        "ticket_child_3": 300,
        "ticket_child_week_1": 300,  # По умолчанию
        "ticket_child_week_2": 600,  # По умолчанию
        "ticket_child_week_3": 900,  # По умолчанию
        "ticket_adult_1": 150,  # По умолчанию
        "ticket_adult_2": 200,  # По умолчанию
        "ticket_adult_3": 250,  # По умолчанию
    }


# Фикстура для создания объекта System
@pytest.fixture
def system(mock_session):
    """Фикстура для создания объекта System с мокированием сессии."""
    with patch("modules.system.Config") as mock_config:  # Исправленный путь
        mock_config_instance = mock_config.return_value
        mock_config_instance.get.side_effect = {
            "host": "localhost",
            "port": "5432",
            "database": "test_db",
            "user": "test_user",
            "version": "1.0",
            "log_file": "system.log",
            "kol": 10,
            "pc_1": "PC1",
            "pc_2": "PC2",
        }.get
        with patch("modules.system.load_dotenv"):  # Исправленный путь
            with patch("modules.system.os.getenv", return_value="test_password"):
                return System()


# Тестируем load_coordinates
def test_load_coordinates_invalid_file_path(mock_config_load_coordinates):
    """Тест на некорректный путь к файлу координат в конфигурации."""
    mock_config_load_coordinates.get.return_value = 12345  # Не строка
    system = System()

    # Теперь ожидаем ошибку TypeError
    with pytest.raises(TypeError, match="Путь к файлу координат должен быть строкой."):
        system.load_coordinates(mock_config_load_coordinates)


def test_load_coordinates_missing_key_in_config(mock_config_load_coordinates):
    """Тест на отсутствие ключа 'ticket_coordinates_file' в конфигурации."""
    mock_config_load_coordinates.get.return_value = None
    system = System()

    with pytest.raises(
        KeyError, match="Не указан путь к файлу координат в конфигурации."
    ):
        system.load_coordinates(mock_config_load_coordinates)


def test_load_coordinates_file_not_found(mock_config_load_coordinates):
    """Тест на несуществующий файл с координатами."""
    mock_config_load_coordinates.get.return_value = "invalid/path/to/coordinates.json"
    system = System()

    with patch("os.path.isfile", return_value=False):
        with pytest.raises(
            FileNotFoundError,
            match="Файл с координатами 'invalid/path/to/coordinates.json' не найден.",
        ):
            system.load_coordinates(mock_config_load_coordinates)


def test_load_coordinates_invalid_json(mock_config_load_coordinates):
    """Тест на некорректный формат JSON в файле."""
    mock_config_load_coordinates.get.return_value = "valid/path/to/coordinates.json"
    system = System()

    with patch("os.path.isfile", return_value=True):
        with patch("builtins.open", mock_open(read_data="invalid_json")):
            with pytest.raises(json.JSONDecodeError):
                system.load_coordinates(mock_config_load_coordinates)


def test_load_coordinates_missing_coordinates_key(mock_config_load_coordinates):
    """Тест на отсутствие ключа 'coordinates' в JSON файле."""
    mock_config_load_coordinates.get.return_value = "valid/path/to/coordinates.json"
    system = System()

    with patch("os.path.isfile", return_value=True):
        invalid_json = json.dumps({"invalid_key": "value"})
        with patch("builtins.open", mock_open(read_data=invalid_json)):
            with pytest.raises(
                KeyError, match="В конфигурации отсутствует ключ 'coordinates'."
            ):
                system.load_coordinates(mock_config_load_coordinates)


def test_load_coordinates_successful(mock_config_load_coordinates):
    """Тест на успешную загрузку координат из корректного JSON файла."""
    mock_config_load_coordinates.get.return_value = "valid/path/to/coordinates.json"
    system = System()

    valid_json = json.dumps(
        {
            "coordinates": {
                "name": {"x": 10, "y": 20},
                "surname": {"x": 15, "y": 25},
                "age": {"x": 20, "y": 30},
            }
        }
    )

    with patch("os.path.isfile", return_value=True):
        with patch("builtins.open", mock_open(read_data=valid_json)):
            coordinates = system.load_coordinates(mock_config_load_coordinates)
            expected_coordinates = {
                "name": {"x": 10, "y": 20},
                "surname": {"x": 15, "y": 25},
                "age": {"x": 20, "y": 30},
            }
            assert coordinates == expected_coordinates


# Тестируем get_price
def check_prices(system, expected_prices):
    """Проверка прайс-листа в системе с детальным выводом при ошибке."""
    for key, expected_value in expected_prices.items():
        assert (
            system.price[key] == expected_value
        ), f"Ошибка для {key}: ожидалось {expected_value}, но получено {system.price[key]}"


# Тесты остаются те же, что и у вас, но теперь с улучшением диагностики в `check_prices`
@patch("modules.system.Session")
def test_get_price_with_enough_records(
    mock_session, system, mock_prices, default_expected_prices
):
    """Тест на достаточное количество записей в прайс-листе."""
    mock_session.return_value.__enter__.return_value.query.return_value.order_by.return_value.all.return_value = (
        mock_prices
    )
    system.get_price()

    expected_prices = {
        "ticket_child_1": 100,
        "ticket_child_2": 200,
        "ticket_child_3": 300,
        "ticket_child_week_1": 400,
        "ticket_child_week_2": 500,
        "ticket_child_week_3": 600,
        "ticket_adult_1": 700,
        "ticket_adult_2": 800,
        "ticket_adult_3": 900,
    }

    check_prices(system, expected_prices)


@patch("modules.system.Session")
def test_get_price_with_insufficient_records(
    mock_session, system, default_expected_prices
):
    """Тест на недостаточное количество записей в прайс-листе."""
    mock_prices = [Price(price=100), Price(price=200), Price(price=300)]
    mock_session.return_value.__enter__.return_value.query.return_value.order_by.return_value.all.return_value = (
        mock_prices
    )
    system.get_price()

    updated_prices = default_expected_prices.copy()
    updated_prices["ticket_child_week_1"] = 300
    updated_prices["ticket_child_week_2"] = 600
    updated_prices["ticket_child_week_3"] = 900
    updated_prices["ticket_adult_1"] = 150
    updated_prices["ticket_adult_2"] = 200
    updated_prices["ticket_adult_3"] = 250

    check_prices(system, updated_prices)


@patch("modules.system.Session")
def test_get_price_with_empty_result(mock_session, system, default_expected_prices):
    """Тест на пустой результат (прайс-лист пуст)."""
    mock_session.return_value.__enter__.return_value.query.return_value.order_by.return_value.all.return_value = (
        []
    )

    # Проверяем обновление цен при пустом результату из базы
    system.get_price()

    updated_prices = default_expected_prices.copy()
    updated_prices["ticket_child_1"] = 250
    updated_prices["ticket_child_2"] = 500
    updated_prices["ticket_child_3"] = 750
    updated_prices["ticket_child_week_1"] = 300
    updated_prices["ticket_child_week_2"] = 600
    updated_prices["ticket_child_week_3"] = 900
    updated_prices["ticket_adult_1"] = 150
    updated_prices["ticket_adult_2"] = 200
    updated_prices["ticket_adult_3"] = 250

    # Проверяем, что все ключи прайс-листа были корректно обновлены
    check_prices(system, updated_prices)
