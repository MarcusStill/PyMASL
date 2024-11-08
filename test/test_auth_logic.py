import datetime as dt
from unittest.mock import MagicMock

import pytest

from auth_logic import perform_pre_sale_checks
from system import System

system = System()


@pytest.fixture
def setup_system():
    # Настройка фикстуры, сбрасывающей состояние System перед каждым тестом
    system.what_a_day = None
    system.num_of_week = None
    system.sunday = 0
    yield
    # Сброс состояния System после каждого теста
    system.what_a_day = None
    system.num_of_week = None
    system.sunday = 0


@pytest.mark.parametrize(
    "login, password, expected_result",
    [("valid_login", "valid_password", 1), ("invalid_login", "invalid_password", 0)],
)
def test_perform_pre_sale_checks_authorization(
    setup_system, login, password, expected_result
):
    """Тесты авторизации"""
    # Подмена метода авторизации
    system.user_authorization = MagicMock(return_value=expected_result)

    # Вызов функции без None
    result = perform_pre_sale_checks(login, password)

    assert result == expected_result
    # Проверка, что метод user_authorization был вызван с правильными аргументами
    system.user_authorization.assert_called_once_with(login, password)


def test_check_day_status_weekday(setup_system):
    """Проверка статуса для буднего дня"""
    # Подмена метода check_day, чтобы он возвращал 0 (будний день)
    system.check_day = MagicMock(return_value=0)
    system.user_authorization = MagicMock(return_value=1)

    # Вызов функции без None
    result = perform_pre_sale_checks("valid_login", "valid_password")

    assert result == 1
    assert system.what_a_day == 0


def test_check_day_status_weekend(setup_system):
    """Проверка статуса для выходного дня"""
    # Подмена метода check_day, чтобы он возвращал 1 (выходной день)
    system.check_day = MagicMock(return_value=1)
    system.user_authorization = MagicMock(return_value=1)

    # Вызов функции без None
    result = perform_pre_sale_checks("valid_login", "valid_password")

    assert result == 1
    assert system.what_a_day == 1


@pytest.mark.parametrize(
    "today_date, expected_sunday",
    [
        (dt.datetime(2024, 11, 3), 1),  # Воскресенье, первая неделя месяца
        (dt.datetime(2024, 11, 10), 0),  # Воскресенье, не первая неделя месяца
        (dt.datetime(2024, 11, 4), 0),  # Понедельник
    ],
)
def test_sunday_for_large_families(
    setup_system, monkeypatch, today_date, expected_sunday
):
    """Проверка установки флага для дня многодетных"""
    system.user_authorization = MagicMock(return_value=1)
    system.check_day = MagicMock(return_value=0)

    # Подмена текущей даты
    monkeypatch.setattr(
        dt, "datetime", MagicMock(today=MagicMock(return_value=today_date))
    )

    result = perform_pre_sale_checks("valid_login", "valid_password")

    assert result == 1
    assert system.sunday == expected_sunday


def test_week_and_month_day_assignment(setup_system, monkeypatch):
    """Проверка номера дня недели и дня месяца"""
    test_date = dt.datetime(2024, 11, 6)  # Среда, 6 ноября

    # Подмена текущей даты для datetime.datetime и datetime.date
    monkeypatch.setattr(
        dt, "datetime", MagicMock(today=MagicMock(return_value=test_date))
    )
    monkeypatch.setattr(
        dt, "date", MagicMock(today=MagicMock(return_value=test_date.date()))
    )

    system.user_authorization = MagicMock(return_value=1)
    system.check_day = MagicMock(return_value=0)

    result = perform_pre_sale_checks("valid_login", "valid_password")

    assert result == 1
    assert system.num_of_week == 3  # Среда (3-й день недели)
    assert dt.date.today().day == 6  # Номер дня месяца (6)
