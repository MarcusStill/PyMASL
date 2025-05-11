import datetime
import os
import tempfile
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import reportlab.pdfgen.canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from modules import system
from modules.otchet import generate_saved_tickets, generate_ticket_report_table, otchet_administratora, safe_int, \
    format_date_range, otchet_kassira, process_sales_and_returns, process_ticket_stats, get_ticket_type
from modules.system import System


# Тестируем generate_saved_tickets
@pytest.fixture
def sample_clients():
    return [
        ('Молчанова', 'Аделия', 1, 450, 'м', 584, 9, 3, 50, datetime.datetime(2025, 5, 4, 10, 14, 7)),
        ('Бесплатов', 'Андрей', 1, 0, 'м', 111, 3, 2, 30, datetime.datetime(2025, 5, 4, 12, 0, 0)),
        ('Неидущий', 'Николай', 0, 500, 'н', 222, 20, 3, 0, datetime.datetime(2025, 5, 4, 15, 0, 0)),
        ('Сидорова', 'Мария', 0, 600, '', 333, 25, 1, 0, datetime.datetime(2025, 5, 4, 16, 0, 0)),
    ]

@pytest.fixture
def mock_coordinates():
    return {
        'surname': {'x': 10, 'y': 10},
        'name': {'x': 20, 'y': 10},
        'age': {'x': 30, 'y': 10},
        'duration': {'x': 40, 'y': 10},
        'date': {'x': 50, 'y': 10},
        'price': {'x': 60, 'y': 10},
        'guest': {'x': 70, 'y': 10},
        'city': {'x': 80, 'y': 10},
        'place': {'x': 90, 'y': 10},
        'ticket_type': {'x': 100, 'y': 10},
        'notes': {'x': 110, 'y': 10},
        'talents': {'x': 120, 'y': 10},
        'qr_code': {'x': 130, 'y': 10},
    }

@pytest.mark.parametrize("font_path", ["files/DejaVuSerif.ttf"])
def test_generate_saved_tickets_creates_pdf(monkeypatch, sample_clients, mock_coordinates, font_path):
    # Подмена метода System.load_coordinates
    monkeypatch.setattr("modules.system.System.load_coordinates", lambda self, config=None: mock_coordinates)
    # Удалим PDF перед тестом, если существует
    pdf_path = "./ticket.pdf"
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    # Регистрация шрифта
    pdfmetrics.registerFont(TTFont("DejaVuSerif", font_path))
    # Запуск функции
    generate_saved_tickets(sample_clients)
    # Проверка
    assert os.path.exists(pdf_path), "Файл ticket.pdf не был создан"
    # Дополнительно можно проверить, что файл не пустой
    assert os.path.getsize(pdf_path) > 0, "Файл ticket.pdf пустой"

#######################################
# Тестируем generate_ticket_report_table
def test_generate_ticket_report_table_empty():
    result = generate_ticket_report_table({})

    # заголовок + 14 пустых категорий + 7 агрегатов = 22 строки
    assert len(result) == 1 + 14 + 7
    assert result[0] == ["№\n п/п", "Тип\nбилета", "Цена,\n руб.", "Количество,\n шт.", "Стоимость,\n руб."]
    for row in result[1:15]:  # категории без данных
        assert row[2:] == ["-", 0, 0]
    for agg_row in result[15:]:
        assert agg_row[-2] == 0

def test_generate_ticket_report_table_partial():
    summary = {
        "Взрослый, 1 ч.": {
            "300": {"count": 2, "total_price": 600}
        }
    }
    result = generate_ticket_report_table(summary)

    # Проверка строки с билетом
    row = result[1]
    assert row == ["1", "Взрослый, 1 ч.", "300", 2, 600]

    # Проверка агрегатов
    adult_total = result[-7]
    assert adult_total == ["", "Всего взрослых билетов", "", 2, 600]

    all_total = result[-1]
    assert all_total[3] == 2
    assert all_total[4] == 600

