import logging
import os
from configparser import (
    ConfigParser,
    NoSectionError,
    NoOptionError,
    MissingSectionHeaderError,
)
from typing import List, Optional

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config_data = self.load_config()
        # Инициализируем список ПК
        self.pcs = self._get_pc_list()

    def _get_pc_list(self) -> List[str]:
        """Возвращает список имен ПК из конфигурации"""
        pc_count = int(self.get("kol"))
        pc_list = []
        for i in range(pc_count):
            pc_key = f"pc_{i+1}"
            pc_name = self.get(pc_key)
            if not pc_name:
                logger.error(f"Пустое имя для {pc_key} в конфиге")
                raise ValueError(f"Пустое имя для {pc_key} в конфиге")
            pc_list.append(pc_name.strip())
        return pc_list

    def load_config(self):
        """Загружает и валидирует параметры конфигурации из INI-файла.

        Чтение и проверка:
        1. Проверяет наличие файла конфигурации
        2. Валидирует обязательные секции и параметры
        3. Проверяет существование файла с координатами билетов
        4. Динамически загружает список рабочих станций (ПК)

        Обязательные параметры:
            [DATABASE]
            host (str): IP-адрес или хост базы данных
            port (str): Порт подключения к БД
            database (str): Имя базы данных
            user (str): Имя пользователя БД

            [OTHER]
            version (str): Версия программного обеспечения
            log_file (str): Путь к файлу журнала (лог-файлу)
            ticket_coordinates_file (str): Путь к JSON-файлу с координатами билета

            [PC]
            kol (str): Количество рабочих станций (должно быть >= 1)
            pc_1..pc_N (str): Имена рабочих станций (N = kol)

            [TERMINAL]
            pinpad_path (str): Путь к ПО платежного терминала

            [PRINT]
            ticket (str): Флаг печати билетов (on/off)

            [KKT]
            available (str): Флаг наличия ККТ (on/off)

        Возвращает:
            dict: Словарь с загруженными параметрами конфигурации, где:
                - ключи соответствуют именам параметров
                - значения - строковые значения параметров

        Исключения:
            FileNotFoundError: Если отсутствует файл конфигурации или файл координат
            ValueError: Если отсутствуют обязательные параметры или секции
            RuntimeError: При других ошибках чтения/парсинга конфига

        """
        logger.info("Запуск функции load_config")
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
                "ticket_coordinates_file": "OTHER",
                "kol": "PC",
                "pinpad_path": "TERMINAL",
                "available": "KKT",
                "ticket": "PRINT",
            }

            config_data = {}
            pc_count = int(config.get("PC", "kol"))
            for i in range(pc_count):
                pc_key = f"pc_{i+1}"
                if not config.has_option("PC", pc_key):
                    raise ValueError(f"Отсутствует параметр '{pc_key}' в секции 'PC'")

                pc_name = config.get("PC", pc_key)
                if not pc_name.strip():  # Проверяем, что имя не пустое
                    raise ValueError(f"Пустое значение для '{pc_key}' в секции 'PC'")

                config_data[pc_key] = pc_name

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

    def get(self, key: str) -> Optional[str]:
        value = self.config_data.get(key)
        return value
