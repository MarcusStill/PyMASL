import unittest
import sys
from unittest.mock import patch, MagicMock

# Mock PySide6 BEFORE importing modules.windows
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()

import modules.windows

class TestWindows(unittest.TestCase):

    @patch('modules.windows.QMessageBox')
    def test_info_window(self, mock_msgbox_class):
        mock_msgbox_inst = MagicMock()
        mock_msgbox_class.return_value = mock_msgbox_inst

        modules.windows.info_window("Text", "Info", "Detail")

        mock_msgbox_inst.setText.assert_called_with("Text")
        mock_msgbox_inst.setInformativeText.assert_called_with("Info")
        mock_msgbox_inst.setDetailedText.assert_called_with("Detail")
        self.assertTrue(mock_msgbox_inst.exec.called)

    @patch('modules.windows.QMessageBox')
    def test_info_dialog_window_yes(self, mock_msgbox_class):
        mock_msgbox_inst = MagicMock()
        mock_msgbox_class.return_value = mock_msgbox_inst
        mock_msgbox_class.Yes = 1
        mock_msgbox_class.No = 2

        buttonY = MagicMock()
        mock_msgbox_inst.button.side_effect = [buttonY, MagicMock()]
        mock_msgbox_inst.clickedButton.return_value = buttonY

        result = modules.windows.info_dialog_window("Title", "Text")

        mock_msgbox_inst.setWindowTitle.assert_called_with("Title")
        mock_msgbox_inst.setText.assert_called_with("Text")
        self.assertTrue(mock_msgbox_inst.exec.called)
        self.assertEqual(result, 1)

    @patch('modules.windows.QMessageBox')
    def test_info_dialog_window_no(self, mock_msgbox_class):
        mock_msgbox_inst = MagicMock()
        mock_msgbox_class.return_value = mock_msgbox_inst
        mock_msgbox_class.Yes = 1
        mock_msgbox_class.No = 2

        buttonN = MagicMock()
        mock_msgbox_inst.button.side_effect = [MagicMock(), buttonN]
        mock_msgbox_inst.clickedButton.return_value = buttonN

        result = modules.windows.info_dialog_window("Title", "Text")

        self.assertEqual(result, 0)

if __name__ == '__main__':
    unittest.main()
