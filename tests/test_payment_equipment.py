import unittest
from unittest.mock import patch, MagicMock, mock_open

import sys

sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()

import types

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

import modules.payment_equipment as pe


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
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.check_terminal_file", return_value=True):
                res = pe.terminal_check_itog()
                self.assertEqual(res, 1)

    def test_terminal_menu(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
            res = pe.terminal_menu()
            self.assertIsNone(res)

    def test_terminal_check_itog_window(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.check_terminal_file", return_value=True):
                with patch("modules.payment_equipment.windows.info_window") as mock_info:
                    pe.terminal_check_itog_window()
                    mock_info.assert_called_once()

    def test_terminal_svod_check(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.print_pinpad_check"):
                res = pe.terminal_svod_check()
                self.assertIsNone(res)

    def test_terminal_control_lenta(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
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
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
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
                        res = pe.process_terminal_transaction("1", 100.0, "Оплата")
                        self.assertEqual(res, 1)

    def test_universal_terminal_operation(self):
        with patch("modules.payment_equipment.process_terminal_transaction") as mock_ptt:
            mock_ptt.return_value = 1
            mock_signal = MagicMock()
            res = pe.universal_terminal_operation(pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=1)
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
            res = pe.universal_terminal_operation(pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=2)
            self.assertEqual(res, (1, 1))

    def test_universal_terminal_operation_cancel(self):
        with patch("modules.payment_equipment.process_terminal_transaction") as mock_ptt:
            mock_ptt.return_value = 1
            mock_signal = MagicMock()
            res = pe.universal_terminal_operation(pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=3)
            self.assertEqual(res, (1, 1))


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
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.check_terminal_file", return_value=True):
                res = pe.terminal_check_itog()
                self.assertEqual(res, 1)
            
    def test_terminal_menu(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
            res = pe.terminal_menu()
            self.assertIsNone(res)
            
    def test_terminal_check_itog_window(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.check_terminal_file", return_value=True):
                with patch("modules.payment_equipment.windows.info_window") as mock_info:
                    pe.terminal_check_itog_window()
                    mock_info.assert_called_once()
            
    def test_terminal_svod_check(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
            with patch("modules.payment_equipment.print_pinpad_check"):
                res = pe.terminal_svod_check()
                self.assertIsNone(res)
            
    def test_terminal_control_lenta(self):
        with patch("modules.payment_equipment.run_terminal_command") as mock_run:
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
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
            mock_run.return_value = MagicMock(returncode=pe.TERMINAL_SUCCESS_CODE)
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
                        res = pe.process_terminal_transaction("1", 100.0, "Оплата")
                        self.assertEqual(res, 1)

    def test_universal_terminal_operation(self):
        with patch("modules.payment_equipment.process_terminal_transaction") as mock_ptt:
            mock_ptt.return_value = 1
            mock_signal = MagicMock()
            res = pe.universal_terminal_operation(pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=1)
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
            res = pe.universal_terminal_operation(pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=2)
            self.assertEqual(res, (1, 1))

    def test_universal_terminal_operation_cancel(self):
        with patch("modules.payment_equipment.process_terminal_transaction") as mock_ptt:
            mock_ptt.return_value = 1
            mock_signal = MagicMock()
            res = pe.universal_terminal_operation(pe.PAYMENT_ELECTRONIC, 100.0, mock_signal, operation_type=3)
            self.assertEqual(res, (1, 1))

if __name__ == '__main__':
    unittest.main()
