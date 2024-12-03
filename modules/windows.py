from PySide6.QtWidgets import QMessageBox


def info_window(text, infotext, detailed_text):
    """Показ информационного окна"""
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Информационное окно")
    msg.setText(text)
    msg.setInformativeText(infotext)
    msg.setDetailedText(detailed_text)
    msg.exec_()


def info_dialog_window(title, text):
    """Показ диалогового окна"""
    box = QMessageBox()
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    buttonY = box.button(QMessageBox.Yes)
    buttonY.setText("Да")
    buttonN = box.button(QMessageBox.No)
    buttonN.setText("Нет")
    box.exec_()

    if box.clickedButton() == buttonY:
        return 1
    elif box.clickedButton() == buttonN:
        return 0
