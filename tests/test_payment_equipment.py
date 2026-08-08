import types
import unittest
from unittest.mock import patch, MagicMock, mock_open

import sys
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()

fake_libfptr10 = types.ModuleType("modules.libfptr10")


class FakeIFptr:
    LIBFPTR_PARAM_TEXT_WRAP = 1
    LIBFPTR_TW_WORDS = 1
    LIBFPTR_PARAM_TEXT = 1
    LIBFPTR_PARAM_PRINT_FOOTER = 1
    LIBFPTR_PARAM_DATA_TYPE = 1
    LIBFPTR_DT_MODEL_INFO = 1
    LIBFPTR_PARAM_MODEL = 1
    LIBFPTR_PARAM_MODEL_NAME = 1
    LIBFPTR_PARAM_UNIT_VERSION = 1
    LIBFPTR_DT_STATUS = 1
    LIBFPTR_PARAM_FN_DATA_TYPE = 1
    LIBFPTR_FNDT_LAST_DOCUMENT = 1
    LIBFPTR_PARAM_DATE_TIME = 1
    LIBFPTR_FNDT_OFD_EXCHANGE_STATUS = 1
    LIBFPTR_PARAM_OFD_EXCHANGE_STATUS = 1
    LIBFPTR_PARAM_DOCUMENTS_COUNT = 1
    LIBFPTR_PARAM_DOCUMENT_NUMBER = 1
    LIBFPTR_PARAM_OFD_MESSAGE_READ = 1
    LIBFPTR_PARAM_LAST_SUCCESSFUL_OKP = 1
    LIBFPTR_DT_DATE_TIME = 1
    LIBFPTR_DT_SHIFT_STATE = 1
    LIBFPTR_PARAM_SHIFT_STATE = 1
    LIBFPTR_PARAM_SHIFT_NUMBER = 1
    LIBFPTR_PARAM_REPORT_TYPE = 1
    LIBFPTR_RT_LAST_DOCUMENT = 1
    LIBFPTR_RT_OFD_EXCHANGE_STATUS = 1
    LIBFPTR_RT_X = 1
    LIBFPTR_PARAM_SUM = 1
    LIBFPTR_DT_CASH_SUM = 1
    LIBFPTR_PARAM_COMMODITY_NAME = 1
    LIBFPTR_PARAM_PRICE = 1
    LIBFPTR_PARAM_QUANTITY = 1
    LIBFPTR_PARAM_TAX_TYPE = 1
    LIBFPTR_TAX_VAT22 = 1
    LIBFPTR_PARAM_RECEIPT_TYPE = 1
    LIBFPTR_RT_SELL = 1
    LIBFPTR_RT_SELL_RETURN = 1
    LIBFPTR_PARAM_RECEIPT_ELECTRONICALLY = 1
    LIBFPTR_PARAM_PAYMENT_TYPE = 1
    LIBFPTR_PT_CASH = 1
    LIBFPTR_PT_ELECTRONICALLY = 1
    LIBFPTR_PARAM_PAYMENT_SUM = 1
    LIBFPTR_PARAM_DOCUMENT_CLOSED = 1
    LIBFPTR_PARAM_DOCUMENT_PRINTED = 1
    LIBFPTR_DT_RECEIPT_STATE = 1
    LIBFPTR_PARAM_RECEIPT_NUMBER = 1
    LIBFPTR_RT_CLOSED = 0
    LIBFPTR_RT_CLOSE_SHIFT = 1

    def __init__(self, *args): pass


fake_libfptr10.IFptr = FakeIFptr
sys.modules['modules.libfptr10'] = fake_libfptr10

import modules.payment_equipment as pe  # noqa: E402

