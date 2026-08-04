import unittest
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock

import modules.sale_logic as sl
import modules.system

class TestSaleLogic(unittest.TestCase):

    def setUp(self):
        # We must re-bind the system instance in sl to our mocked one
        self.system = modules.system.System()

        self.system.age = {"min": 5, "max": 15}
        self.system.price = {
            "ticket_child_1": 250,
            "ticket_child_2": 500,
            "ticket_child_3": 750,
            "ticket_child_week_1": 300,
            "ticket_child_week_2": 600,
            "ticket_child_week_3": 900,
            "ticket_adult_1": 150,
            "ticket_adult_2": 200,
            "ticket_adult_3": 250,
            "ticket_free": 0,
        }
        self.system.talent = {"1_hour": 25, "2_hour": 35, "3_hour": 50}
        self.system.sale_dict = {
            "kol_adult": 0,
            "price_adult": 0,
            "kol_child": 0,
            "price_child": 0,
            "detail": [0, 0, 0, 0, 0, 0, 1, 0],
        }
        self.system.count_number_of_visitors = {
            "kol_adult": 0,
            "kol_child": 0,
            "kol_sale_adult": 0,
            "kol_sale_child": 0,
            "kol_adult_many_child": 0,
            "kol_child_many_child": 0,
            "kol_adult_invalid": 0,
            "kol_child_invalid": 0,
            "id_adult": 0,
            "many_child": 0,
            "invalid": 0,
            "talent": 0,
        }
        self.system.what_a_day = 0 # 0=weekday, 1=weekend

        # Override the system object inside the sale_logic module
        self.original_system = sl.system
        sl.system = self.system

    def tearDown(self):
        sl.system = self.original_system

    def test_calculate_age(self):
        with patch('modules.sale_logic.get_today_date', return_value=date(2024, 1, 1)):
            self.assertEqual(sl.calculate_age(date(2000, 1, 1)), 24)
            self.assertEqual(sl.calculate_age(date(2000, 1, 2)), 23)

    def test_calculate_ticket_type(self):
        self.assertEqual(sl.calculate_ticket_type(4), "бесплатный")
        self.assertEqual(sl.calculate_ticket_type(5), "детский")
        self.assertEqual(sl.calculate_ticket_type(14), "детский")
        self.assertEqual(sl.calculate_ticket_type(15), "взрослый")

    def test_calculated_ticket_price(self):
        self.assertEqual(sl.calculated_ticket_price("взрослый", 1), 150)
        self.assertEqual(sl.calculated_ticket_price("детский", 2), 500)
        self.assertEqual(sl.calculated_ticket_price("бесплатный", 1), 0)
        with self.assertRaises(KeyError):
            sl.calculated_ticket_price("взрослый", 4)

    def test_calculate_adult_price(self):
        self.system.sale_dict["detail"][6] = 1
        self.assertEqual(sl.calculate_adult_price(), 150)

        self.system.sale_dict["detail"][6] = 2
        self.system.count_number_of_visitors["many_child"] = 1
        self.assertEqual(sl.calculate_adult_price(), 0)

        self.system.sale_dict["detail"][6] = 3
        self.system.count_number_of_visitors["invalid"] = 1
        self.assertEqual(sl.calculate_adult_price(), 0)

    def test_calculate_child_price(self):
        self.system.sale_dict["detail"][6] = 1
        self.assertEqual(sl.calculate_child_price(), 250)

        self.system.what_a_day = 1
        self.assertEqual(sl.calculate_child_price(), 300)

        self.system.what_a_day = 0
        self.system.sale_dict["detail"][6] = 2
        self.system.count_number_of_visitors["many_child"] = 1
        self.assertEqual(sl.calculate_child_price(), 0)

        self.system.sale_dict["detail"][6] = 3
        self.system.count_number_of_visitors["invalid"] = 1
        self.assertEqual(sl.calculate_child_price(), 0)

    def test_calculate_discounted_price(self):
        self.system.count_number_of_visitors["many_child"] = 1
        price, cat, status = sl.calculate_discounted_price(500, "детский")
        self.assertEqual(price, 0)
        self.assertEqual(self.system.sale_special, 1)

        self.system.count_number_of_visitors["many_child"] = 2
        price, cat, status = sl.calculate_discounted_price(500, "детский")
        self.assertEqual(price, 250)

        self.system.count_number_of_visitors["many_child"] = 0
        self.system.count_number_of_visitors["invalid"] = 1
        price, cat, status = sl.calculate_discounted_price(500, "взрослый")
        self.assertEqual(price, 0)
        self.assertEqual(cat, "с")

    def test_calculate_discount(self):
        self.assertEqual(sl.calculate_discount(100, 20), Decimal("80.00"))
        self.assertEqual(sl.calculate_discount(100, -10), Decimal("100.00"))
        self.assertEqual(sl.calculate_discount(100, 150), Decimal("0.00"))

    def test_calculate_itog(self):
        self.system.sale_dict = {
            "kol_adult": 5,
            "price_adult": 100,
            "kol_child": 3,
            "price_child": 50,
            "detail": [2, 20, 1, 10, 0, 0, 0, 0] # adult_dis_cnt, adult_dis_price, child_dis_cnt, child_dis_price
        }
        res = sl.calculate_itog()
        # 3*100 + 2*50 + 2*20 + 1*10 = 300 + 100 + 40 + 10 = 450
        self.assertEqual(res, 450)

    def test_get_talent_based_on_time(self):
        self.assertEqual(sl.get_talent_based_on_time(1), (1, 25))
        self.assertEqual(sl.get_talent_based_on_time(2), (2, 35))
        self.assertEqual(sl.get_talent_based_on_time(3), (3, 50))
        self.assertEqual(sl.get_talent_based_on_time(4), (0, 0))

    def test_update_sale_dict_methods(self):
        self.system.count_number_of_visitors["kol_adult_many_child"] = 2
        sl.update_sale_dict_adult_many_child()
        self.assertEqual(self.system.sale_dict["detail"][0], 2)
        self.assertEqual(self.system.sale_dict["detail"][1], 0)

        self.system.count_number_of_visitors["kol_adult_invalid"] = 1
        sl.update_sale_dict_adult_invalid()
        self.assertEqual(self.system.sale_dict["detail"][0], 1)
        self.assertEqual(self.system.sale_dict["detail"][1], 0)

        self.system.count_number_of_visitors["kol_child_many_child"] = 3
        sl.update_sale_dict_child_many_child()
        self.assertEqual(self.system.sale_dict["detail"][2], 3)
        self.assertEqual(self.system.sale_dict["detail"][3], 0)

        self.system.count_number_of_visitors["kol_child_invalid"] = 4
        sl.update_sale_dict_child_invalid()
        self.assertEqual(self.system.sale_dict["detail"][2], 4)
        self.assertEqual(self.system.sale_dict["detail"][3], 0)

    def test_update_counts(self):
        sl.update_adult_count()
        self.assertEqual(self.system.count_number_of_visitors["kol_adult"], 1)
        self.assertEqual(self.system.sale_dict["kol_adult"], 1)

        sl.update_child_count()
        self.assertEqual(self.system.count_number_of_visitors["kol_child"], 1)
        self.assertEqual(self.system.sale_dict["kol_child"], 1)

    def test_convert_sale_dict_values(self):
        sale_dict = {
            "price_adult": Decimal("250.0"),
            "price_child": Decimal("750.5"),
            "detail": [Decimal("125.0"), 375.5, "some_string"],
        }
        updated = sl.convert_sale_dict_values(sale_dict)
        self.assertEqual(updated["price_adult"], 250)
        self.assertEqual(updated["price_child"], 750.5)
        self.assertEqual(updated["detail"], [125, 375.5, "some_string"])

    def test_generating_parts_for_partial_returns(self):
        tickets = {"adult": [100, 2], "child": [50, 2]}
        amount = 120
        res = sl.generating_parts_for_partial_returns(tickets, amount)
        self.assertEqual(res, {"adult": [100, 1], "child акция": [20, 1]})

        self.assertEqual(sl.generating_parts_for_partial_returns("not a dict", 100), {})
        self.assertEqual(sl.generating_parts_for_partial_returns(tickets, -10), {})

if __name__ == '__main__':
    unittest.main()
