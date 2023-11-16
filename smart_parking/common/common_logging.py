import os
import logging
from dataclasses import dataclass


@dataclass
class Logging:
    filename: str
    exec_name: str

    def get_logger(self):
        _logger = logging.getLogger(self.exec_name)
        path_logs = os.path.abspath(f'odoo_smart_parking/smart_parking/logs/{self.filename}.log')
        _logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(path_logs, 'w', 'utf-8')
        file_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
        file_handler.setFormatter(file_formatter)
        _logger.addHandler(file_handler)
        return _logger