def test_generate_ticket_report_table_full():
    summary = {
        "Взрослый, 1 ч.": {"300": {"count": 2, "total_price": 600}},
        "Детский, 1 ч.": {"200": {"count": 1, "total_price": 200}},
        "Многодетный взрослый, 1 ч.": {"250": {"count": 1, "total_price": 250}},
        "Многодетный детский, 1 ч.": {"150": {"count": 1, "total_price": 150}},
        "Инвалид, 3 ч.": {"0": {"count": 1, "total_price": 0}},
        "Сопровождающий, 3 ч.": {"0": {"count": 1, "total_price": 0}},
    }
    result = generate_ticket_report_table(summary)

    # Проверка агрегатов
    assert result[-7][4] == 600  # взрослые
    assert result[-6][4] == 200  # детские
    assert result[-5][4] == 250  # многодетные взрослые
    assert result[-4][4] == 150  # многодетные детские
    assert result[-3][3] == 1    # инвалид
    assert result[-2][3] == 1    # сопровождающий

    # Итого
    assert result[-1][3] == 7
    assert result[-1][4] == 600 + 200 + 250 + 150

def test_generate_ticket_report_table_aggregation():
    summary = {
        "Взрослый, 2 ч.": {"400": {"count": 3, "total_price": 1200}},
        "Детский, 2 ч.": {"250": {"count": 2, "total_price": 500}},
        "Многодетный детский, 2 ч.": {"150": {"count": 1, "total_price": 150}},
    }
    result = generate_ticket_report_table(summary)

    # Проверка итогов
    assert result[-7] == ["", "Всего взрослых билетов", "", 3, 1200]
    assert result[-6] == ["", "Всего детских билетов", "", 2, 500]
    assert result[-5] == ["", "Всего многодетных взрослых билетов", "", 0, 0]
    assert result[-4] == ["", "Всего многодетных детских билетов", "", 1, 150]

    total_row = result[-1]
    assert total_row[3] == 6  # общее количество
    assert total_row[4] == 1200 + 500 + 150

#######################################
# Тестируем otchet_administratora

# Тестовые данные
ticket_summary_sample = {
    "Взрослый, 1 ч.": {
        "300": {"count": 2, "total_price": 600}
    },
    "Детский, 2 ч.": {
        "200": {"count": 3, "total_price": 600}
    },
    "Инвалид, 3 ч.": {
        "0": {"count": 1, "total_price": 0}
    }
}

def test_otchet_administratora_creates_pdf(monkeypatch):
    # Создаем временный файл
    with tempfile.TemporaryDirectory() as tmpdirname:
        pdf_path = os.path.join(tmpdirname, "otchet.pdf")

        # Сохраняем оригинальный Canvas
        original_canvas = rl_canvas.Canvas

        # Обертка над оригинальным Canvas, чтобы изменить путь
        def mocked_canvas(path, *args, **kwargs):
            return original_canvas(pdf_path, *args, **kwargs)

        # Мокаем только в модуле otchet
        import modules.otchet as otchet_module
        monkeypatch.setattr(otchet_module.canvas, "Canvas", mocked_canvas)

        # Вызов функции
        date_1 = "2024-01-01 00:00:00"
        date_2 = "2024-01-01 23:59:59"
        values = ticket_summary_sample

        otchet_administratora(date_1, date_2, values)

        # Проверка существования и содержимого файла
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 100  # Убедимся, что PDF не пустой

#######################################
# Тестируем safe_int
def test_safe_int_with_valid_integer():
    assert safe_int(10) == 10  # Проверка с целым числом
    assert safe_int('100') == 100  # Проверка с числовой строкой
    assert safe_int('-50') == -50  # Проверка с отрицательным числом в виде строки


def test_safe_int_with_invalid_values():
    assert safe_int('abc') == 0  # Проверка с некорректной строкой
    assert safe_int(None) == 0  # Проверка с None
    assert safe_int('None') == 0  # Проверка со строкой 'None'
    assert safe_int([]) == 0  # Проверка с пустым списком
    assert safe_int({}) == 0  # Проверка с пустым словарем
    assert safe_int(set()) == 0  # Проверка с пустым множеством
    assert safe_int(('tuple',)) == 0  # Проверка с кортежем


