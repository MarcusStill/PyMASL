from unittest.mock import MagicMock, patch
from unittest.mock import Mock

import pytest

from modules.payment_equipment import (
    TERMINAL_SUCCESS_CODE, TERMINAL_USER_CANCEL_CODE, TERMINAL_USER_TIMEOUT, TERMINAL_DATA_EXCHANGE,
    TERMINAL_NO_MONEY,
    TERMINAL_KLK,
    TERMINAL_CARD_BLOCKED,
    TERMINAL_CARD_LIMIT,
    TERMINAL_INVALID_CURRENCY_CODE,
    TERMINAL_NO_ADDRESS_TO_CONTACT,
    TERMINAL_ERROR_PIN_CODE,
    TERMINAL_LIMIT_OPERATION,
    TERMINAL_BIOMETRIC_ERROR,
    TERMINAL_NO_CONNECTION_BANK,
    TERMINAL_NEED_CASH_COLLECTION,
    TERMINAL_CARD_ERROR,
    TERMINAL_OPERATION_CANCELED,
    TERMINAL_SERVER_ROUTINE_MAINTENANCE,
    TERMINAL_PIN_PAD_ERROR,
    TERMINAL_COMMAND_ERROR,
    TERMINAL_QR_ERROR,
    TERMINAL_OPERATION_AMOUNT_ERROR,
)
from modules.payment_equipment import process_terminal_error
from modules.worker import PaymentHandler


@pytest.fixture
def payment_handler_fixture():
    worker_mock = MagicMock()
    pq_mock = MagicMock()
    payment_type = 101
    amount = 1000

    handler = PaymentHandler(worker_mock, pq_mock, payment_type, amount)
    return handler, worker_mock, pq_mock


@pytest.mark.parametrize(
    "bank_returned, exception_to_raise, expected_emit_error_calls",
    [
        (0, None, 1),  # Ошибка оплаты, банк = 0
        (None, Exception("Terminal failure"), 1),  # Исключение в операции терминала
    ]
)
def test_process_bank_payment_errors(payment_handler_fixture, bank_returned, exception_to_raise, expected_emit_error_calls):
    handler, worker_mock, pq_mock = payment_handler_fixture

    if exception_to_raise:
        pq_mock.universal_terminal_operation.side_effect = exception_to_raise
    else:
        pq_mock.universal_terminal_operation.return_value = (bank_returned, None)

    # Мокаем emit_error_and_finish для проверки вызова
    worker_mock.emit_error_and_finish = MagicMock()

    success, payment = handler.process_bank_payment()

    assert success is False
    assert payment is None
    assert worker_mock.emit_error_and_finish.call_count == expected_emit_error_calls


def test_process_bank_payment_success(payment_handler_fixture):
    handler, worker_mock, pq_mock = payment_handler_fixture

    pq_mock.universal_terminal_operation.return_value = (1, "payment_data")

    worker_mock.emit_error_and_finish = MagicMock()

    success, payment = handler.process_bank_payment()

    assert success is True
    assert payment == "payment_data"
    worker_mock.emit_error_and_finish.assert_not_called()


@pytest.mark.parametrize("code, expected_message_part", [
    (2000, "Оплата отменена пользователем"),
    (2002, "Слишком долгий ввод ПИН-кода"),
    (4336, "Указан неверный код валюты"),
])
def test_simple_errors(code, expected_message_part, monkeypatch):
    mock_windows = MagicMock()
    monkeypatch.setattr("modules.payment_equipment.windows", mock_windows)

    callback = Mock()

    # Вариант 1: Проверяем позиционные аргументы
    with patch('modules.payment_equipment.handle_error') as mock_handle:
        result = process_terminal_error(code, error_callback=callback)

        # Проверяем что handle_error вызван с правильным callback
        mock_handle.assert_called_once()
        args, kwargs = mock_handle.call_args
        assert len(args) >= 4, "Callback должен быть 4-м позиционным аргументом"
        assert args[3] is callback, "Callback потерялся при передаче!"

    # Вариант 2: Проверяем реальный вызов
    result = process_terminal_error(code, error_callback=callback)
    assert callback.called, "Callback не был вызван!"
    assert expected_message_part in callback.call_args[0][1]

def test_unknown_error_code():
    unknown_code = 99999
    callback = Mock()

    result = process_terminal_error(unknown_code, error_callback=callback)

    assert result == 0
    callback.assert_called_once_with(
        "Ошибка терминала",
        "Возвращен неизвестный код ошибки. Обратитесь в службу поддержки. Телефон тех.поддержки 0321. Код возврата: 99999.",
        99999
    )

@pytest.fixture
def mock_windows(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("modules.payment_equipment.windows", mock)
    return mock


#====
ALL_ERROR_CODES = {
    "success_code": TERMINAL_SUCCESS_CODE,
    "user_cancel": TERMINAL_USER_CANCEL_CODE,
    "timeout": TERMINAL_USER_TIMEOUT,
    "data_exchange": TERMINAL_DATA_EXCHANGE,
    "no_money": TERMINAL_NO_MONEY,
    "klk": TERMINAL_KLK,
    "card_blocked": TERMINAL_CARD_BLOCKED,
    "card_limit": TERMINAL_CARD_LIMIT,
    "invalid_currency": TERMINAL_INVALID_CURRENCY_CODE,
    "no_address": TERMINAL_NO_ADDRESS_TO_CONTACT,
    "pin_error": TERMINAL_ERROR_PIN_CODE,
    "limit_operation": TERMINAL_LIMIT_OPERATION,
    "biometric_error": TERMINAL_BIOMETRIC_ERROR,
    "no_connection": TERMINAL_NO_CONNECTION_BANK,
    "need_collection": TERMINAL_NEED_CASH_COLLECTION,
    "card_error": TERMINAL_CARD_ERROR,
    "operation_canceled": TERMINAL_OPERATION_CANCELED,
    "server_maintenance": TERMINAL_SERVER_ROUTINE_MAINTENANCE,
    "pin_pad_error": TERMINAL_PIN_PAD_ERROR,
    "command_error": TERMINAL_COMMAND_ERROR,
    "qr_error": TERMINAL_QR_ERROR,
    "amount_error": TERMINAL_OPERATION_AMOUNT_ERROR
}

# Разворачиваем словарь для параметризации
@pytest.mark.parametrize("group_name,error_codes", ALL_ERROR_CODES.items())
def test_process_terminal_error_grouped_codes(group_name, error_codes):
    callback = Mock()

    if isinstance(error_codes, int):
        error_codes = [error_codes]  # оборачиваем одиночный код в список

    for code in error_codes:
        result = process_terminal_error(code, error_callback=callback)
        assert result == 0, f"Ожидается 0 для кода {code}"
        assert callback.called, f"callback не вызван для {code}"
        called_args = callback.call_args[0]
        assert isinstance(called_args[0], str), "Ожидается строка в качестве заголовка"
        assert isinstance(called_args[1], str), "Ожидается строка в качестве сообщения"
        assert called_args[2] == code, f"Код возврата не совпадает: {called_args[2]} != {code}"
        callback.reset_mock()
