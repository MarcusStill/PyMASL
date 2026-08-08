import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

import sys
sys.modules['reportlab'] = MagicMock()
sys.modules['reportlab.lib'] = MagicMock()
sys.modules['reportlab.lib.colors'] = MagicMock()
sys.modules['reportlab.lib.pagesizes'] = MagicMock()
sys.modules['reportlab.lib.pagesizes'].landscape = lambda x: x
sys.modules['reportlab.lib.pagesizes'].A4 = "A4"
sys.modules['reportlab.lib.pagesizes'].letter = "letter"
sys.modules['reportlab.lib.units'] = MagicMock()
sys.modules['reportlab.lib.units'].mm = 1
sys.modules['reportlab.lib.units'].inch = 1
sys.modules['reportlab.pdfbase'] = MagicMock()
sys.modules['reportlab.pdfbase.pdfmetrics'] = MagicMock()
sys.modules['reportlab.pdfbase.ttfonts'] = MagicMock()
sys.modules['reportlab.pdfgen'] = MagicMock()
sys.modules['reportlab.platypus'] = MagicMock()
sys.modules['reportlab.platypus'].Table = MagicMock()
sys.modules['reportlab.platypus'].TableStyle = MagicMock()

from modules.otchet import (
    get_ticket_type,
    generate_ticket_report_table,
    safe_int,
    format_date_range,
    process_sales_and_returns,
    process_ticket_stats
)  # noqa: E402
import modules.otchet as otchet  # noqa: E402

class TestOtchet(unittest.TestCase):

    def test_get_ticket_type(self):
        self.assertEqual(get_ticket_type(3), "бесплатный")
        self.assertEqual(get_ticket_type("4"), "бесплатный")
        self.assertEqual(get_ticket_type(5), "детский")
        self.assertEqual(get_ticket_type(14), "детский")
        self.assertEqual(get_ticket_type(15), "взрослый")
        self.assertEqual(get_ticket_type(99), "взрослый")

        with self.assertRaises(ValueError):
            get_ticket_type(-1)

        with self.assertRaises(ValueError):
            get_ticket_type("invalid")

    def test_safe_int(self):
        self.assertEqual(safe_int(5), 5)
        self.assertEqual(safe_int("5"), 5)
        self.assertEqual(safe_int(5.5), 5)
        self.assertEqual(safe_int("5.5"), 5)
        self.assertEqual(safe_int(None), 0)
        self.assertEqual(safe_int("None"), 0)
        self.assertEqual(safe_int([]), 0)
        self.assertEqual(safe_int({}), 0)
        self.assertEqual(safe_int("invalid"), 0)

    def test_format_date_range(self):
        dt1, dt2 = format_date_range(
            "2023-10-01 12:00:00", "2023-10-02 15:30:00")
        self.assertEqual(dt1, "01-10-2023")
        self.assertEqual(dt2, "02-10-2023")

    def test_generate_ticket_report_table(self):
        summary = {
            "Взрослый, 1 ч.": {
                250: {"count": 2, "total_price": 500}
            },
            "Детский, 2 ч.": {
                500: {"count": 1, "total_price": 500}
            }
        }
        table = generate_ticket_report_table(summary)

        self.assertEqual(table[0], ["№\n п/п", "Тип\nбилета",
                         "Цена,\n руб.", "Количество,\n шт.", "Стоимость,\n руб."])
        self.assertIn(["1", "Взрослый, 1 ч.", 250, 2, 500], table)
        self.assertEqual(table[-1][1], "Итого билетов")
        self.assertEqual(table[-1][3], 3)
        self.assertEqual(table[-1][4], 1000)

    @patch('modules.otchet.system')
    def test_process_sales_and_returns(self, mock_system):
        mock_system.pcs = ["PC1", "PC2"]
        sales = [("PC1", 1, 1000), ("PC1", 2, 500), ("PC2", 1, 200)]
        returns = [("PC1", 1, 100, 2), ("PC2", 2, 50, 2)]
        result = process_sales_and_returns(sales, returns)
        pc1_row = next(r for r in result if r[0] == "PC1")
        self.assertEqual(pc1_row[1], 1000)
        self.assertEqual(pc1_row[2], 500)
        pc2_row = next(r for r in result if r[0] == "PC2")
        self.assertEqual(pc2_row[1], 200)
        total_row = result[-1]
        self.assertEqual(total_row[0], "Итого")
        self.assertEqual(total_row[1], 1200)

    @patch('modules.otchet.system')
    def test_process_ticket_stats(self, mock_system):
        tickets = [
            (0, 1, "-", None, None, 100),
            (1, 2, "-", None, None, 200),
            (2, 3, "м", None, None, 0),
            (0, 3, "м", None, None, 0),
            (4, 3, "и", None, None, 0),
        ]
        result = process_ticket_stats(tickets)
        self.assertEqual(len(result), 6)
        adult_stats = next(r for r in result if r[0] == "взрослый")[1]
        self.assertEqual(adult_stats["sum"], 1)

    @patch('modules.otchet.canvas.Canvas')
    def test_otchet_administratora(self, mock_canvas_class):
        mock_canvas_inst = MagicMock()
        mock_canvas_class.return_value = mock_canvas_inst

        values = {"Взрослый, 1 ч.": {250: {"count": 2, "total_price": 500}}}
        otchet.otchet_administratora(
            "2023-10-01 12:00:00", "2023-10-02 15:30:00", values)

        self.assertTrue(mock_canvas_class.called)
        self.assertTrue(mock_canvas_inst.save.called)

    @patch('modules.otchet.canvas.Canvas')
    def test_otchet_kassira(self, mock_canvas_class):
        mock_canvas_inst = MagicMock()
        mock_canvas_class.return_value = mock_canvas_inst

        val = [1000, 500, 100, 50]
        kassir = MagicMock()
        kassir.last_name = "Иванов"
        kassir.first_name = "Иван"
        kassir.middle_name = "Иванович"

        otchet.otchet_kassira(val, "2023-10-01 12:00:00",
                              "2023-10-02 15:30:00", kassir)
        self.assertTrue(mock_canvas_class.called)
        self.assertTrue(mock_canvas_inst.save.called)

    @patch('modules.otchet.canvas.Canvas')
    @patch('modules.otchet.system.load_coordinates')
    def test_generate_saved_tickets(self, mock_load_coords, mock_canvas_class):
        mock_canvas_inst = MagicMock()
        mock_canvas_class.return_value = mock_canvas_inst

        mock_load_coords.return_value = {
            "name": {"x": 10, "y": 20},
            "surname": {"x": 10, "y": 20},
            "age": {"x": 10, "y": 20},
            "duration": {"x": 10, "y": 20},
            "date": {"x": 10, "y": 20},
            "guest": {"x": 10, "y": 20},
            "city": {"x": 10, "y": 20},
            "place": {"x": 10, "y": 20},
            "price": {"x": 10, "y": 20},
            "ticket_type": {"x": 10, "y": 20},
            "notes": {"x": 10, "y": 20},
            "talents": {"x": 10, "y": 20},
            "qr_code": {"x": 10, "y": 20}
        }

        values = [
            ("Иванов", "Иван", 1, 500, "-", 1, 10, 3, 50, "2023-10-01")
        ]
        otchet.generate_saved_tickets(values)
        self.assertTrue(mock_canvas_class.called)
        self.assertTrue(mock_canvas_inst.save.called)


if __name__ == '__main__':
    unittest.main()
