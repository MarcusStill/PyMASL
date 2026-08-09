import unittest
from unittest.mock import patch, MagicMock
from modules.system import System
import base64
import json
import tempfile
from datetime import date
from db.models import Price

class TestSystem(unittest.TestCase):
    def setUp(self):
        # By-pass __init__ and provide dummy values to prevent DB init error
        self.patcher = patch('modules.system.create_engine')
        self.mock_create_engine = self.patcher.start()
        
        System._instance = None
        
        with patch.dict('os.environ', {'DB_PASSWORD': 'dummy', 'DB_USER': 'dummy', 'DB_NAME': 'dummy', 'DB_HOST': 'dummy'}):
            self.system = System()
            
    def tearDown(self):
        self.patcher.stop()

    def test_decode_password(self):
        encoded = base64.b64encode(b"mysecret").decode()
        self.assertEqual(System.decode_password(encoded), "mysecret")

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

    @patch('modules.system.dt.datetime')
    @patch('modules.system.select')
    @patch('modules.system.Session')
    def test_check_day_holiday(self, mock_Session, mock_select, mock_datetime):
        mock_datetime.now.return_value.strftime.return_value = "2024-01-01"
        
        mock_session_inst = MagicMock()
        mock_Session.return_value.__enter__.return_value = mock_session_inst
        
        # When querying Calendar or Holiday, we want first() to return a Holiday object
        # The easiest way is to mock scalars().first() to return a mock
        mock_scalars = MagicMock()
        mock_session_inst.execute.return_value.scalars.return_value = mock_scalars
        mock_scalars.first.side_effect = [None, True] # First for Calendar, second for Holiday
        
        with patch('modules.system.calendar.weekday', return_value=0):
            result = self.system.check_day()
            
        self.assertEqual(result, 1)

    def test_calculate_age(self):
        age = self.system.calculate_age(born=date(2020, 1, 1))
        self.assertEqual(age, 6)

    def test_load_coordinates(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            json.dump({"coordinates": {"name": {"x": 10, "y": 20}}}, f)
            temp_path = f.name
            
        mock_config = MagicMock()
        mock_config.get.return_value = temp_path
        
        try:
            coords = self.system.load_coordinates(mock_config)
            self.assertEqual(coords, {"name": {"x": 10, "y": 20}})
        finally:
            import os
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
        
        fake_slip = "Номер QR: 123456\nКарта: ************1234\nМ:987654\nRRN: 111222\nОстаток:"
        mock_session_inst.execute.return_value.scalars.return_value.one.return_value = fake_slip
        
        card_tail, merchant_id, rrn_value, load_slip = self.system.get_slip_data(1)
        self.assertEqual(card_tail, "1234")
        self.assertEqual(merchant_id, "987654")
        self.assertEqual(rrn_value, "111222")

if __name__ == '__main__':
    unittest.main()
