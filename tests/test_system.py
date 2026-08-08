import base64
import json
import os
import tempfile
import unittest
from datetime import date
from unittest.mock import MagicMock, patch

from db.models import Price
from modules.system import System


class TestSystem(unittest.TestCase):

    def setUp(self):
        patcher = patch('modules.system.create_engine')
        self.mock_create_engine = patcher.start()
        self.addCleanup(patcher.stop)

        System._instance = None

        with patch('modules.system.Config') as mock_config_cls:
            mock_cfg_inst = MagicMock()

            def config_get(key):
                if key == "kol":
                    return "2"
                return "dummy"
            mock_cfg_inst.get.side_effect = config_get
            mock_cfg_inst.pcs = ["PC1", "PC2"]
            mock_config_cls.return_value = mock_cfg_inst

            self.system = System()

    def test_decode_password(self):
        encoded = base64.b64encode(b"mysecret").decode()
        self.assertEqual(System.decode_password(encoded), "mysecret")

    def test_calculate_age(self):
        today = date.today()
        born = date(today.year - 10, today.month, today.day)
        self.assertEqual(System.calculate_age(born), 10)

        if today.month == 12 and today.day == 31:
            born = date(today.year - 9, 1, 1)
        else:
            try:
                born = date(today.year - 10, today.month, today.day + 1)
            except ValueError:
                born = date(today.year - 10, today.month + 1, 1)
        self.assertEqual(System.calculate_age(born), 9)

    @patch('modules.system.Session')
    @patch('modules.system.select')
    def test_user_authorization_success(self, mock_select, mock_Session):
        mock_session_inst = MagicMock()
        mock_Session.return_value.__enter__.return_value = mock_session_inst

        mock_user = MagicMock()
        mock_user.password = base64.b64encode(b"password123").decode()

        mock_session_inst.execute.return_value.scalars.return_value.first.return_value = mock_user

        result = self.system.user_authorization("login1", "password123")
        self.assertEqual(result, 1)
        self.assertEqual(self.system.user, mock_user)

    @patch('modules.system.Session')
    @patch('modules.system.select')
    def test_user_authorization_failure_wrong_password(self, mock_select, mock_Session):
        mock_session_inst = MagicMock()
        mock_Session.return_value.__enter__.return_value = mock_session_inst

        mock_user = MagicMock()
        mock_user.password = base64.b64encode(b"password123").decode()

        mock_session_inst.execute.return_value.scalars.return_value.first.return_value = mock_user

        result = self.system.user_authorization("login1", "wrongpassword")
        self.assertEqual(result, 0)

    @patch('modules.system.Session')
    def test_get_price_with_db_values(self, mock_Session):
        mock_session_inst = MagicMock()
        mock_Session.return_value.__enter__.return_value = mock_session_inst

        mock_prices = []
        for i in range(9):
            p = Price(price=(100 * (i+1)) ^ 42)
            mock_prices.append(p)

        mock_session_inst.query.return_value.order_by.return_value.all.return_value = mock_prices

        self.system.get_price()

        self.assertEqual(self.system.price["ticket_child_1"], 100)

    @patch('modules.system.Session')
    def test_get_price_defaults_on_empty_db(self, mock_Session):
        mock_session_inst = MagicMock()
        mock_Session.return_value.__enter__.return_value = mock_session_inst

        mock_session_inst.query.return_value.order_by.return_value.all.return_value = []

        self.system.get_price()
        self.assertEqual(self.system.price["ticket_child_1"], 250)
        self.assertEqual(self.system.price["ticket_adult_1"], 150)

    @patch('modules.system.Session')
    @patch('modules.system.select')
    @patch('modules.system.dt.datetime')
    def test_check_day_holiday(self, mock_datetime, mock_select, mock_Session):
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01"

        mock_session_inst = MagicMock()
        mock_Session.return_value.__enter__.return_value = mock_session_inst

        def side_effect_first(*args, **kwargs):
            return MagicMock() if "Holiday" in str(mock_select.call_args) else None

        mock_scalars = MagicMock()
        mock_session_inst.execute.return_value.scalars.return_value = mock_scalars
        mock_scalars.first.side_effect = [None, True]

        with patch('modules.system.calendar.weekday', return_value=0):
            result = self.system.check_day()

        self.assertEqual(result, 1)
        self.assertEqual(self.system.what_a_day, 1)

    def test_load_coordinates(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            json.dump({"coordinates": {"name": {"x": 10, "y": 20}}}, f)
            temp_path = f.name

        mock_config = MagicMock()
        mock_config.get.return_value = temp_path

        try:
            coords = self.system.load_coordinates(mock_config)
            self.assertEqual(coords["name"]["x"], 10)
        finally:
            os.remove(temp_path)

    @patch('modules.system.Session')
    @patch('modules.system.select')
    def test_check_db_connection(self, mock_select, mock_Session):
        mock_session_inst = MagicMock()
        mock_Session.return_value.__enter__.return_value = mock_session_inst

        self.assertTrue(self.system.check_db_connection())

        mock_session_inst.execute.side_effect = Exception("DB Error")
        self.assertFalse(self.system.check_db_connection())

    @patch('modules.system.Session')
    @patch('modules.system.select')
    def test_get_slip_data(self, mock_select, mock_Session):
        mock_session_inst = MagicMock()
        mock_Session.return_value.__enter__.return_value = mock_session_inst

        fake_slip = "Номер QR: 123456\nКарта: ************1234\nМ:987654\nRRN: 111222"
        mock_session_inst.execute.return_value.scalars.return_value.one.return_value = fake_slip

        card_tail, merchant_id, rrn_value, load_slip = self.system.get_slip_data(
            1)

        self.assertEqual(card_tail, "1234")
        self.assertEqual(merchant_id, "987654")
        self.assertEqual(rrn_value, "111222")
        self.assertEqual(load_slip, fake_slip)


if __name__ == '__main__':
    unittest.main()

    @patch('modules.system.Session')
    def test_check_day_normal_day(self, mock_Session):
        # We need a clear weekday and no holiday mock
        mock_session_inst = MagicMock()
        mock_Session.return_value.__enter__.return_value = mock_session_inst

        # scalars().first() returns None meaning no holiday
        mock_session_inst.execute.return_value.scalars.return_value.first.return_value = None

        with patch('modules.system.dt.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-02"
            with patch('modules.system.calendar.weekday', return_value=0):  # 0 = Monday = Workday
                self.assertEqual(self.system.check_day(), 0)
