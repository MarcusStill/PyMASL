import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from modules.otchet import (
    get_ticket_type,
    generate_ticket_report_table,
    safe_int,
    format_date_range,
    process_sales_and_returns,
    process_ticket_stats
)

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
        dt1, dt2 = format_date_range("2023-10-01 12:00:00", "2023-10-02 15:30:00")
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

        # Check header
        self.assertEqual(table[0], ["№\n п/п", "Тип\nбилета", "Цена,\n руб.", "Количество,\n шт.", "Стоимость,\n руб."])

        # Check data row
        self.assertIn(["1", "Взрослый, 1 ч.", 250, 2, 500], table)

        # Ensure aggregates are calculated properly
        # The last row is "Итого билетов"
        self.assertEqual(table[-1][1], "Итого билетов")
        self.assertEqual(table[-1][3], 3) # 2 adult + 1 child
        self.assertEqual(table[-1][4], 1000) # 500 + 500

    @patch('modules.otchet.system')
    def test_process_sales_and_returns(self, mock_system):
        mock_system.pcs = ["PC1", "PC2"]

        sales = [
            ("PC1", 1, 1000), # Card
            ("PC1", 2, 500),  # Cash
            ("PC2", 1, 200)   # Card
        ]
        returns = [
            ("PC1", 1, 100, 2), # Card return
            ("PC2", 2, 50, 2)   # Cash return
        ]

        result = process_sales_and_returns(sales, returns)

        # Find PC1 row
        pc1_row = next(r for r in result if r[0] == "PC1")
        self.assertEqual(pc1_row[1], 1000) # Card sales
        self.assertEqual(pc1_row[2], 500) # Cash sales
        self.assertEqual(pc1_row[4], 100) # Card returns
        self.assertEqual(pc1_row[5], 0) # Cash returns

        # Find PC2 row
        pc2_row = next(r for r in result if r[0] == "PC2")
        self.assertEqual(pc2_row[1], 200) # Card sales
        self.assertEqual(pc2_row[2], 0) # Cash sales
        self.assertEqual(pc2_row[4], 0) # Card returns
        self.assertEqual(pc2_row[5], 50) # Cash returns

        # Check totals row (last)
        total_row = result[-1]
        self.assertEqual(total_row[0], "Итого")
        self.assertEqual(total_row[1], 1200) # 1000 + 200
        self.assertEqual(total_row[2], 500)
        self.assertEqual(total_row[6], 150) # total returns

    @patch('modules.otchet.system')
    def test_process_ticket_stats(self, mock_system):
        # Format: (ticket_type, arrival_time, description, _, _, price)
        tickets = [
            (0, 1, "-", None, None, 100), # Взрослый, 1 ч.
            (1, 2, "-", None, None, 200), # Детский, 2 ч.
            (2, 3, "м", None, None, 0),   # Многодетный взрослый, 3 ч (ticket_type=2 means +2 = 4 -> doesn't match map properly depending on logic, let's use 0 with "м")
            (0, 3, "м", None, None, 0),   # This maps to key (2, 3) -> "Многодетный взрослый, 3 ч."
            (4, 3, "и", None, None, 0),   # Инвалид
        ]

        result = process_ticket_stats(tickets)

        # Check that it returns 6 categories
        self.assertEqual(len(result), 6)

        # Find results
        adult_stats = next(r for r in result if r[0] == "взрослый")[1]
        self.assertEqual(adult_stats["sum"], 1)
        self.assertEqual(adult_stats["t_1"], 1)

        child_stats = next(r for r in result if r[0] == "детский")[1]
        self.assertEqual(child_stats["sum"], 1)
        self.assertEqual(child_stats["t_2"], 1)

        many_adult_stats = next(r for r in result if r[0] == "многодетный взр.")[1]
        self.assertEqual(many_adult_stats["sum"], 1)
        self.assertEqual(many_adult_stats["t_3"], 1)

if __name__ == '__main__':
    unittest.main()
