import unittest
import os
import tempfile
from modules.config import Config

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "config.ini")

        # Valid config content
        self.valid_config_content = """
[DATABASE]
host = 127.0.0.1
port = 5432
database = mydb
user = myuser

[OTHER]
version = 1.0.0
log_file = app.log
ticket_coordinates_file = coords.json

[PC]
kol = 2
pc_1 = Workstation-1
pc_2 = Workstation-2

[TERMINAL]
pinpad_path = /opt/pinpad

[PRINT]
ticket = on

[KKT]
available = on
"""
        with open(self.config_path, "w") as f:
            f.write(self.valid_config_content)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_valid_config(self):
        config = Config(config_file=self.config_path)

        self.assertEqual(config.get("host"), "127.0.0.1")
        self.assertEqual(config.get("kol"), "2")
        self.assertEqual(config.get("pc_1"), "Workstation-1")
        self.assertEqual(config.get("ticket"), "on")

        self.assertEqual(len(config.pcs), 2)
        self.assertEqual(config.pcs[0], "Workstation-1")
        self.assertEqual(config.pcs[1], "Workstation-2")

    def test_missing_config_file(self):
        with self.assertRaises(RuntimeError) as context:
            Config(config_file="non_existent_file.ini")
        self.assertIn("Неизвестная ошибка", str(context.exception))

    def test_missing_required_section(self):
        invalid_content = """
[DATABASE]
host = 127.0.0.1
port = 5432
database = mydb
user = myuser

[OTHER]
version = 1.0.0
log_file = app.log
ticket_coordinates_file = coords.json

[PC]
kol = 1
pc_1 = PC-1

[TERMINAL]
pinpad_path = /opt/pinpad

# Missing [PRINT] and [KKT]
"""
        with open(self.config_path, "w") as f:
            f.write(invalid_content)

        with self.assertRaises(RuntimeError) as context:
            Config(config_file=self.config_path)
        self.assertIn("Неизвестная ошибка: Отсутствует секция:", str(context.exception))

    def test_missing_pc_option(self):
        invalid_content = """
[DATABASE]
host = 127.0.0.1
port = 5432
database = mydb
user = myuser

[OTHER]
version = 1.0.0
log_file = app.log
ticket_coordinates_file = coords.json

[PC]
kol = 2
pc_1 = Workstation-1
# Missing pc_2

[TERMINAL]
pinpad_path = /opt/pinpad

[PRINT]
ticket = on

[KKT]
available = on
"""
        with open(self.config_path, "w") as f:
            f.write(invalid_content)

        with self.assertRaises(RuntimeError) as context:
            Config(config_file=self.config_path)
        self.assertIn("Неизвестная ошибка: Отсутствует параметр 'pc_2'", str(context.exception))

    def test_empty_pc_name(self):
        invalid_content = """
[DATABASE]
host = 127.0.0.1
port = 5432
database = mydb
user = myuser

[OTHER]
version = 1.0.0
log_file = app.log
ticket_coordinates_file = coords.json

[PC]
kol = 1
pc_1 =

[TERMINAL]
pinpad_path = /opt/pinpad

[PRINT]
ticket = on

[KKT]
available = on
"""
        with open(self.config_path, "w") as f:
            f.write(invalid_content)

        with self.assertRaises(RuntimeError) as context:
            Config(config_file=self.config_path)
        self.assertIn("Неизвестная ошибка: Пустое значение", str(context.exception))

if __name__ == '__main__':
    unittest.main()

    def test_missing_pc_name_empty(self):
        # Additional edge cases from original term-missing
        invalid_content = """
[DATABASE]
host = 127.0.0.1
port = 5432
database = mydb
user = myuser

[OTHER]
version = 1.0.0
log_file = app.log
ticket_coordinates_file = coords.json

[PC]
kol = 1
pc_1 =

[TERMINAL]
pinpad_path = /opt/pinpad

[PRINT]
ticket = on

[KKT]
available = on
"""
        with open(self.config_path, "w") as f:
            f.write(invalid_content)

        with self.assertRaises(RuntimeError):
            Config(config_file=self.config_path)

    def test_missing_section_header(self):
        invalid_content = "this is not a valid ini file"
        with open(self.config_path, "w") as f:
            f.write(invalid_content)

        with self.assertRaises(RuntimeError):
            Config(config_file=self.config_path)