def test_safe_int_with_zero():
    assert safe_int(0) == 0  # Проверка с нулем
    assert safe_int('0') == 0  # Проверка с нулем в виде строки


def test_safe_int_with_float():
    assert safe_int(10.5) == 10  # Проверка с числом с плавающей точкой
    assert safe_int('10.5') == 10  # Проверка с числом с плавающей точкой в виде строки


def test_safe_int_with_boolean():
    assert safe_int(True) == 1  # Проверка с булевым значением True
    assert safe_int(False) == 0  # Проверка с булевым значением False
    assert safe_int('True') == 0  # Проверка с строкой 'True', которая не является целым числом
    assert safe_int('False') == 0  # Проверка с строкой 'False', которая не является целым числом

#######################################
# Тестируем format_date_range
# Тест 1: Проверка преобразования дат с использованием стандартных форматов
def test_format_date_range_default_formats():
    date1_str = "2025-05-07 14:30:00"
    date2_str = "2025-05-08 16:45:00"

    expected_dt1 = "07-05-2025"
    expected_dt2 = "08-05-2025"

    result = format_date_range(date1_str, date2_str)
    assert result == (expected_dt1, expected_dt2)

# Тест 2: Проверка с различными форматами входных и выходных дат
def test_format_date_range_custom_formats():
    date1_str = "2025-05-07 14:30:00"
    date2_str = "2025-05-08 16:45:00"
    input_format = "%Y-%m-%d %H:%M:%S"
    output_format = "%m/%d/%Y"

    expected_dt1 = "05/07/2025"
    expected_dt2 = "05/08/2025"

    result = format_date_range(date1_str, date2_str, input_format, output_format)
    assert result == (expected_dt1, expected_dt2)

# Тест 3: Проверка с одинаковыми датами
def test_format_date_range_same_dates():
    date1_str = "2025-05-07 14:30:00"
    date2_str = "2025-05-07 16:45:00"

    expected_dt1 = "07-05-2025"
    expected_dt2 = "07-05-2025"

    result = format_date_range(date1_str, date2_str)
    assert result == (expected_dt1, expected_dt2)

# Тест 4: Проверка с другими строками форматов (например, с годами и месяцами)
def test_format_date_range_with_other_format():
    date1_str = "2025-05-07 14:30:00"
    date2_str = "2026-06-08 16:45:00"
    input_format = "%Y-%m-%d %H:%M:%S"
    output_format = "%Y/%m/%d"

    expected_dt1 = "2025/05/07"
    expected_dt2 = "2026/06/08"

    result = format_date_range(date1_str, date2_str, input_format, output_format)
    assert result == (expected_dt1, expected_dt2)

# Тест 5: Проверка с ошибочными датами (неправильный формат)
def test_format_date_range_invalid_date_format():
    date1_str = "2025-05-07 14:30:00"
    date2_str = "2025-05-08 16:45:00"
    input_format = "%Y/%m/%d %H:%M:%S"  # Неверный формат

    with pytest.raises(ValueError):  # Ожидаем ошибку, так как формат даты не совпадает
        format_date_range(date1_str, date2_str, input_format)

# Тест 6: Проверка с пустыми строками
def test_format_date_range_empty_strings():
    date1_str = ""
    date2_str = ""

    with pytest.raises(ValueError):  # Ожидаем ошибку из-за пустых строк
        format_date_range(date1_str, date2_str)

#######################################
# Тестируем otchet_kassira
# Тест 1: Проверка создания PDF-отчета
def test_otchet_kassira_creates_pdf():
    val = [1000, 500, 100, 50]  # Пример данных
    date1 = "2025-05-01 00:00:00"
    date2 = "2025-05-07 23:59:59"

    # Создаем мок-объект для kassir
    kassir_mock = MagicMock()
    kassir_mock.last_name = "Иванов"
    kassir_mock.first_name = "Иван"
    kassir_mock.middle_name = "Иванович"

    # Вызов функции
    otchet_kassira(val, date1, date2, kassir_mock)

    # Проверка, что файл создан
    assert os.path.exists("./otchet.pdf")  # Проверяем, что файл otchet.pdf существует

