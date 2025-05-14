from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QMessageBox as MB

from design.logic.progress_dialog import Ui_ProgressDialog
from modules.logger import logger


class ProgressWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Блокируем только родительское окно
        self.setModal(True)

        self.ui = Ui_ProgressDialog()
        self.ui.setupUi(self)
        # Отображение поверх остальных окон
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Стилизация окна и прогрессбара
        self.setWindowTitle("Выполнение операции")



        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 20px;
            }

            QLabel {
                color: #333;
                font: bold 14px;
            }

            QProgressBar {
                background-color: #f5f5f5;
                border: 2px solid #bbb;
                border-radius: 5px;
                text-align: center;
                color: black;
                font-weight: bold;
                font-size: 18px;
            }

            QProgressBar::chunk {
                background-color: #4caf50;
                width: 20px;
                margin: 0.5px;
                border-radius: 5px;
            }

            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }

            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

    def update_status(self, step_text: str, progress_percent: int):
        """
        Обновляет статус выполнения процесса, отображая текст и прогресс.

        Параметры:
            step_text (str): Текст, который будет отображен в статусной метке.
            progress_percent (int): Процент выполнения процесса (от 0 до 100), который будет отображен на прогресс-баре.

        Возвращаемое значение:
            None: Эта функция не возвращает значения, но обновляет элементы пользовательского интерфейса (метка и прогресс-бар).
        """
        logger.debug(f"Progress update: {step_text} - {progress_percent}%")
        # Обновляем текст
        self.ui.label_status.setText(step_text)
        # Обновляем прогресс
        self.ui.progressBar.setValue(progress_percent)
