import unittest
from unittest.mock import MagicMock, patch
import datetime as dt

from modules.auth_logic import perform_pre_sale_checks
from modules.system import System

class TestAuthLogic(unittest.TestCase):

    def setUp(self):
        # Prevent System from trying to connect to a real DB
        patcher = patch('modules.system.create_engine')
        self.mock_create_engine = patcher.start()
        self.addCleanup(patcher.stop)

        self.system = System()
        self.system.what_a_day = None
        self.system.num_of_week = None
        self.system.sunday = 0

    def tearDown(self):
        self.system.what_a_day = None
        self.system.num_of_week = None
        self.system.sunday = 0

    def test_perform_pre_sale_checks_authorization_success(self):
        self.system.user_authorization = MagicMock(return_value=1)
        self.system.get_price = MagicMock()
        self.system.check_day = MagicMock(return_value=0)

        result = perform_pre_sale_checks("valid_login", "valid_password")
        self.assertEqual(result, 1)
        self.system.user_authorization.assert_called_once_with("valid_login", "valid_password")

    def test_perform_pre_sale_checks_authorization_failure(self):
        self.system.user_authorization = MagicMock(return_value=0)

        result = perform_pre_sale_checks("invalid_login", "invalid_password")
        self.assertEqual(result, 0)
        self.system.user_authorization.assert_called_once_with("invalid_login", "invalid_password")

    @patch('modules.auth_logic.dt')
    def test_check_day_status_weekday(self, mock_dt):
        mock_date = dt.datetime(2024, 11, 6) # Wednesday
        mock_dt.datetime.today.return_value = mock_date

        self.system.user_authorization = MagicMock(return_value=1)
        self.system.get_price = MagicMock()
        self.system.check_day = MagicMock(return_value=0)

        result = perform_pre_sale_checks("valid_login", "valid_password")
        self.assertEqual(result, 1)
        self.assertEqual(self.system.what_a_day, 0)

    @patch('modules.auth_logic.dt')
    def test_check_day_status_weekend(self, mock_dt):
        mock_date = dt.datetime(2024, 11, 2) # Saturday
        mock_dt.datetime.today.return_value = mock_date

        self.system.user_authorization = MagicMock(return_value=1)
        self.system.get_price = MagicMock()
        self.system.check_day = MagicMock(return_value=1)

        result = perform_pre_sale_checks("valid_login", "valid_password")
        self.assertEqual(result, 1)
        self.assertEqual(self.system.what_a_day, 1)

    @patch('modules.auth_logic.dt')
    def test_sunday_for_large_families_yes(self, mock_dt):
        mock_date = MagicMock()
        mock_date.isoweekday.return_value = 7
        mock_date.day = 3
        mock_dt.datetime.today.return_value = mock_date

        self.system.user_authorization = MagicMock(return_value=1)
        self.system.get_price = MagicMock()
        self.system.check_day = MagicMock(return_value=0)

        result = perform_pre_sale_checks("valid", "valid")
        self.assertEqual(result, 1)
        self.assertEqual(self.system.sunday, 1)

    @patch('modules.auth_logic.dt')
    def test_sunday_for_large_families_no_not_sunday(self, mock_dt):
        mock_date = MagicMock()
        mock_date.isoweekday.return_value = 1
        mock_date.day = 4
        mock_dt.datetime.today.return_value = mock_date

        self.system.user_authorization = MagicMock(return_value=1)
        self.system.get_price = MagicMock()
        self.system.check_day = MagicMock(return_value=0)

        result = perform_pre_sale_checks("valid", "valid")
        self.assertEqual(result, 1)
        self.assertEqual(self.system.sunday, 0)

    @patch('modules.auth_logic.dt')
    def test_sunday_for_large_families_no_not_first_week(self, mock_dt):
        mock_date = MagicMock()
        mock_date.isoweekday.return_value = 7
        mock_date.day = 10
        mock_dt.datetime.today.return_value = mock_date

        self.system.user_authorization = MagicMock(return_value=1)
        self.system.get_price = MagicMock()
        self.system.check_day = MagicMock(return_value=0)

        result = perform_pre_sale_checks("valid", "valid")
        self.assertEqual(result, 1)
        self.assertEqual(self.system.sunday, 0)

    @patch('modules.auth_logic.dt')
    def test_week_and_month_day_assignment(self, mock_dt):
        mock_date = MagicMock()
        mock_date.isoweekday.return_value = 3
        mock_date.day = 6
        mock_dt.datetime.today.return_value = mock_date

        self.system.user_authorization = MagicMock(return_value=1)
        self.system.get_price = MagicMock()
        self.system.check_day = MagicMock(return_value=0)

        result = perform_pre_sale_checks("valid_login", "valid_password")

        self.assertEqual(result, 1)
        self.assertEqual(self.system.num_of_week, 3)

if __name__ == '__main__':
    unittest.main()
