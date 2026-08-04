import unittest
from unittest.mock import patch, MagicMock, mock_open
import subprocess
import sys

# Mock PySide6 and libfptr10 before importing payment_equipment
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['modules.libfptr10'] = MagicMock()

from modules.payment_equipment import (
    fptr_connection,
    run_terminal_command,
    check_terminal_file,
    process_success_result,
    handle_error,
    process_terminal_error,
    universal_terminal_operation,
    TERMINAL_SUCCESS_CODE,
    TERMINAL_USER_CANCEL_CODE
)

class TestPaymentEquipment(unittest.TestCase):

    def test_fptr_connection_success(self):
        mock_device = MagicMock()
        mock_device.isOpened.return_value = True

        with fptr_connection(mock_device) as d:
            self.assertEqual(d, mock_device)
            mock_device.open.assert_called_once()

        mock_device.close.assert_called_once()

    def test_fptr_connection_failed_to_open(self):
        mock_device = MagicMock()
        mock_device.isOpened.return_value = False

        with fptr_connection(mock_device) as d:
            self.assertIsNone(d)

        mock_device.close.assert_called_once()

    @patch('modules.payment_equipment.os.path.isfile')
    @patch('modules.payment_equipment.subprocess.Popen')
    def test_run_terminal_command_success(self, mock_popen, mock_isfile):
        mock_isfile.return_value = True

        mock_process = MagicMock()
        mock_process.communicate.return_value = (b"stdout", b"stderr")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        with patch('modules.payment_equipment.config.get', return_value="/opt/pinpad"):
            res = run_terminal_command("1 1000")

        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout, b"stdout")

    @patch('modules.payment_equipment.os.path.isfile')
    def test_run_terminal_command_not_found(self, mock_isfile):
        mock_isfile.return_value = False
        with patch('modules.payment_equipment.config.get', return_value="/opt/pinpad"):
            with self.assertRaises(FileNotFoundError):
                run_terminal_command("1 1000")

    @patch('modules.payment_equipment.open', new_callable=mock_open, read_data="ОДОБРЕНО")
    def test_check_terminal_file_found(self, m_open):
        with patch('modules.payment_equipment.config.get', return_value="/opt"):
            self.assertTrue(check_terminal_file("ОДОБРЕНО"))

    @patch('modules.payment_equipment.open', new_callable=mock_open, read_data="ОТКЛОНЕНО")
    def test_check_terminal_file_not_found(self, m_open):
        with patch('modules.payment_equipment.config.get', return_value="/opt"):
            self.assertFalse(check_terminal_file("ОДОБРЕНО"))

    @patch('modules.payment_equipment.check_terminal_file')
    def test_process_success_result(self, mock_check):
        mock_check.return_value = True
        self.assertEqual(process_success_result(), 1)

        mock_check.return_value = False
        self.assertEqual(process_success_result(), 0)

    def test_handle_error_with_callback(self):
        mock_cb = MagicMock()
        handle_error(123, "Title", "Message", error_callback=mock_cb)
        mock_cb.assert_called_once_with("Title", "Message", 123)

    @patch('modules.payment_equipment._safe_handle_error')
    def test_process_terminal_error(self, mock_safe_handle):
        process_terminal_error(TERMINAL_USER_CANCEL_CODE, MagicMock())
        mock_safe_handle.assert_called()
        args = mock_safe_handle.call_args[0]
        self.assertEqual(args[0], 2000)
        self.assertEqual(args[1], "Оплата отменена пользователем")

    @patch('modules.payment_equipment.process_terminal_transaction')
    def test_universal_terminal_operation(self, mock_ptt):
        mock_signal = MagicMock()

        mock_ptt.return_value = 1
        bank, payment = universal_terminal_operation(101, 150.0, mock_signal, operation_type=1)
        self.assertEqual(bank, 1)
        self.assertEqual(payment, 1)

        mock_ptt.return_value = 0
        bank, payment = universal_terminal_operation(101, 150.0, mock_signal, operation_type=1)
        self.assertEqual(bank, 0)
        self.assertEqual(payment, 1)

        bank, payment = universal_terminal_operation(100, 150.0, mock_signal, operation_type=1)
        self.assertEqual(bank, 1)
        self.assertEqual(payment, 3)

if __name__ == '__main__':
    unittest.main()
