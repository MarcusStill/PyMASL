import logging
import os
from configparser import (
    ConfigParser,
    NoSectionError,
    NoOptionError,
    MissingSectionHeaderError,
)

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        """Функция для загрузки параметров из файла конфигурации.

        Параметры:
            None

        Возвращаемое значение:
            dict: Словарь с параметрами конфигурации, содержащий следующие ключи:
                - host (str): Хост базы данных.
                - port (str): Порт базы данных.
                - database (str): Имя базы данных.
                - user (str): Имя пользователя базы данных.
                - version (str): Версия программного обеспечения.
                - log_file (str): Путь к файлу журнала.
                - kol (str): Количество ПК.
                - pc_1 (str): Имя первого ПК.
                - pc_2 (str): Имя второго ПК.
                - pinpad_path (str): Путь к терминалу.
        """
        config = ConfigParser()
        try:
            if not os.path.exists(self.config_file):
                raise FileNotFoundError(
                    f"Файл конфигурации {self.config_file} не найден."
                )
            config.read(self.config_file)
            required_keys = {
                "host": "DATABASE",
                "port": "DATABASE",
                "database": "DATABASE",
                "user": "DATABASE",
                "version": "OTHER",
                "log_file": "OTHER",
                "kol": "PC",
                "pc_1": "PC",
                "pc_2": "PC",
                "pinpad_path": "TERMINAL",
                "ticket_coordinates_file": "OTHER",
            }
            config_data = {}
            for key, section in required_keys.items():
                if not config.has_section(section):
                    raise ValueError(
                        f"Отсутствует секция: '{section}' в конфигурационном файле."
                    )
                if not config.has_option(section, key):
                    raise ValueError(
                        f"Отсутствует параметр '{key}' в секции '{section}'"
                    )
                config_data[key] = config.get(section, key)
            return config_data
        except (NoSectionError, NoOptionError) as e:
            logger.error(f"Ошибка в конфигурационном файле: {e}")
            raise ValueError(f"Ошибка в файле конфигурации: {e}")
        except MissingSectionHeaderError:
            logger.error("Отсутствует заголовок секции в конфигурационном файле.")
            raise ValueError(
                "Ошибка: отсутствует заголовок секции в файле конфигурации."
            )
        except Exception as e:
            logger.error(f"Неизвестная ошибка при чтении файла конфигурации: {e}")
            raise RuntimeError(f"Неизвестная ошибка: {e}")

    def get(self, key: str):
        return self.config_data.get(key)
