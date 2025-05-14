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
        "ticket_child_1": 100 ^ 42,
        "ticket_child_2": 200 ^ 42,
        "ticket_child_3": 300 ^ 42,
        "ticket_child_week_1": 400 ^ 42,
        "ticket_child_week_2": 500 ^ 42,
        "ticket_child_week_3": 600 ^ 42,
        "ticket_adult_1": 700 ^ 42,
        "ticket_adult_2": 800 ^ 42,
        "ticket_adult_3": 900 ^ 42,
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
    updated_prices["ticket_child_1"] = 100 ^ 42  # 78
    updated_prices["ticket_child_2"] = 200 ^ 42  # 234
    updated_prices["ticket_child_3"] = 300 ^ 42  # 334

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

#######################################
# Тестируем get_slip_data

# Фикстуры для тестов get_slip_data
@pytest.fixture
def mock_session():
    """Фикстура для мокирования сессии базы данных."""
    with patch("modules.system.Session") as mock:
        yield mock

@pytest.fixture
def slip_processor():
    """Фикстура для создания тестируемого объекта."""
    from modules.system import System
    return System()

@pytest.fixture
def invalid_slip():
    return "Invalid slip format without any required data"

# Вспомогательная фикстура для мокирования запроса
@pytest.fixture
def mock_db_query(mock_session):
    def _mock_db_query(return_value):
        # Мокируем поведение сессии так, чтобы .execute().scalars().one() возвращали строку слипа
        mock_query = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.one.return_value = return_value  # Передаем строку слипа напрямую

        # Строим цепочку вызовов: execute().scalars().one()
        mock_session.return_value.__enter__.return_value.execute.return_value = mock_query
        mock_query.scalars.return_value = mock_scalars

        return mock_session
    return _mock_db_query

# Фикстуры с примерами слипов
@pytest.fixture
def mastercard_slip():
    return """
            Umbrella Corporation            

ПАО БАНК                  Оплата
Т: 12345678           М:000000000001
MASTERCARD            A0000000000000
Карта:(E1)          ************1234
Сумма (Руб):                  1.00
Комиссия за операцию - 0 Руб.
              ОДОБРЕНО
К/А: 123456      RRN:   000000000001
    Подпись клиента не требуется    
0123456789012345678901234567890123456
===================================="""

@pytest.fixture
def visa_slip():
    return """
            Umbrella Corporation            

ПАО БАНК                  Оплата
Т: 12345678           М:000000000001
VISA                  A0000000000000
Карта:(E1)          ************1234
Сумма (Руб):                  1.00
Комиссия за операцию - 0 Руб.
              ОДОБРЕНО
К/А: 123456      RRN:   000000000001
    Подпись клиента не требуется    
0123456789012345678901234567890123456
===================================="""

@pytest.fixture
def mir_slip():
    return """
            Umbrella Corporation            

ПАО БАНК                  Оплата
Т: 12345678           М:000000000001
MIR                   A0000000000000
Карта:(E4)       ***************1234
Сумма (Руб):                 1.00
Комиссия за операцию - 0 Руб.
              ОДОБРЕНО
К/А: 123456      RRN:   000000000001
  Проверено на устройстве клиента   
0123456789012345678901234567890123456
===================================="""

@pytest.fixture
def qr_slip():
    return """
            Umbrella Corporation            

ПАО БАНК               Оплата QR
Т: 12345678           М:000000000001
Терминал QR:                00000001
Номер QR:                 0000000001
Банк плательщика:           БАНК
Заказ:
    352dba227a944a44b1ffa19eaf37f379
Карта:              ************1234
Сумма (Руб):                 1.00
              ОДОБРЕНО
К/А: 123456      RRN:   000000000001
  Проверено на устройстве клиента   
0123456789012345678901234567890123456
===================================="""

@pytest.fixture
def mir_pay_slip():
    return """
            Umbrella Corporation            

ПАО БАНК                  Оплата
Т: 12345678           М:000000000001
MIR PAY               A0000000000000
Карта:(E4)       ***************1234
Сумма (Руб):                 1.00
Комиссия за операцию - 0 Руб.
              ОДОБРЕНО
К/А: 123456      RRN:   000000000001
  Проверено на устройстве клиента   
0123456789012345678901234567890123456
===================================="""