class TestPE(unittest.TestCase):
    def setUp(self):
        pe.dev_mode = False
        pe.kkt_available = True

    def test_smena_info(self):
        mock_fptr = MagicMock()
        mock_fptr.open.return_value = None
        mock_fptr.getParamInt.side_effect = [1, 100]

        with patch("modules.payment_equipment.fptr", mock_fptr):
            with patch("modules.payment_equipment.windows.info_window") as mock_info:
                res = pe.smena_info()
                self.assertEqual(res, 1)

    def test_last_document(self):
        mock_fptr = MagicMock()
        with patch("modules.payment_equipment.fptr", mock_fptr):
            pe.last_document()
            mock_fptr.report.assert_called_once()

    def test_report_payment(self):
        mock_fptr = MagicMock()
        with patch("modules.payment_equipment.fptr", mock_fptr):
            pe.report_payment()
            mock_fptr.report.assert_called_once()

    def test_report_x(self):
        mock_fptr = MagicMock()
        with patch("modules.payment_equipment.fptr", mock_fptr):
            pe.report_x()
            mock_fptr.report.assert_called_once()

    def test_deposit_of_money(self):
        mock_fptr = MagicMock()
        with patch("modules.payment_equipment.fptr", mock_fptr):
            with patch("modules.payment_equipment.windows.info_window") as mock_info:
                pe.deposit_of_money(100.0)
                mock_fptr.cashIncome.assert_called_once()

    def test_payment(self):
        mock_fptr = MagicMock()
        with patch("modules.payment_equipment.fptr", mock_fptr):
            with patch("modules.payment_equipment.windows.info_window") as mock_info:
                pe.payment(100.0)
                mock_fptr.cashOutcome.assert_called_once()

    def test_balance_check(self):
        mock_fptr = MagicMock()
        mock_fptr.getParamDouble.return_value = 500.0
        with patch("modules.payment_equipment.fptr", mock_fptr):
            with patch("modules.payment_equipment.windows.info_window") as mock_info:
                res = pe.balance_check()
                self.assertEqual(res, 500.0)
                self.assertEqual(mock_fptr.printText.call_count, 2)

    def test_run_terminal_command(self):
        with patch("subprocess.Popen") as mock_popen:
            with patch("os.path.isfile", return_value=True):
                mock_process = MagicMock()
                mock_process.communicate.return_value = (b"", b"")
                mock_popen.return_value = mock_process
                pe.run_terminal_command("1")
                mock_popen.assert_called_once()

    def test_check_terminal_file(self):
        with patch("builtins.open", mock_open(read_data="УСПЕШНО")):
            res = pe.check_terminal_file("УСПЕШНО")
            self.assertTrue(res)

    def test_process_success_result(self):
        with patch("modules.payment_equipment.windows.info_window"):
            res = pe.process_success_result()
            self.assertEqual(res, pe.TERMINAL_SUCCESS_CODE)

    def test_handle_error(self):
        with patch("modules.payment_equipment.windows.info_window"):
            res = pe.handle_error(1, "title", "msg", None)
            self.assertIsNone(res)

    def test_process_terminal_error(self):
        with patch("modules.payment_equipment.handle_error") as mock_handle:
            mock_handle.return_value = None
            with patch("modules.payment_equipment.windows.info_window"):
                res = pe.process_terminal_error(4451, None)
                mock_handle.assert_called_once()
            self.assertEqual(res, 0)

    def test_terminal_oplata(self):
        with patch("modules.payment_equipment.process_terminal_transaction") as mock_ptt:
            mock_ptt.return_value = 1
            res = pe.terminal_oplata(100.0)
            self.assertEqual(res, 1)

    def test_terminal_check_itog(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.check_terminal_file", return_value=True):
                res = pe.terminal_check_itog()
                self.assertEqual(res, 1)

    def test_terminal_menu(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            res = pe.terminal_menu()
            self.assertIsNone(res)

    def test_terminal_check_itog_window(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.check_terminal_file", return_value=True):
                with patch("modules.payment_equipment.windows.info_window") as mock_info:
                    pe.terminal_check_itog_window()
                    mock_info.assert_called_once()

    def test_terminal_svod_check(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.print_pinpad_check"):
                res = pe.terminal_svod_check()
                self.assertIsNone(res)

    def test_terminal_control_lenta(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.print_pinpad_check"):
                res = pe.terminal_control_lenta()
                self.assertIsNone(res)

    def test_terminal_print_file(self):
        with patch("modules.payment_equipment.read_pinpad_file", return_value="print_data"), \
                patch("modules.payment_equipment.fptr") as mock_fptr, \
                patch("modules.payment_equipment.windows.info_window"):
            pe.terminal_print_file()
            mock_fptr.printText.assert_called()

    def test_terminal_copy_last_check(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.print_pinpad_check"):
                res = pe.terminal_copy_last_check()
                self.assertIsNone(res)

    def test_is_kkt_connected(self):
        pe.kkt_available = True
        mock_fptr = MagicMock()
        mock_fptr.open.return_value = None
        with patch("modules.payment_equipment.fptr", mock_fptr):
            res = pe.is_kkt_connected()
            self.assertTrue(res)

    def test_process_terminal_transaction(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            with patch("os.path.isfile", return_value=True):
                mock_proc = MagicMock()
                mock_proc.returncode = pe.TERMINAL_SUCCESS_CODE
                mock_run.return_value = mock_proc
                with patch("modules.payment_equipment.check_terminal_file", return_value=True):
                    with patch("modules.payment_equipment.terminal_print_file"):
                        res = pe.process_terminal_transaction(
                            "1", 100.0, "Оплата")
                        self.assertEqual(res, 1)

    def test_universal_terminal_operation(self):
        with patch("modules.payment_equipment.process_terminal_transaction") as mock_ptt:
            mock_ptt.return_value = 1
            mock_signal = MagicMock()
            res = pe.universal_terminal_operation(
                pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=1)
            self.assertEqual(res, (1, 1))

    def test_print_slip_check(self):
        with patch("modules.payment_equipment.read_pinpad_file", return_value="slip_data"), \
                patch("modules.payment_equipment.fptr") as mock_fptr, \
                patch("modules.payment_equipment.windows.info_window"):
            pe.print_slip_check()
            mock_fptr.printText.assert_called()

    def test_print_pinpad_check(self):
        with patch("modules.payment_equipment.read_pinpad_file", return_value=["line1", "line2"]), \
                patch("modules.payment_equipment.fptr") as mock_fptr, \
                patch("modules.payment_equipment.windows.info_window"):
            pe.print_pinpad_check()
            mock_fptr.printText.assert_called()

    def test_universal_terminal_operation_refund(self):
        with patch("modules.payment_equipment.process_terminal_transaction") as mock_ptt:
            mock_ptt.return_value = 1
            mock_signal = MagicMock()
            res = pe.universal_terminal_operation(
                pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=2)
            self.assertEqual(res, (1, 1))

    def test_universal_terminal_operation_cancel(self):
        with patch("modules.payment_equipment.process_terminal_transaction") as mock_ptt:
            mock_ptt.return_value = 1
            mock_signal = MagicMock()
            res = pe.universal_terminal_operation(
                pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=3)
            self.assertEqual(res, (1, 1))


if __name__ == '__main__':
    unittest.main()

    def test_kkt_connection_dev_mode(self):
        with patch("modules.payment_equipment.dev_mode", True):
            with pe.fptr_connection(None) as conn:
                self.assertIsNone(conn)

    def test_kkt_connection_kkt_not_available(self):
        with patch("modules.payment_equipment.kkt_available", False):
            with pe.fptr_connection(pe.fptr) as conn:
                self.assertIsNone(conn)

    def test_kkt_connection_not_opened(self):
        mock_device = MagicMock()
        mock_device.isOpened.return_value = False
        with pe.fptr_connection(mock_device) as conn:
            self.assertIsNone(conn)
            mock_device.open.assert_called_once()

    def test_kkt_connection_exception_on_open(self):
        mock_device = MagicMock()
        mock_device.open.side_effect = Exception("Open failed")
        with pe.fptr_connection(mock_device) as conn:
            self.assertIsNone(conn)

    def test_kkt_connection_success(self):
        mock_device = MagicMock()
        mock_device.isOpened.return_value = True
        with pe.fptr_connection(mock_device) as conn:
            self.assertEqual(conn, mock_device)
        mock_device.close.assert_called_once()

    def test_run_terminal_command_timeout(self):
        with patch("subprocess.Popen") as mock_popen, \
                patch("os.path.isfile", return_value=True):
            mock_process = MagicMock()
            mock_process.communicate.side_effect = [
                subprocess.TimeoutExpired(cmd="", timeout=1), (b"", b"")]
            mock_popen.return_value = mock_process
            res = pe.run_terminal_command("1", timeout=1)
            mock_process.terminate.assert_called_once()

    def test_run_terminal_command_timeout_twice(self):
        with patch("subprocess.Popen") as mock_popen, \
                patch("os.path.isfile", return_value=True):
            mock_process = MagicMock()
            mock_process.communicate.side_effect = [
                subprocess.TimeoutExpired(cmd="", timeout=1),
                subprocess.TimeoutExpired(cmd="", timeout=1),
                (b"", b"")
            ]
            mock_popen.return_value = mock_process
            res = pe.run_terminal_command("1", timeout=1)
            mock_process.terminate.assert_called_once()
            mock_process.kill.assert_called_once()

    def test_run_terminal_command_file_not_found(self):
        with patch("os.path.isfile", return_value=False):
            with self.assertRaises(FileNotFoundError):
                pe.run_terminal_command("1")

    def test_run_terminal_command_exception(self):
        with patch("os.path.isfile", return_value=True), \
                patch("subprocess.Popen", side_effect=Exception("Exec failed")):
            res = pe.run_terminal_command("1")
            self.assertIsNone(res)

    def test_check_terminal_file_not_found_word(self):
        with patch("builtins.open", mock_open(read_data="НЕУСПЕШНО")):
            res = pe.check_terminal_file("УСПЕШНО")
            self.assertFalse(res)

    def test_check_terminal_file_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            res = pe.check_terminal_file("УСПЕШНО")
            self.assertFalse(res)

    def test_check_terminal_file_decode_error(self):
        with patch("builtins.open", side_effect=UnicodeDecodeError("codec", b"", 0, 1, "reason")):
            res = pe.check_terminal_file("УСПЕШНО")
            self.assertFalse(res)

    def test_process_success_result_not_found(self):
        with patch("modules.payment_equipment.check_terminal_file", return_value=False):
            res = pe.process_success_result()
            self.assertEqual(res, 0)

    def test_process_success_result_exception(self):
        with patch("modules.payment_equipment.check_terminal_file", side_effect=FileNotFoundError):
            res = pe.process_success_result()
            self.assertEqual(res, 0)

    def test_safe_handle_error(self):
        with patch("modules.payment_equipment.handle_error", side_effect=Exception("Error")):
            res = pe._safe_handle_error(1, "title", "msg", None)
            self.assertIsNone(res)

    def test_handle_error_with_callback_success(self):
        mock_callback = MagicMock()
        pe.handle_error(1, "title", "msg", mock_callback)
        mock_callback.assert_called_once_with("title", "msg", 1)

    def test_handle_error_with_callback_exception(self):
        mock_callback = MagicMock(side_effect=Exception("Callback error"))
        pe.handle_error(1, "title", "msg", mock_callback)
        mock_callback.assert_called_once_with("title", "msg", 1)

    def test_process_terminal_error_conditions(self):
        with patch("modules.payment_equipment.handle_error"):
            # Test each error category
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_CARD_BLOCKED[0], None), 0)
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_CARD_LIMIT[0], None), 0)
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_BIOMETRIC_ERROR[0], None), 0)
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_ERROR_PIN_CODE[0], None), 0)
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_NO_CONNECTION_BANK[0], None), 0)
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_HARDWARE_ERROR[0], None), 0)
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_OPERATION_CANCEL[0], None), 0)
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_LACK_PAPER[0], None), 0)
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_SUM_LIMIT[0], None), 0)

            # Test default mapped error
            self.assertEqual(pe.process_terminal_error(4451, None), 0)

            # Test unknown error
            self.assertEqual(pe.process_terminal_error(99999, None), 0)

    def test_process_terminal_error_more_conditions(self):
        with patch("modules.payment_equipment.handle_error"):
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_COMMAND_ERROR[0], None), 0)
            self.assertEqual(pe.process_terminal_error(
                pe.TERMINAL_PIN_PAD_ERROR[0], None), 0)

    def test_universal_terminal_operation_unsupported_operation_type(self):
        mock_signal = MagicMock()
        res = pe.universal_terminal_operation(
            pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=99)
        self.assertEqual(res, (0, 0))

    def test_universal_terminal_operation_offline(self):
        mock_signal = MagicMock()
        res = pe.universal_terminal_operation(
            pe.PAYMENT_OFFLINE, 100.0, mock_signal, operation_type=1)
        self.assertEqual(res, (1, 3))

    def test_universal_terminal_operation_offline_not_payment(self):
        mock_signal = MagicMock()
        res = pe.universal_terminal_operation(
            pe.PAYMENT_OFFLINE, 100.0, mock_signal, operation_type=2)
        self.assertEqual(res, (0, 0))

    def test_universal_terminal_operation_unknown_payment_type(self):
        mock_signal = MagicMock()
        res = pe.universal_terminal_operation(
            999, 100.0, mock_signal, operation_type=1)
        self.assertEqual(res, (0, 0))

    def test_universal_terminal_operation_transaction_fails(self):
        with patch("modules.payment_equipment.process_terminal_transaction") as mock_ptt:
            mock_ptt.return_value = 0
            mock_signal = MagicMock()
            res = pe.universal_terminal_operation(
                pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=1)
            self.assertEqual(res, (0, 1))

    def test_universal_terminal_operation_exceptions(self):
        mock_signal = MagicMock()
        with patch("modules.payment_equipment.process_terminal_transaction", side_effect=ValueError("Test")):
            res = pe.universal_terminal_operation(
                pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=1)
            self.assertEqual(res, (0, 0))
        with patch("modules.payment_equipment.process_terminal_transaction", side_effect=Exception("Test2")):
            res = pe.universal_terminal_operation(
                pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=1)
            self.assertEqual(res, (0, 0))

    def test_terminal_check_itog_run_error(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = None
            res = pe.terminal_check_itog()
            self.assertEqual(res, 0)

    def test_terminal_check_itog_unknown_code(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=999)
            res = pe.terminal_check_itog()
            self.assertEqual(res, 0)

    def test_terminal_check_itog_file_not_found(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.check_terminal_file", side_effect=FileNotFoundError):
                res = pe.terminal_check_itog()
                self.assertEqual(res, 0)

    def test_terminal_check_itog_window_run_error(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = None
            with patch("modules.payment_equipment.windows.info_window") as mock_info:
                pe.terminal_check_itog_window()
                mock_info.assert_called_once()

    def test_terminal_check_itog_window_file_not_found(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.read_pinpad_file", side_effect=FileNotFoundError):
                with patch("modules.payment_equipment.windows.info_window") as mock_info:
                    pe.terminal_check_itog_window()
                    mock_info.assert_called_once()

    def test_terminal_check_itog_window_unknown_code(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=999)
            with patch("modules.payment_equipment.windows.info_window") as mock_info:
                pe.terminal_check_itog_window()
                mock_info.assert_called_once()

    def test_terminal_svod_check_file_not_found(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.print_pinpad_check", side_effect=FileNotFoundError(1, "msg", "filename")):
                pe.terminal_svod_check()

    def test_terminal_control_lenta_file_not_found(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.print_pinpad_check", side_effect=FileNotFoundError(1, "msg", "filename")):
                pe.terminal_control_lenta()

    def test_terminal_copy_last_check_file_not_found(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.print_pinpad_check", side_effect=FileNotFoundError(1, "msg", "filename")):
                pe.terminal_copy_last_check()
