import unittest
import sys
from unittest.mock import MagicMock, patch

sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
class MockQObject:
    def __init__(self, parent=None): pass
sys.modules['PySide6.QtCore'].QObject = MockQObject
sys.modules['PySide6.QtCore'].Signal = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['db.models'] = MagicMock()

import modules.worker as worker

class TestWorker(unittest.TestCase):

    def test_with_timer_decorator(self):
        class Dummy:
            @worker.with_timer
            def do_something(self, timer, arg1):
                return arg1 * 2

        d = Dummy()
        res = d.do_something(3)
        self.assertEqual(res, 6)

    def test_base_worker_log_step(self):
        mock_timer = MagicMock()
        mock_timer.elapsed.return_value = 100
        
        with patch('modules.worker.logger.debug') as mock_debug:
            worker.BaseWorker.log_step(mock_timer, "test_step")
            mock_debug.assert_called_with("[TIMER] test_step — 100 ms")

    def test_base_worker_delayed_progress_update(self):
        bw = worker.BaseWorker()
        bw.progress_updated = MagicMock()
        
        with patch('modules.worker.QTimer') as mock_timer_cls, \
             patch('modules.worker.QEventLoop') as mock_loop_cls:
            
            mock_timer = MagicMock()
            mock_timer_cls.return_value = mock_timer
            mock_loop = MagicMock()
            mock_loop_cls.return_value = mock_loop
            
            bw.delayed_progress_update("Test", 50, 10)
            
            bw.progress_updated.emit.assert_called_with("Test", 50)
            mock_timer.start.assert_called_with(10)
            mock_loop.exec.assert_called_once()

    def test_base_worker_emit_error_and_finish(self):
        bw = worker.BaseWorker()
        bw.error_signal = MagicMock()
        bw.close_window_signal = MagicMock()
        bw.finished = MagicMock()
        bw.delayed_progress_update = MagicMock()
        
        bw.emit_error_and_finish("Err", "Msg", "123", close_window=True)
        
        bw.error_signal.emit.assert_called_with("Err", "Msg", "123")
        bw.delayed_progress_update.assert_called_with("Ошибка: Err", 100, 1)
        bw.close_window_signal.emit.assert_called_once()
        bw.finished.emit.assert_called_once()

    def test_payment_handler_process_bank_payment_dev_mode(self):
        mock_worker = MagicMock()
        mock_pq = MagicMock()
        
        ph = worker.PaymentHandler(mock_worker, mock_pq, 101, 100.0, dev_mode=True)
        success, payment = ph.process_bank_payment()
        
        self.assertTrue(success)
        self.assertEqual(payment, 1)

    def test_payment_handler_process_bank_payment_normal(self):
        mock_worker = MagicMock()
        mock_pq = MagicMock()
        mock_pq.universal_terminal_operation.return_value = (1, 1)
        
        ph = worker.PaymentHandler(mock_worker, mock_pq, 101, 100.0, dev_mode=False)
        success, payment = ph.process_bank_payment()
        
        self.assertTrue(success)
        self.assertEqual(payment, 1)

    def test_payment_handler_process_bank_payment_failed(self):
        mock_worker = MagicMock()
        mock_pq = MagicMock()
        mock_pq.universal_terminal_operation.return_value = (0, None)
        
        ph = worker.PaymentHandler(mock_worker, mock_pq, 101, 100.0, dev_mode=False)
        success, payment = ph.process_bank_payment()
        
        self.assertFalse(success)
        self.assertIsNone(payment)

    def test_check_handler_print_check(self):
        mock_worker = MagicMock()
        mock_pq = MagicMock()
        mock_pq.check_open.return_value = 1
        
        ch = worker.CheckHandler(mock_worker, mock_pq)
        
        res = ch.print_check({"detail": [0,0,0,0,0,0,0,100]}, 1, MagicMock(), 1, 100, 1)
        self.assertTrue(res)
        
        mock_pq.check_open.return_value = 0
        res = ch.print_check({"detail": [0,0,0,0,0,0,0,100]}, 1, MagicMock(), 1, 100, 1)
        self.assertFalse(res)

    def test_database_handler_sale_exists(self):
        mock_session_cls = MagicMock()
        mock_engine = MagicMock()
        
        mock_session = MagicMock()
        mock_session_cls.return_value.__enter__.return_value = mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = True
        
        dh = worker.DatabaseHandler(mock_session_cls, mock_engine)
        self.assertTrue(dh.sale_exists(1))

    def test_transaction_worker_cleanup(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(1, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        
        self.assertFalse(tw._is_cleaned)
        tw.cleanup()
        self.assertTrue(tw._is_cleaned)
        self.assertEqual(mock_system.sale_status, 0)
        
        mock_system.sale_status = 1
        tw.cleanup()
        self.assertEqual(mock_system.sale_status, 1)

    def test_transaction_worker_process_special_sale(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(1, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.invoke_main_window_method = MagicMock()
        tw.delayed_progress_update = MagicMock()
        
        # Call it directly bypassing the decorator logic issues with MagicMock args
        tw.process_special_sale.__wrapped__(tw, MagicMock(), 90)
        tw.invoke_main_window_method.assert_called_with("print_saved_tickets")

    def test_transaction_worker_process_payment(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        
        tw.payment_handler = MagicMock()
        tw.payment_handler.process_bank_payment.return_value = (True, 1)
        tw.dev_mode = False # Prevent attribute error
        
        tw.pq = MagicMock()
        tw.pq.read_pinpad_file.return_value = "check_text"
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertEqual(payment, 1)
        self.assertEqual(bank_status, 1)
        tw.db_handler.update_sale.assert_called()

    def test_transaction_worker_process_checks(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        
        tw.check_handler = MagicMock()
        tw.check_handler.print_check.return_value = True
        
        tw.db_handler = MagicMock()
        
        res = tw.process_checks(MagicMock(), 1, 1)
        self.assertTrue(res)
        tw.db_handler.update_sale.assert_called()

    def test_transaction_worker_run(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_special = 0
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.process_payment = MagicMock(return_value=(1, 1))
        tw.process_checks = MagicMock(return_value=True)
        tw.finalize_transaction = MagicMock()
        
        tw.run()
        tw.process_payment.assert_called()
        tw.process_checks.assert_called()
        tw.finalize_transaction.assert_called()

if __name__ == '__main__':
    unittest.main()