@pytest.fixture
def mir_classic_slip():
    return """
            Umbrella Corporation            

ПАО БАНК                  Оплата
Т: 12345678           М:000000000001
MIR Classic CRD       A0000000000000
Карта:(E)           ************1234
Сумма (Руб):                  1.00
Комиссия за операцию - 0 Руб.
              ОДОБРЕНО
К/А: 123456      RRN:   000000000001
    Подпись клиента не требуется    
0123456789012345678901234567890123456"""

# Тесты для каждого типа слипа
def test_mastercard_slip(slip_processor, mock_db_query, mastercard_slip):
    # Мокируем возврат строки слипа напрямую
    mock_db_query(mastercard_slip.strip())  # передаем строку напрямую

    # Получаем результат
    card_tail, merchant_id, rrn_value, full_slip = slip_processor.get_slip_data(1)

    # Проверяем, что данные корректны
    assert card_tail == "1234", f"Ожидалось '1234', но получено '{card_tail}'"
    assert merchant_id == "000000000001", f"Ожидалось '000000000001', но получено '{merchant_id}'"
    assert rrn_value == "000000000001", f"Ожидалось '000000000001', но получено '{rrn_value}'"
    assert full_slip == mastercard_slip.strip(), f"Ожидался полный слип, но получено '{full_slip}'"

def test_visa_slip(slip_processor, mock_db_query, visa_slip):
    # Мокируем возврат строки слипа напрямую
    mock_db_query(visa_slip.strip())  # передаем строку напрямую

    # Получаем результат
    card_tail, merchant_id, rrn_value, full_slip = slip_processor.get_slip_data(1)

    # Проверяем, что данные корректны
    assert card_tail == "1234", f"Ожидалось '1234', но получено '{card_tail}'"
    assert merchant_id == "000000000001", f"Ожидалось '000000000001', но получено '{merchant_id}'"
    assert rrn_value == "000000000001", f"Ожидалось '000000000001', но получено '{rrn_value}'"
    assert full_slip == visa_slip.strip(), f"Ожидался полный слип, но получено '{full_slip}'"

def test_mir_slip(slip_processor, mock_db_query, mir_slip):
    mock_db_query(mir_slip.strip())
    card_tail, merchant_id, rrn_value, full_slip = slip_processor.get_slip_data(1)

    assert card_tail == "1234"
    assert merchant_id == "000000000001"
    assert rrn_value == "000000000001"
    assert full_slip == mir_slip.strip()

def test_qr_slip(slip_processor, mock_db_query, qr_slip):
    mock_db_query(qr_slip.strip())
    card_tail, merchant_id, rrn_value, full_slip = slip_processor.get_slip_data(1)

    assert card_tail == "1234"
    assert merchant_id == "000000000001"
    assert rrn_value == "000000000001"
    assert full_slip == qr_slip.strip()

def test_mir_pay_slip(slip_processor, mock_db_query, mir_pay_slip):
    mock_db_query(mir_pay_slip.strip())
    card_tail, merchant_id, rrn_value, full_slip = slip_processor.get_slip_data(1)

    assert card_tail == "1234"
    assert merchant_id == "000000000001"
    assert rrn_value == "000000000001"
    assert full_slip == mir_pay_slip.strip()

def test_mir_classic_slip(slip_processor, mock_db_query, mir_classic_slip):
    mock_db_query(mir_classic_slip.strip())
    card_tail, merchant_id, rrn_value, full_slip = slip_processor.get_slip_data(1)

    assert card_tail == "1234"
    assert merchant_id == "000000000001"
    assert rrn_value == "000000000001"
    assert full_slip == mir_classic_slip.strip()

def test_invalid_slip(slip_processor, invalid_slip, mock_db_query):
    # Мокируем возврат невалидного слипа
    mock_db_query(invalid_slip.strip())  # фикстура передана как параметр

    card_tail, merchant_id, rrn_value, full_slip = slip_processor.get_slip_data(1)

    assert card_tail == ""
    assert merchant_id == ""
    assert rrn_value == ""
    assert full_slip == invalid_slip.strip()

def test_empty_slip(slip_processor, mock_db_query):
    # Мокируем возврат пустого слипа
    mock_db_query("")  # фикстура передана как параметр

    card_tail, merchant_id, rrn_value, full_slip = slip_processor.get_slip_data(1)

    assert card_tail == ""
    assert merchant_id == ""
    assert rrn_value == ""
    assert full_slip == ""
