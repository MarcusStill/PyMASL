import datetime as dt

from PySide6.QtCore import QElapsedTimer, QObject, Signal, QMetaObject, Qt, QTimer, QEventLoop
from sqlalchemy import update

from db.models import Sale
from modules.logger import logger


class TransactionWorker(QObject):
    # Константа для задержки
    DEFAULT_DELAY_MS = 15

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

    def delayed_progress_update(self, step_text: str, progress_percent: int, delay_ms: int = DEFAULT_DELAY_MS):
        """
        Обновляет прогресс с гарантированной задержкой перед следующим шагом.
        :param step_text: Текст для отображения
        :param progress_percent: Процент выполнения (0-100)
        :param delay_ms: Минимальная задержка в миллисекундах перед продолжением
        """
        if delay_ms < 0:
            delay_ms = 0
        if delay_ms > 0:
            # Создаем локальный таймер для обеспечения задержки
            timer = QTimer(self)
            timer.setSingleShot(True)

            # Соединяем сигнал таймера с продолжением выполнения
            timer.timeout.connect(lambda: None)  # Просто как маркер завершения задержки

            # Отправляем сигнал прогресса немедленно
            self.progress_updated.emit(step_text, progress_percent)

            # Запускаем таймер задержки
            timer.start(delay_ms)

            # Блокируем выполнение до срабатывания таймера (не блокируя главный цикл Qt)
            loop = QEventLoop()
            timer.timeout.connect(loop.quit)
            loop.exec()

    def run(self):
        timer = QElapsedTimer()
        timer.start()
        try:
            self.delayed_progress_update("Анализ продажи...", 5)
            # Сохраняем новую продажу
            if self.system.sale_id is None:
                self.delayed_progress_update("Сохраняем продажу...", 10)
                self.save_sale_signal.emit()
                self.log_step(timer, "save_sale finished")
            # Особая продажа — только билеты
            if self.system.sale_special == 1:
                self.delayed_progress_update("Печатаем билеты (особая продажа)...", 90)
                QMetaObject.invokeMethod(
                    self.main_window,
                    "print_saved_tickets",
                    Qt.QueuedConnection,
                )
                self.log_step(timer, "print_saved_tickets finished")
                self.close_window_signal.emit()
                return

            # Если оплата банковской картой
            if self.payment_type in (101, 200):
                self.delayed_progress_update("Ожидаем оплату на терминале...", 25)
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
                    self.delayed_progress_update("Ошибка оплаты", 100, 1)
                    self.log_step(timer, "error_signal finished")
                    # Закрытие окна прогресса в случае ошибки
                    self.close_window_signal.emit()
                    # Завершаем поток
                    self.finished.emit()
                    return
                if bank == 0:
                    self.error_signal.emit(
                        "Ошибка",
                        "Операция оплаты не удалась. Повторите попытку.",
                        "",
                    )
                    self.delayed_progress_update("Ошибка оплаты", 100, 1)
                    self.log_step(timer, "payment error finished")
                    # Закрытие окна прогресса в случае ошибки
                    self.close_window_signal.emit()
                    # Завершаем поток
                    self.finished.emit()
                    return
                if bank == 1:
                    self.delayed_progress_update("Сохраняем банковский чек...", 35)
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
                        self.delayed_progress_update("Печатаем слип-чек...", 40)
                        self.pq.print_slip_check()
                        self.log_step(timer, "pq.print_slip_check finished")
            else:
                payment = 2
                bank = None

            self.delayed_progress_update("Печатаем кассовый чек...", 60)
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
                self.delayed_progress_update("Оплата прошла успешно.", 70)
                if self.print_check == 0:
                    self.info_signal.emit("Оплата прошла успешно.", "Чек не печатаем.", "")
                self.delayed_progress_update("Сохраняем данные в БД...", 80)
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
            self.delayed_progress_update("Печатаем билеты...", 90)
            QMetaObject.invokeMethod(
                self.main_window,
                "print_saved_tickets",
                Qt.QueuedConnection,
            )
            self.log_step(timer, "print_saved_tickets finished")
            self.system.sale_status = 0
            self.delayed_progress_update("Завершено.", 100, 1)
            self.log_step(timer, "all steps finished")
            self.close_window_signal.emit()

        except Exception as e:
            self.error_signal.emit("Ошибка", str(e), True)
            self.delayed_progress_update("Ошибка во время выполнения", 100, 1)

        finally:
            self.system.sale_status = 0
            # Завершаем поток
            self.finished.emit()
            # Закрытие окна после всех операций
            self.close_window_signal.emit()
