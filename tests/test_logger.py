import unittest
from unittest.mock import patch

from modules.logger import logger, logger_wraps


class TestLogger(unittest.TestCase):
    def test_logger_wraps_success(self):
        @logger_wraps()
        def test_func():
            return "success"

        with patch.object(logger, "info"):
            res = test_func()
            self.assertEqual(res, "success")

    def test_logger_wraps_exception(self):
        @logger_wraps()
        def test_func():
            raise ValueError("Test Error")

        with patch.object(logger, "exception"):
            with self.assertRaises(ValueError):
                test_func()

    def test_logger_wraps_no_entry_exit(self):
        @logger_wraps(entry=False, exit=False)
        def test_func():
            return "success"

        with patch.object(logger, "info"):
            res = test_func()
            self.assertEqual(res, "success")


if __name__ == "__main__":
    unittest.main()
