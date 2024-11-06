import datetime as dt
from unittest.mock import MagicMock

import pytest

from auth_logic import perform_pre_sale_checks
from system import System


@pytest.fixture
def setup_system():
    # Настройка фикстуры, сбрасывающей состояние System перед каждым тестом
    System.what_a_day = None
    System.num_of_week = None
    System.sunday = 0
    yield
    # Сброс состояния System после каждого теста
    System.what_a_day = None
    System.num_of_week = None
    System.sunday = 0


@pytest.mark.parametrize(
    "login, password, expected_result",
    [("valid_login", "valid_password", 1), ("invalid_login", "invalid_password", 0)],
)
def test_perform_pre_sale_checks_authorization(
    setup_system, login, password, expected_result
):
    """Тесты авторизации"""
    # Подмена метода авторизации
    System.user_authorization = MagicMock(return_value=expected_result)
    result = perform_pre_sale_checks(None, login, password)
    assert result == expected_result
    if expected_result == 1:
        System.user_authorization.assert_called_once_with(None, login, password)
    else:
        System.user_authorization.assert_called_once_with(None, login, password)


def test_check_day_status_weekday(setup_system):
    """Проверка статуса для буднего дня"""
    System.check_day = MagicMock(return_value=0)
    System.user_authorization = MagicMock(return_value=1)
    result = perform_pre_sale_checks(None, "valid_login", "valid_password")
    assert result == 1
    assert System.what_a_day == 0


def test_check_day_status_weekend(setup_system):
    """Проверка статуса для выходного дня"""
    System.check_day = MagicMock(return_value=1)
    System.user_authorization = MagicMock(return_value=1)
    result = perform_pre_sale_checks(None, "valid_login", "valid_password")
    assert result == 1
    assert System.what_a_day == 1


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
    System.user_authorization = MagicMock(return_value=1)
    System.check_day = MagicMock(return_value=0)
    # Подмена текущей даты
    monkeypatch.setattr(
        dt, "datetime", MagicMock(today=MagicMock(return_value=today_date))
    )

    result = perform_pre_sale_checks(None, "valid_login", "valid_password")
    assert result == 1
    assert System.sunday == expected_sunday


def test_week_and_month_day_assignment(setup_system, monkeypatch):
    """Проверка номера дня недели и дня месяца"""
    test_date = dt.datetime(2024, 11, 6)  # Среда, 6 ноября
    monkeypatch.setattr(
        dt, "datetime", MagicMock(today=MagicMock(return_value=test_date))
    )

    System.user_authorization = MagicMock(return_value=1)
    System.check_day = MagicMock(return_value=0)
    result = perform_pre_sale_checks(None, "valid_login", "valid_password")

    assert result == 1
    assert System.num_of_week == 3  # Среда
    assert dt.date.today().day == 6  # Номер дня месяца
