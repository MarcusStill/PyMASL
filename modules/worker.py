import datetime as dt
from functools import wraps

from PySide6.QtCore import QElapsedTimer, QObject, Signal, QMetaObject, Qt, QTimer, QEventLoop
from sqlalchemy import update

from db.models import Sale
from modules.logger import logger


def with_timer(func):
    """Декоратор для автоматического создания QElapsedTimer"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        timer = QElapsedTimer()
        timer.start()
        return func(self, timer, *args, **kwargs)
    return wrapper


class BaseWorker(QObject):
    """Базовый класс с общими методами"""
    DEFAULT_DELAY_MS = 15

    progress_updated = Signal(str, int)
    finished = Signal()
    save_sale_signal = Signal()
    error_signal = Signal(str, str, str)
    info_signal = Signal(str)
    print_ticket_signal = Signal()
    close_window_signal = Signal()

    @staticmethod
    def log_step(timer, step_name):
        elapsed = timer.elapsed()
        logger.debug(f"[TIMER] {step_name} — {elapsed} ms")

    def delayed_progress_update(self, step_text: str, progress_percent: int, delay_ms: int = DEFAULT_DELAY_MS):
        if delay_ms < 0:
            delay_ms = 0
        if delay_ms > 0:
            # Создаем локальный таймер для обеспечения задержки
            timer = QTimer(self)
            timer.setSingleShot(True)
            # Отправляем сигнал прогресса немедленно
            self.progress_updated.emit(step_text, progress_percent)
            # Запускаем таймер задержки
            timer.start(delay_ms)
            # Блокируем выполнение до срабатывания таймера (не блокируя главный цикл Qt)
            loop = QEventLoop()
            timer.timeout.connect(loop.quit)
            loop.exec()

    def invoke_main_window_method(self, method_name: str):
        QMetaObject.invokeMethod(
            self.main_window,
            method_name,
            Qt.QueuedConnection,
        )

    def emit_error_and_finish(self, title: str, message: str, code: str = "",
        timer: QElapsedTimer = None, step_name: str = "",
        close_window: bool = True):
        """
        Универсальный метод обработки ошибок
        :param title: Заголовок ошибки
        :param message: Текст ошибки
        :param code: Код ошибки (опционально)
        :param timer: Таймер для логирования
        :param step_name: Название шага для лога
        :param close_window: Нужно ли закрывать окно
        """
        logger.error(f"{title}: {message} (код: {code})")
        self.error_signal.emit(title, message, str(code))
        self.delayed_progress_update(f"Ошибка: {title}", 100, 1)

        if timer and step_name:
            self.log_step(timer, step_name)

        if close_window:
            self.close_window_signal.emit()

        self.finished.emit()

class PaymentHandler:
    """Обработчик банковских платежей"""
    def __init__(self, worker, pq, payment_type, amount):
        self.worker = worker
        self.pq = pq
        self.payment_type = payment_type
        self.amount = amount

    @with_timer
    def process_bank_payment(self, timer: QElapsedTimer):
        """Основной метод обработки банковского платежа"""
        self.worker.delayed_progress_update("Ожидаем оплату на терминале...", 25)
        try:
            # Пытаемся выполнить операцию на терминале
            bank, payment = self.pq.universal_terminal_operation(
                self.payment_type,
                self.amount,
                self.worker.progress_updated,
                error_callback=self._handle_terminal_error_callback
            )
            self.worker.log_step(timer, "pq.universal_terminal_operation finished")

            # Обрабатываем результат операции
            if bank == 0:
                self._handle_payment_failed(timer)
                return False, None
            # Возвращаем только payment
            return True, payment

        except Exception as e:
            self._handle_payment_exception(timer, e)
            return False, None

    def _handle_terminal_error_callback(self, title: str, message: str, code: int) -> None:
        """Callback для обработки ошибок от терминала"""
        self.worker.emit_error_and_finish(
            title=title,
            message=message,
            code=str(code),
            step_name="terminal_error"
        )
        raise Exception(f"{title}: {message}")

    def _handle_payment_failed(self, timer):
        """Обработка неудачного платежа (bank == 0)"""
        self.worker.emit_error_and_finish(
            title="Ошибка",
            message="Операция оплаты не удалась. Повторите попытку.",
            timer=timer,
            step_name="payment_failed"
        )

    def _handle_payment_exception(self, timer, exception):
        """Обработка исключений при проведении платежа"""
        self.worker.emit_error_and_finish(
            title="Ошибка",
            message="Не удалось выполнить операцию на терминале.",
            code=str(exception),
            timer=timer,
            step_name="payment_exception"
        )


class CheckHandler:
    """Обработчик печати чеков"""
    def __init__(self, worker, pq):
        self.worker = worker
        self.pq = pq

    def print_check(self, sale_dict, payment_type, user, print_check, amount, bank_data):
        """Печать кассового чека"""
        state_check = self.pq.check_open(
            sale_dict,
            payment_type,
            user,
            1,
            print_check,
            amount,
            bank_data,
            on_error=self.handle_check_error
        )
        if state_check != 1:
            self.handle_check_error("Ошибка ККМ", "Документ не закрылся")
            return False

        return True

    def handle_check_error(self, title="Неизвестная ошибка", text="Произошла неизвестная ошибка"):
        """Обработчик ошибок печати чека"""
        logger.error(f"handle_check_error вызван с title={title}, text={text}")
        self.worker.emit_error_and_finish(
            title="Ошибка ККМ",
            message="Документ не закрылся после 5 попыток. Отмена кассового чека.",
            code="critical",
            step_name="check_error"
        )
        raise Exception(f"{title}: {text}")


class DatabaseHandler:
    """Обработчик работы с базой данных"""
    def __init__(self, Session, engine):
        self.Session = Session
        self.engine = engine

    def update_sale(self, sale_id, **values):
        """Общее сохранение данных о продаже"""
        with self.Session(self.engine) as session:
            session.execute(
                update(Sale)
                .where(Sale.id == sale_id)
                .values(**values)
            )
            session.commit()


class TransactionWorker(BaseWorker):
    """Основной класс обработки транзакций"""
    def __init__(self, payment_type, print_check, system, pq, Session, main_window, parent=None):
        super().__init__(parent)
        self.payment_type = payment_type
        self.print_check = print_check
        self.system = system
        self.pq = pq
        self.Session = Session
        self.main_window = main_window

        amount = system.sale_dict["detail"][7]

        # Инициализация обработчиков
        self.payment_handler = PaymentHandler(self, pq, payment_type, amount)
        self.check_handler = CheckHandler(self, pq)
        self.db_handler = DatabaseHandler(Session, system.engine)

    @with_timer
    def process_special_sale(self, timer: QElapsedTimer, progress_percent: int):
        """Обработка специальной продажи"""
        self.delayed_progress_update("Печатаем билеты (особая продажа)...", progress_percent)
        self.invoke_main_window_method("print_saved_tickets")
        self.log_step(timer, "print_saved_tickets finished")
        self.close_window_signal.emit()

    def process_payment(self, timer):
        """Обработка платежа"""
        # По умолчанию наличные
        payment = 2
        bank_data = None

        if self.payment_type in (101, 200):
            success, payment = self.payment_handler.process_bank_payment()
            if not success:
                self.close_window_signal.emit()
                self.finished.emit()
                return None, None

            # Сохраняем банковский чек
            self.delayed_progress_update("Сохраняем банковский чек...", 45)
            if payment == 3:
                check = "offline"
            else:
                check = self.pq.read_pinpad_file(remove_newline=False)
                self.log_step(timer, "pq.read_pinpad_file finished")

            self.db_handler.update_sale(self.system.sale_id,bank_pay=check)
            self.log_step(timer, "save in db finished")

            if self.print_check == 1 and payment == 1:
                self.delayed_progress_update("Печатаем слип-чек...", 50)
                self.pq.print_slip_check()
                self.log_step(timer, "pq.print_slip_check finished")

            bank_data = check

        return payment, bank_data

    def process_checks(self, timer, payment, bank_data):
        """Печать чеков"""
        self.delayed_progress_update("Печатаем кассовый чек...", 60)
        try:
            if not self.check_handler.print_check(
                self.system.sale_dict,
                self.payment_type,
                self.system.user,
                self.print_check,
                self.system.sale_dict["detail"][7],
                bank_data
            ):
                return False

            self.log_step(timer, "pq.check_open finished")

            self.delayed_progress_update("Оплата прошла успешно.", 70)
            if self.print_check == 0:
                self.info_signal.emit("Оплата прошла успешно.", "Чек не печатаем.", "")

            self.delayed_progress_update("Сохраняем данные в БД...", 80)
            self.db_handler.update_sale(
                self.system.sale_id,
                status=1,
                id_user=self.system.user.id,
                pc_name=self.system.pc_name,
                payment_type=payment,
                datetime=dt.datetime.now(),
            )
            self.log_step(timer, "save check in db finished")

            return True

        except Exception as e:
            logger.exception("Ошибка при печати чеков: %s", e)
            return False

    def finalize_transaction(self, timer):
        """Завершение транзакции"""
        self.delayed_progress_update("Печатаем билеты...", 90)
        self.invoke_main_window_method("print_saved_tickets")
        self.log_step(timer, "print_saved_tickets finished")
        self.system.sale_status = 0
        self.delayed_progress_update("Завершено.", 100, 1)
        self.log_step(timer, "all steps finished")
        self.close_window_signal.emit()

    def handle_error(self, error, timer):
        """Обработка ошибок"""
        self.emit_error_and_finish(
            title="Ошибка",
            message="Не удалось выполнить операцию на терминале.",
            code=str(error),
            timer=timer,
            step_name="transaction_error",
            close_window=True
        )
        self.system.sale_status = 0

    def cleanup(self):
        """Завершающие действия"""
        self.system.sale_status = 0
        self.finished.emit()
        self.close_window_signal.emit()

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
                self.process_special_sale(90)
                return

            # Обработка платежа
            payment, bank_data = self.process_payment(timer)
            # Если была ошибка
            if payment is None:
                return

            # Печать чеков
            if not self.process_checks(timer, payment, bank_data):
                return

            # Завершение транзакции
            self.finalize_transaction(timer)

        except Exception as e:
            self.handle_error(e, timer)
        finally:
            self.cleanup()
