from PySide6.QtWidgets import QMessageBox


def info_window(text, detailed_text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    #msg.setInformativeText("This is additional information")
    msg.setWindowTitle("MessageBox")
    msg.setDetailedText(detailed_text)
    msg.exec_()