# Тест 2: Проверка обработки данных с корректными значениями
def test_otchet_kassira_correct_values():
    val = [1000, 500, 100, 50]  # Пример данных
    date1 = "2025-05-01 00:00:00"
    date2 = "2025-05-07 23:59:59"

    kassir_mock = MagicMock()
    kassir_mock.last_name = "Иванов"
    kassir_mock.first_name = "Иван"
    kassir_mock.middle_name = "Иванович"

    # Вызов функции
    otchet_kassira(val, date1, date2, kassir_mock)

    # Проверка, что файл создан
    assert os.path.exists("./otchet.pdf")  # Проверяем, что файл otchet.pdf существует

# Тест 3: Проверка на некорректные значения (например, None)
def test_otchet_kassira_invalid_values():
    val = [None, None, None, None]  # Неверные данные
    date1 = "2025-05-01 00:00:00"
    date2 = "2025-05-07 23:59:59"

    kassir_mock = MagicMock()
    kassir_mock.last_name = "Иванов"
    kassir_mock.first_name = "Иван"
    kassir_mock.middle_name = "Иванович"

    # Вызов функции
    otchet_kassira(val, date1, date2, kassir_mock)

    # Проверка, что файл создан
    assert os.path.exists("./otchet.pdf")  # Проверяем, что файл otchet.pdf существует
    # Также можно проверять, что сумма вернулась как 0 или другое значение для некорректных данных
    # Но для этого можно внедрить логику обработки ошибок в саму функцию, если она не обрабатывает такие случаи

# Тест 4: Проверка на ошибку при отсутствии данных
def test_otchet_kassira_missing_data():
    val = []  # Пустой список данных
    date1 = "2025-05-01 00:00:00"
    date2 = "2025-05-07 23:59:59"

    kassir_mock = MagicMock()
    kassir_mock.last_name = "Иванов"
    kassir_mock.first_name = "Иван"
    kassir_mock.middle_name = "Иванович"

    # Вызов функции
    otchet_kassira(val, date1, date2, kassir_mock)

    # Проверка, что файл создан
    assert os.path.exists("./otchet.pdf")  # Проверяем, что файл otchet.pdf существует

#######################################
# Тестируем process_sales_and_returns

# Тест 1: Проверка обработки простых данных
@patch('modules.otchet.system.pcs', {'кассир_1': {}, 'кассир_2': {}})
def test_process_sales_and_returns_basic():
    sales = [
        ("кассир_1", 1, 1000),
        ("кассир_1", 2, 2000),
        ("кассир_2", 1, 1500),
    ]
    sales_return = [
        ("кассир_1", 1, 500, 2),
        ("кассир_1", 2, 1000, 4),
        ("кассир_2", 1, 300, 6),
    ]

    result = process_sales_and_returns(sales, sales_return)

    assert result == [
        ("кассир_1", 1000, 2000, None, 500, 1000, 1500),
        ("кассир_2", 1500, 0, None, 300, 0, 300),
        ("Итого", 2500, 2000, 4500, None, None, 1800)
    ]

# Тест 2: Проверка обработки пустых данных
@patch('modules.otchet.system.pcs', {'кассир_1': {}, 'кассир_2': {}})
def test_process_sales_and_returns_empty():
    sales = []
    sales_return = []

    result = process_sales_and_returns(sales, sales_return)

    assert result == [
        ("кассир_1", 0, 0, None, 0, 0, 0),
        ("кассир_2", 0, 0, None, 0, 0, 0),
        ("Итого", 0, 0, 0, None, None, 0)
    ]

# Тест 3: Проверка обработки данных без возвратов
@patch('modules.otchet.system.pcs', {'кассир_1': {}, 'кассир_2': {}})
def test_process_sales_and_returns_no_returns():
    sales = [
        ("кассир_1", 1, 1000),
        ("кассир_2", 2, 1500),
    ]
    sales_return = []

    result = process_sales_and_returns(sales, sales_return)

    assert result == [
        ("кассир_1", 1000, 0, None, 0, 0, 0),
        ("кассир_2", 0, 1500, None, 0, 0, 0),
        ("Итого", 1000, 1500, 2500, None, None, 0)
    ]

