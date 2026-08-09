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


    def test_transaction_worker_init_amount_error(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {}
        tw = worker.TransactionWorker(1, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        self.assertEqual(tw.payment_handler.amount, 0)

    def test_transaction_worker_process_payment_sale_id_none(self):
        mock_system = MagicMock()
        mock_system.sale_id = None
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.emit_error_and_finish = MagicMock()
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertIsNone(payment)
        self.assertIsNone(bank_status)
        tw.emit_error_and_finish.assert_called()

    def test_transaction_worker_process_payment_sale_not_in_db(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = False
        tw.emit_error_and_finish = MagicMock()
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertIsNone(payment)
        self.assertIsNone(bank_status)
        tw.emit_error_and_finish.assert_called()


    def test_transaction_worker_process_payment_dev_mode(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        # Override getattr inside the module or just mock main_window properly
        class MockMainWindow:
            dev_mode = True
            
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MockMainWindow())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.delayed_progress_update = MagicMock()
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertEqual(payment, 1)
        self.assertEqual(bank_status, 0)

    def test_transaction_worker_process_payment_fail(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.payment_handler = MagicMock()
        tw.payment_handler.process_bank_payment.return_value = (False, None)
        tw.dev_mode = False
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertIsNone(payment)
        self.assertIsNone(bank_status)

    def test_transaction_worker_process_payment_bank_status_3(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.payment_handler = MagicMock()
        tw.payment_handler.process_bank_payment.return_value = (True, 3)
        tw.dev_mode = False
        tw.delayed_progress_update = MagicMock()
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertEqual(payment, 3)
        self.assertEqual(bank_status, 1)
        tw.db_handler.update_sale.assert_not_called()

    def test_transaction_worker_process_checks_check_open_fails(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.check_handler = MagicMock()
        tw.check_handler.print_check.return_value = False
        
        res = tw.process_checks(MagicMock(), 1, 1)
        self.assertFalse(res)

    def test_transaction_worker_process_checks_exception(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.check_handler = MagicMock()
        tw.check_handler.print_check.side_effect = Exception("Test Error")
        
        res = tw.process_checks(MagicMock(), 1, 1)
        self.assertFalse(res)

    def test_transaction_worker_finalize_transaction(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.invoke_main_window_method = MagicMock()
        tw.close_window_signal = MagicMock()
        tw.finished = MagicMock()
        
        tw.finalize_transaction(MagicMock())
        tw.invoke_main_window_method.assert_called_with("print_saved_tickets")
        tw.close_window_signal.emit.assert_called_once()
        tw.finished.emit.assert_called_once()
        self.assertEqual(mock_system.sale_status, 0)


    def test_transaction_worker_run_special_sale(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_special = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.process_special_sale = MagicMock()
        tw.finalize_transaction = MagicMock()
        
        tw.run()
        tw.process_special_sale.assert_called_with(90)
        tw.finalize_transaction.assert_called_once()

    def test_transaction_worker_run_process_payment_fails(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_special = 0
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.process_payment = MagicMock(return_value=(None, None))
        tw.process_checks = MagicMock()
        tw.finalize_transaction = MagicMock()
        
        tw.run()
        tw.process_payment.assert_called_once()
        tw.process_checks.assert_not_called()
        tw.finalize_transaction.assert_not_called()

    def test_transaction_worker_run_process_checks_fails(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_special = 0
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.process_payment = MagicMock(return_value=(1, 1))
        tw.process_checks = MagicMock(return_value=False)
        tw.finalize_transaction = MagicMock()
        
        tw.run()
        tw.process_payment.assert_called_once()
        tw.process_checks.assert_called_once()
        tw.finalize_transaction.assert_not_called()

    def test_transaction_worker_run_exception(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_special = 0
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.process_payment = MagicMock(side_effect=Exception("Test Run Error"))
        tw.handle_error = MagicMock()
        
        tw.run()
        tw.handle_error.assert_called_once()
        self.assertTrue(tw._is_cleaned)

    def test_transaction_worker_run_new_sale_save(self):
        mock_system = MagicMock()
        mock_system.sale_id = None
        mock_system.sale_special = 0
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.save_sale_signal = MagicMock()
        tw.log_step = MagicMock()
        tw.process_payment = MagicMock(return_value=(1, 1))
        tw.process_checks = MagicMock(return_value=True)
        tw.finalize_transaction = MagicMock()
        
        tw.run()
        tw.save_sale_signal.emit.assert_called_once()

    def test_transaction_worker_handle_error(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.emit_error_and_finish = MagicMock()
        
        tw.handle_error(Exception("Test exception"), MagicMock())
        tw.emit_error_and_finish.assert_called_once()
        self.assertEqual(mock_system.sale_status, 0)


    def test_payment_handler_exception(self):
        mock_worker = MagicMock()
        mock_pq = MagicMock()
        mock_pq.universal_terminal_operation.side_effect = Exception("Terminal Err")
        
        ph = worker.PaymentHandler(mock_worker, mock_pq, 101, 100.0, dev_mode=False)
        success, payment = ph.process_bank_payment()
        
        self.assertFalse(success)
        self.assertIsNone(payment)
        mock_worker.emit_error_and_finish.assert_called()

    def test_payment_handler_handle_terminal_error_callback(self):
        mock_worker = MagicMock()
        ph = worker.PaymentHandler(mock_worker, MagicMock(), 101, 100.0, dev_mode=False)
        
        ph._handle_terminal_error_callback("title", "msg", 123)
        mock_worker.emit_error_and_finish.assert_called_with(
            title="title",
            message="msg",
            code="123",
            step_name="terminal_error"
        )
        
    def test_payment_handler_handle_payment_failed(self):
        mock_worker = MagicMock()
        ph = worker.PaymentHandler(mock_worker, MagicMock(), 101, 100.0, dev_mode=False)
        
        ph._handle_payment_failed(MagicMock())
        mock_worker.emit_error_and_finish.assert_called()
        
    def test_payment_handler_get_mock_slip(self):
        ph = worker.PaymentHandler(MagicMock(), MagicMock(), 101, 100.0, dev_mode=False)
        slip = ph.get_mock_slip()
        self.assertIn("DEBUG_SLIP", slip)
        self.assertIn("100.0", slip)

    def test_check_handler_error(self):
        mock_worker = MagicMock()
        ch = worker.CheckHandler(mock_worker, MagicMock())
        
        ch.handle_check_error("Title", "Error text")
        mock_worker.emit_error_and_finish.assert_called()

    def test_database_handler_sale_exists_exception(self):
        mock_session_cls = MagicMock()
        mock_session_cls.return_value.__enter__.side_effect = Exception("DB error")
        
        dh = worker.DatabaseHandler(mock_session_cls, MagicMock())
        self.assertFalse(dh.sale_exists(1))

    def test_database_handler_update_sale(self):
        mock_session_cls = MagicMock()
        mock_session = MagicMock()
        mock_session_cls.return_value.__enter__.return_value = mock_session
        
        dh = worker.DatabaseHandler(mock_session_cls, MagicMock())
        dh.update_sale(1, status=1)
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()


    def test_base_worker_emit_error_and_finish_runtime_error(self):
        bw = worker.BaseWorker()
        bw.error_signal = MagicMock()
        bw.error_signal.emit.side_effect = RuntimeError("already deleted")
        
        # This shouldn't raise exception
        bw.emit_error_and_finish("Err", "Msg")
        
        bw.error_signal.emit.side_effect = RuntimeError("other error")
        with self.assertRaises(RuntimeError):
            bw.emit_error_and_finish("Err", "Msg")

    def test_base_worker_emit_error_and_finish_generic_exception(self):
        bw = worker.BaseWorker()
        bw.error_signal = MagicMock()
        bw.error_signal.emit.side_effect = Exception("generic error")
        
        # Should just log it, not raise
        bw.emit_error_and_finish("Err", "Msg")

    def test_base_worker_delayed_progress_update_negative_delay(self):
        bw = worker.BaseWorker()
        bw.progress_updated = MagicMock()
        
        with patch('modules.worker.QTimer') as mock_timer_cls,              patch('modules.worker.QEventLoop') as mock_loop_cls:
            mock_timer = MagicMock()
            mock_timer_cls.return_value = mock_timer
            mock_loop = MagicMock()
            mock_loop_cls.return_value = mock_loop
            
            bw.delayed_progress_update("Test", 50, -10)
            # -10 will become 0, meaning it won't trigger the QTimer logic
            mock_timer.start.assert_not_called()


    def test_base_worker_invoke_main_window_method(self):
        bw = worker.BaseWorker()
        bw.main_window = MagicMock()
        
        with patch('modules.worker.QMetaObject.invokeMethod') as mock_invoke:
            bw.invoke_main_window_method("test_method")
            mock_invoke.assert_called_once()
            
    def test_transaction_worker_process_payment_slip_check_print(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.payment_handler = MagicMock()
        tw.payment_handler.process_bank_payment.return_value = (True, 1)
        tw.dev_mode = False
        tw.delayed_progress_update = MagicMock()
        tw.pq = MagicMock()
        tw.print_check = 1
        
        tw.process_payment(MagicMock())
        tw.pq.print_slip_check.assert_called_once()
        
    def test_transaction_worker_process_payment_db_error(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.db_handler.update_sale.side_effect = Exception("DB save err")
        
        tw.payment_handler = MagicMock()
        tw.payment_handler.process_bank_payment.return_value = (True, 1)
        tw.dev_mode = False
        tw.delayed_progress_update = MagicMock()
        tw.pq = MagicMock()
        
        tw.process_payment(MagicMock())
        tw.pq.read_pinpad_file.assert_called_once()

    def test_transaction_worker_process_checks_print_check_0(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.user = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 0, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.check_handler = MagicMock()
        tw.check_handler.print_check.return_value = True
        tw.db_handler = MagicMock()
        tw.info_signal = MagicMock()
        
        tw.process_checks(MagicMock(), 1, 1)
        tw.info_signal.emit.assert_called_once()


    def test_base_worker_emit_error_and_finish_with_timer(self):
        bw = worker.BaseWorker()
        bw.error_signal = MagicMock()
        bw.close_window_signal = MagicMock()
        bw.finished = MagicMock()
        bw.delayed_progress_update = MagicMock()
        bw.log_step = MagicMock()
        
        mock_timer = MagicMock()
        bw.emit_error_and_finish("Err", "Msg", timer=mock_timer, step_name="test_step")
        
        bw.log_step.assert_called_once_with(mock_timer, "test_step")


    def test_transaction_worker_process_payment_dev_mode(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        # Override getattr inside the module or just mock main_window properly
        class MockMainWindow:
            dev_mode = True
            
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MockMainWindow())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.delayed_progress_update = MagicMock()
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertEqual(payment, 1)
        self.assertEqual(bank_status, 0)

    def test_transaction_worker_process_payment_fail(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.payment_handler = MagicMock()
        tw.payment_handler.process_bank_payment.return_value = (False, None)
        tw.dev_mode = False
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertIsNone(payment)
        self.assertIsNone(bank_status)

    def test_transaction_worker_process_payment_bank_status_3(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.payment_handler = MagicMock()
        tw.payment_handler.process_bank_payment.return_value = (True, 3)
        tw.dev_mode = False
        tw.delayed_progress_update = MagicMock()
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertEqual(payment, 3)
        self.assertEqual(bank_status, 1)
        tw.db_handler.update_sale.assert_not_called()

    def test_transaction_worker_process_checks_check_open_fails(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.check_handler = MagicMock()
        tw.check_handler.print_check.return_value = False
        
        res = tw.process_checks(MagicMock(), 1, 1)
        self.assertFalse(res)

    def test_transaction_worker_process_checks_exception(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.check_handler = MagicMock()
        tw.check_handler.print_check.side_effect = Exception("Test Error")
        
        res = tw.process_checks(MagicMock(), 1, 1)
        self.assertFalse(res)

    def test_transaction_worker_finalize_transaction(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.invoke_main_window_method = MagicMock()
        tw.close_window_signal = MagicMock()
        tw.finished = MagicMock()
        
        tw.finalize_transaction(MagicMock())
        tw.invoke_main_window_method.assert_called_with("print_saved_tickets")
        tw.close_window_signal.emit.assert_called_once()
        tw.finished.emit.assert_called_once()
        self.assertEqual(mock_system.sale_status, 0)


    def test_transaction_worker_run_special_sale(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_special = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.process_special_sale = MagicMock()
        tw.finalize_transaction = MagicMock()
        
        tw.run()
        tw.process_special_sale.assert_called_with(90)
        tw.finalize_transaction.assert_called_once()

    def test_transaction_worker_run_process_payment_fails(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_special = 0
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.process_payment = MagicMock(return_value=(None, None))
        tw.process_checks = MagicMock()
        tw.finalize_transaction = MagicMock()
        
        tw.run()
        tw.process_payment.assert_called_once()
        tw.process_checks.assert_not_called()
        tw.finalize_transaction.assert_not_called()

    def test_transaction_worker_run_process_checks_fails(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_special = 0
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.process_payment = MagicMock(return_value=(1, 1))
        tw.process_checks = MagicMock(return_value=False)
        tw.finalize_transaction = MagicMock()
        
        tw.run()
        tw.process_payment.assert_called_once()
        tw.process_checks.assert_called_once()
        tw.finalize_transaction.assert_not_called()

    def test_transaction_worker_run_exception(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_special = 0
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.process_payment = MagicMock(side_effect=Exception("Test Run Error"))
        tw.handle_error = MagicMock()
        
        tw.run()
        tw.handle_error.assert_called_once()
        self.assertTrue(tw._is_cleaned)

    def test_transaction_worker_run_new_sale_save(self):
        mock_system = MagicMock()
        mock_system.sale_id = None
        mock_system.sale_special = 0
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.save_sale_signal = MagicMock()
        tw.log_step = MagicMock()
        tw.process_payment = MagicMock(return_value=(1, 1))
        tw.process_checks = MagicMock(return_value=True)
        tw.finalize_transaction = MagicMock()
        
        tw.run()
        tw.save_sale_signal.emit.assert_called_once()

    def test_transaction_worker_handle_error(self):
        mock_system = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.emit_error_and_finish = MagicMock()
        
        tw.handle_error(Exception("Test exception"), MagicMock())
        tw.emit_error_and_finish.assert_called_once()
        self.assertEqual(mock_system.sale_status, 0)


    def test_payment_handler_exception(self):
        mock_worker = MagicMock()
        mock_pq = MagicMock()
        mock_pq.universal_terminal_operation.side_effect = Exception("Terminal Err")
        
        ph = worker.PaymentHandler(mock_worker, mock_pq, 101, 100.0, dev_mode=False)
        success, payment = ph.process_bank_payment()
        
        self.assertFalse(success)
        self.assertIsNone(payment)
        mock_worker.emit_error_and_finish.assert_called()

    def test_payment_handler_handle_terminal_error_callback(self):
        mock_worker = MagicMock()
        ph = worker.PaymentHandler(mock_worker, MagicMock(), 101, 100.0, dev_mode=False)
        
        ph._handle_terminal_error_callback("title", "msg", 123)
        mock_worker.emit_error_and_finish.assert_called_with(
            title="title",
            message="msg",
            code="123",
            step_name="terminal_error"
        )
        
    def test_payment_handler_handle_payment_failed(self):
        mock_worker = MagicMock()
        ph = worker.PaymentHandler(mock_worker, MagicMock(), 101, 100.0, dev_mode=False)
        
        ph._handle_payment_failed(MagicMock())
        mock_worker.emit_error_and_finish.assert_called()
        
    def test_payment_handler_get_mock_slip(self):
        ph = worker.PaymentHandler(MagicMock(), MagicMock(), 101, 100.0, dev_mode=False)
        slip = ph.get_mock_slip()
        self.assertIn("DEBUG_SLIP", slip)
        self.assertIn("100.0", slip)

    def test_check_handler_error(self):
        mock_worker = MagicMock()
        ch = worker.CheckHandler(mock_worker, MagicMock())
        
        ch.handle_check_error("Title", "Error text")
        mock_worker.emit_error_and_finish.assert_called()

    def test_database_handler_sale_exists_exception(self):
        mock_session_cls = MagicMock()
        mock_session_cls.return_value.__enter__.side_effect = Exception("DB error")
        
        dh = worker.DatabaseHandler(mock_session_cls, MagicMock())
        self.assertFalse(dh.sale_exists(1))

    def test_database_handler_update_sale(self):
        mock_session_cls = MagicMock()
        mock_session = MagicMock()
        mock_session_cls.return_value.__enter__.return_value = mock_session
        
        dh = worker.DatabaseHandler(mock_session_cls, MagicMock())
        dh.update_sale(1, status=1)
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()


    def test_base_worker_emit_error_and_finish_runtime_error(self):
        bw = worker.BaseWorker()
        bw.error_signal = MagicMock()
        bw.error_signal.emit.side_effect = RuntimeError("already deleted")
        
        # This shouldn't raise exception
        bw.emit_error_and_finish("Err", "Msg")
        
        bw.error_signal.emit.side_effect = RuntimeError("other error")
        with self.assertRaises(RuntimeError):
            bw.emit_error_and_finish("Err", "Msg")

    def test_base_worker_emit_error_and_finish_generic_exception(self):
        bw = worker.BaseWorker()
        bw.error_signal = MagicMock()
        bw.error_signal.emit.side_effect = Exception("generic error")
        
        # Should just log it, not raise
        bw.emit_error_and_finish("Err", "Msg")

    def test_base_worker_delayed_progress_update_negative_delay(self):
        bw = worker.BaseWorker()
        bw.progress_updated = MagicMock()
        
        with patch('modules.worker.QTimer') as mock_timer_cls,              patch('modules.worker.QEventLoop') as mock_loop_cls:
            mock_timer = MagicMock()
            mock_timer_cls.return_value = mock_timer
            mock_loop = MagicMock()
            mock_loop_cls.return_value = mock_loop
            
            bw.delayed_progress_update("Test", 50, -10)
            # -10 will become 0, meaning it won't trigger the QTimer logic
            mock_timer.start.assert_not_called()


    def test_base_worker_invoke_main_window_method(self):
        bw = worker.BaseWorker()
        bw.main_window = MagicMock()
        
        with patch('modules.worker.QMetaObject.invokeMethod') as mock_invoke:
            bw.invoke_main_window_method("test_method")
            mock_invoke.assert_called_once()
            
    def test_transaction_worker_process_payment_slip_check_print(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.payment_handler = MagicMock()
        tw.payment_handler.process_bank_payment.return_value = (True, 1)
        tw.dev_mode = False
        tw.delayed_progress_update = MagicMock()
        tw.pq = MagicMock()
        tw.print_check = 1
        
        tw.process_payment(MagicMock())
        tw.pq.print_slip_check.assert_called_once()
        
    def test_transaction_worker_process_payment_db_error(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = True
        tw.db_handler.update_sale.side_effect = Exception("DB save err")
        
        tw.payment_handler = MagicMock()
        tw.payment_handler.process_bank_payment.return_value = (True, 1)
        tw.dev_mode = False
        tw.delayed_progress_update = MagicMock()
        tw.pq = MagicMock()
        
        tw.process_payment(MagicMock())
        tw.pq.read_pinpad_file.assert_called_once()

    def test_transaction_worker_process_checks_print_check_0(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.user = MagicMock()
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 0, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.delayed_progress_update = MagicMock()
        tw.check_handler = MagicMock()
        tw.check_handler.print_check.return_value = True
        tw.db_handler = MagicMock()
        tw.info_signal = MagicMock()
        
        tw.process_checks(MagicMock(), 1, 1)
        tw.info_signal.emit.assert_called_once()


    def test_base_worker_emit_error_and_finish_with_timer(self):
        bw = worker.BaseWorker()
        bw.error_signal = MagicMock()
        bw.close_window_signal = MagicMock()
        bw.finished = MagicMock()
        bw.delayed_progress_update = MagicMock()
        bw.log_step = MagicMock()
        
        mock_timer = MagicMock()
        bw.emit_error_and_finish("Err", "Msg", timer=mock_timer, step_name="test_step")
        
        bw.log_step.assert_called_once_with(mock_timer, "test_step")

    def test_transaction_worker_process_payment_sale_id_none(self):
        mock_system = MagicMock()
        mock_system.sale_id = None
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.emit_error_and_finish = MagicMock()
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertIsNone(payment)
        self.assertIsNone(bank_status)
        tw.emit_error_and_finish.assert_called()

    def test_transaction_worker_process_payment_sale_not_in_db(self):
        mock_system = MagicMock()
        mock_system.sale_id = 1
        mock_system.sale_dict = {"detail": [0,0,0,0,0,0,0,100]}
        tw = worker.TransactionWorker(101, 1, mock_system, MagicMock(), MagicMock(), MagicMock())
        tw.db_handler = MagicMock()
        tw.db_handler.sale_exists.return_value = False
        tw.emit_error_and_finish = MagicMock()
        
        payment, bank_status = tw.process_payment(MagicMock())
        self.assertIsNone(payment)
        self.assertIsNone(bank_status)
        tw.emit_error_and_finish.assert_called()

if __name__ == '__main__':
    unittest.main()

    