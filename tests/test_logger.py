import unittest
from unittest.mock import patch, MagicMock
from modules.logger import logger_wraps

class TestLogger(unittest.TestCase):

    def test_logger_wraps_success(self):
        @logger_wraps()
        def dummy_func(x):
            return x * 2

        with patch('modules.logger.logger.opt') as mock_opt:
            mock_logger = MagicMock()
            mock_opt.return_value = mock_logger
            
            result = dummy_func(3)
            self.assertEqual(result, 6)
            
            # Should log entry and exit
            self.assertEqual(mock_logger.log.call_count, 2)
            mock_logger.log.assert_any_call('DEBUG', "Entering '{}' (args={}, kwargs={})", 'dummy_func', (3,), {})
            mock_logger.log.assert_any_call('DEBUG', "Exiting '{}' (result={})", 'dummy_func', 6)

    def test_logger_wraps_exception(self):
        @logger_wraps(level='INFO')
        def failing_func():
            raise ValueError("Test error")

        with patch('modules.logger.logger.opt') as mock_opt:
            mock_logger = MagicMock()
            mock_opt.return_value = mock_logger
            
            with self.assertRaises(ValueError):
                failing_func()
            
            # Should log entry and exception
            self.assertEqual(mock_logger.log.call_count, 1)
            mock_logger.log.assert_any_call('INFO', "Entering '{}' (args={}, kwargs={})", 'failing_func', (), {})
            mock_logger.error.assert_called_once_with("Exception in '{}': {}", 'failing_func', 'Test error')

    def test_logger_wraps_no_entry_exit(self):
        @logger_wraps(entry=False, exit=False)
        def silent_func():
            return True

        with patch('modules.logger.logger.opt') as mock_opt:
            mock_logger = MagicMock()
            mock_opt.return_value = mock_logger
            
            result = silent_func()
            self.assertTrue(result)
            
            # Should not log anything
            mock_logger.log.assert_not_called()

if __name__ == '__main__':
    unittest.main()