# Тест 4: Проверка обработки данных с отсутствующими кассовыми аппаратами в возвратах
@patch('modules.otchet.system.pcs', {'кассир_1': {}, 'кассир_2': {}})
def test_process_sales_and_returns_missing_pc_in_returns():
    sales = [
        ("кассир_1", 1, 1000),
        ("кассир_2", 2, 1500),
    ]
    sales_return = [
        ("кассир_3", 1, 500, 2),  # Кассир_3 не существует в sales
    ]

    result = process_sales_and_returns(sales, sales_return)

    assert result == [
        ("кассир_1", 1000, 0, None, 0, 0, 0),
        ("кассир_2", 0, 1500, None, 0, 0, 0),
        ("Итого", 1000, 1500, 2500, None, None, 0)
    ]

# Тест 5: Проверка обработки данных с некорректными значениями
@patch('modules.otchet.system.pcs', {'кассир_1': {}, 'кассир_2': {}})
def test_process_sales_and_returns_invalid_values():
    sales = [
        ("кассир_1", 1, 1000),
        ("кассир_1", 3, 2000),  # попадёт как наличные
    ]
    sales_return = [
        ("кассир_1", 1, 500, 2),
        ("кассир_1", 3, 1000, 4),  # попадёт как возврат по наличным
    ]

    result = process_sales_and_returns(sales, sales_return)

    assert result == [
        ("кассир_1", 1000, 2000, None, 500, 1000, 1500),
        ("кассир_2", 0, 0, None, 0, 0, 0),
        ("Итого", 1000, 2000, 3000, None, None, 1500)
    ]

#######################################
# Тестируем process_ticket_stats

system = System()

@pytest.fixture
def setup_system_ticket_stats():
    # Настройка фикстуры, сбрасывающей состояние перед каждым тестом
    if hasattr(system, 'ticket_price_summary'):
        delattr(system, 'ticket_price_summary')
    yield system
    # Сброс состояния после каждого теста
    if hasattr(system, 'ticket_price_summary'):
        delattr(system, 'ticket_price_summary')

def test_normal_case(setup_system_ticket_stats):
    # Подготовка тестовых данных
    tickets = [
        (0, 1, "-", None, None, 100),  # Взрослый, 1 ч.
        (0, 2, "-", None, None, 100),  # Взрослый, 2 ч.
        (1, 1, "-", None, None, 50),   # Детский, 1 ч.
        (1, 3, "-", None, None, 50),   # Детский, 3 ч.
        (0, 1, "м", None, None, 80),   # Многодетный взрослый, 1 ч.
        (1, 2, "м", None, None, 40),   # Многодетный детский, 2 ч.
        (0, 3, "и", None, None, 0),    # Инвалид, 3 ч.
        (0, 3, "с", None, None, 0),    # Сопровождающий, 3 ч.
    ]

    # Ожидаемый результат
    expected = [
        ("взрослый", {"sum": 2, "t_1": 1, "t_2": 1, "t_3": 0}),
        ("детский", {"sum": 2, "t_1": 1, "t_2": 0, "t_3": 1}),
        ("многодетный взр.", {"sum": 1, "t_1": 1, "t_2": 0, "t_3": 0}),
        ("многодетный дет.", {"sum": 1, "t_1": 0, "t_2": 1, "t_3": 0}),
        ("инвалид", {"sum": 1, "t_1": 0, "t_2": 0, "t_3": 1}),
        ("сопровождающий", {"sum": 1, "t_1": 0, "t_2": 0, "t_3": 1}),
    ]

    # Вызов функции и проверка
    result = process_ticket_stats(tickets)
    assert result == expected

    # Проверка сводки по ценам
    assert hasattr(system, 'ticket_price_summary')
    price_summary = system.ticket_price_summary
    assert price_summary["Взрослый, 1 ч."][100]["count"] == 1
    assert price_summary["Взрослый, 1 ч."][100]["total_price"] == 100
    assert price_summary["Детский, 1 ч."][50]["count"] == 1
    assert price_summary["Детский, 1 ч."][50]["total_price"] == 50

