import datetime as dt
import time

from PySide6.QtCore import QElapsedTimer
from PySide6.QtCore import QObject, Signal, QMetaObject, Qt
from sqlalchemy import update

from db.models import Sale
from modules.logger import logger


class TransactionWorker(QObject):
    progress_updated = Signal(str, int)
    finished = Signal()
    save_sale_signal = Signal()
    error_signal = Signal(str, str, str)
    info_signal = Signal(str)
    print_ticket_signal = Signal()
    close_window_signal = Signal()

    def __init__(self, payment_type, print_check, system, pq, Session, main_window, parent=None):
        super().__init__(parent)
        self.payment_type = payment_type
        self.print_check = print_check
        self.system = system
        self.pq = pq
        self.Session = Session
        self.main_window = main_window

    def log_step(self, timer, step_name):
        elapsed = timer.elapsed()
        logger.debug(f"[TIMER] {step_name} — {elapsed} ms")

    def run(self):
        timer = QElapsedTimer()
        timer.start()
        try:
            self.progress_updated.emit("Анализ продажи...", 5)

            # Сохраняем новую продажу
            if self.system.sale_id is None:
                self.progress_updated.emit("Сохраняем продажу...", 10)
                time.sleep(0.25) # for view
                self.save_sale_signal.emit()
                self.log_step(timer, "save_sale finished")
            # Особая продажа — только билеты
            if self.system.sale_special == 1:
                self.progress_updated.emit("Печатаем билеты (особая продажа)...", 100)
                time.sleep(0.25) # for view
                QMetaObject.invokeMethod(
                    self.main_window,
                    "print_saved_tickets",
                    Qt.QueuedConnection,
                )
                self.log_step(timer, "print_saved_tickets finished")
                self.close_window_signal.emit()
                return

            # Если оплата банковской картой
            # bank, payment = None, None
            if self.payment_type in (101, 100):
                self.progress_updated.emit("Ожидаем оплату на терминале...", 25)
                time.sleep(0.25) # for view
                try:
                    amount = self.system.sale_dict["detail"][7]
                    bank, payment = self.pq.universal_terminal_operation(self.payment_type, amount, self.progress_updated)
                    self.log_step(timer, "pq.universal_terminal_operation finished")
                except Exception as e:
                    self.error_signal.emit(
                        "Ошибка",
                        "Не удалось выполнить операцию на терминале.",
                        str(e),
                    )
                    self.progress_updated.emit("Ошибка оплаты", 100)
                    self.log_step(timer, "error_signal finished")
                    time.sleep(0.25) # for view
                    self.close_window_signal.emit()  # Закрытие окна прогресса в случае ошибки
                    self.finished.emit()  # Завершаем поток
                    return
                if bank == 0:
                    self.error_signal.emit(
                        "Ошибка",
                        "Операция оплаты не удалась. Повторите попытку.",
                        "",
                    )
                    self.progress_updated.emit("Ошибка оплаты", 100)
                    self.log_step(timer, "payment error finished")
                    time.sleep(0.25) # for view
                    self.close_window_signal.emit()  # Закрытие окна прогресса в случае ошибки
                    self.finished.emit()  # Завершаем поток
                    return
                if bank == 1:
                    self.progress_updated.emit("Сохраняем банковский чек...", 35)
                    time.sleep(0.25) # for view
                    if payment == 3:
                        check = "offline"
                    else:
                        check = self.pq.read_pinpad_file(remove_newline=False)
                        self.log_step(timer, "pq.read_pinpad_file finished")
                    with self.Session(self.system.engine) as session:
                        session.execute(
                            update(Sale)
                            .where(Sale.id == self.system.sale_id)
                            .values(bank_pay=check)
                        )
                        session.commit()
                    self.log_step(timer, "save in db finished")
                    if self.print_check == 1 and payment == 1:
                        self.progress_updated.emit("Печатаем слип-чек...", 40)
                        time.sleep(0.25) # for view
                        self.pq.print_slip_check()
                        self.log_step(timer, "pq.print_slip_check finished")
            else:
                payment = 2
                bank = None

            self.progress_updated.emit("Печатаем кассовый чек...", 60)
            time.sleep(0.25) # for view
            state_check = self.pq.check_open(
                self.system.sale_dict,
                self.payment_type,
                self.system.user,
                1,
                self.print_check,
                self.system.sale_dict["detail"][7],
                bank,
                on_error=lambda title, text: self.error_signal.emit("Ошибка ККМ", "Документ не закрылся после 5 попыток. Отмена кассового чека.", "critical"),
            )
            self.log_step(timer, "pq.check_open finished")
            if state_check == 1:
                self.progress_updated.emit("Оплата прошла успешно.", 70)
                time.sleep(0.25) # for view
                if self.print_check == 0:
                    self.info_signal.emit("Оплата прошла успешно.", "Чек не печатаем.", "")
                self.progress_updated.emit("Сохраняем данные в БД...", 80)
                time.sleep(0.25) # for view
                with self.Session(self.system.engine) as session:
                    session.execute(
                        update(Sale)
                        .where(Sale.id == self.system.sale_id)
                        .values(
                            status=1,
                            id_user=self.system.user.id,
                            pc_name=self.system.pc_name,
                            payment_type=payment,
                            datetime=dt.datetime.now(),
                        )
                    )
                    session.commit()
                self.log_step(timer, "save check in db finished")
            self.progress_updated.emit("Печатаем билеты...", 90)
            QMetaObject.invokeMethod(
                self.main_window,
                "print_saved_tickets",
                Qt.QueuedConnection,
            )
            self.log_step(timer, "print_saved_tickets finished")
            self.system.sale_status = 0
            self.progress_updated.emit("Завершено.", 100)
            time.sleep(0.25) # for view
            self.close_window_signal.emit()


        except Exception as e:
            self.error_signal.emit("Ошибка", str(e), True)
            self.progress_updated.emit("Ошибка во время выполнения", 100)
            time.sleep(0.25) # for view

        finally:
            self.system.sale_status = 0
            # Завершаем поток
            self.finished.emit()
            # Закрытие окна после всех операций
            self.close_window_signal.emit()