def test_empty_input():
    tickets = []
    expected = [
        ("взрослый", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("детский", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный взр.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный дет.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("инвалид", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("сопровождающий", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
    ]
    result = process_ticket_stats(tickets)
    assert result == expected

def test_unknown_description():
    tickets = [
        (0, 1, "unknown", None, None, 100),  # Неизвестное описание
        (0, 2, "-", None, None, 100),         # Корректный билет
    ]

    expected = [
        ("взрослый", {"sum": 1, "t_1": 0, "t_2": 1, "t_3": 0}),
        ("детский", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный взр.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный дет.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("инвалид", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("сопровождающий", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
    ]

    result = process_ticket_stats(tickets)
    assert result == expected

def test_invalid_arrival_time():
    tickets = [
        (0, 4, "-", None, None, 100),  # Некорректное время пребывания
        (0, 1, "-", None, None, 100),   # Корректный билет
    ]

    expected = [
        ("взрослый", {"sum": 1, "t_1": 1, "t_2": 0, "t_3": 0}),
        ("детский", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный взр.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный дет.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("инвалид", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("сопровождающий", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
    ]

    result = process_ticket_stats(tickets)
    assert result == expected

def test_multiple_tickets_same_category(setup_system_ticket_stats):
    tickets = [
        (0, 1, "-", None, None, 100),
        (0, 1, "-", None, None, 100),
        (0, 1, "-", None, None, 100),
    ]

    expected = [
        ("взрослый", {"sum": 3, "t_1": 3, "t_2": 0, "t_3": 0}),
        ("детский", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный взр.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный дет.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("инвалид", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("сопровождающий", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
    ]

    result = process_ticket_stats(tickets)
    assert result == expected

    # Проверка сводки по ценам
    assert hasattr(system, 'ticket_price_summary')
    price_summary = system.ticket_price_summary
    assert price_summary["Взрослый, 1 ч."][100]["count"] == 3
    assert price_summary["Взрослый, 1 ч."][100]["total_price"] == 300

def test_different_prices_same_category(setup_system_ticket_stats):
    tickets = [
        (0, 1, "-", None, None, 100),
        (0, 1, "-", None, None, 150),
        (0, 1, "-", None, None, 100),
    ]

    expected = [
        ("взрослый", {"sum": 3, "t_1": 3, "t_2": 0, "t_3": 0}),
        ("детский", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный взр.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("многодетный дет.", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("инвалид", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
        ("сопровождающий", {"sum": 0, "t_1": 0, "t_2": 0, "t_3": 0}),
    ]

    result = process_ticket_stats(tickets)
    assert result == expected

    # Проверка сводки по ценам
    assert hasattr(system, 'ticket_price_summary')
    price_summary = system.ticket_price_summary
    assert price_summary["Взрослый, 1 ч."][100]["count"] == 2
    assert price_summary["Взрослый, 1 ч."][100]["total_price"] == 200
    assert price_summary["Взрослый, 1 ч."][150]["count"] == 1
    assert price_summary["Взрослый, 1 ч."][150]["total_price"] == 150

#######################################
# Тестируем generate_ticket_report_table
@pytest.mark.parametrize("age, expected_ticket_type", [
    (4, "бесплатный"),  # Для возраста < 5
    (5, "детский"),     # Для возраста 5
    (14, "детский"),    # Для возраста 14
    (15, "взрослый"),   # Для возраста 15
    (99, "взрослый")    # Для возраста 99
])
def test_get_ticket_type(age, expected_ticket_type):
    assert get_ticket_type(age) == expected_ticket_type, f"Expected {expected_ticket_type} for age {age}"

# Тест для пограничных значений
def test_get_ticket_type_boundary_values():
    # Проверяем именно 5 и 15 лет
    assert get_ticket_type(5) == "детский", "Expected 'детский' for age 5"
    assert get_ticket_type(15) == "взрослый", "Expected 'взрослый' for age 15"

# Проверка на отрицательные возраст
def test_get_ticket_type_negative_age():
    with pytest.raises(ValueError):
        get_ticket_type(-1)  # Ожидается ошибка, так как возраст не может быть отрицательным
