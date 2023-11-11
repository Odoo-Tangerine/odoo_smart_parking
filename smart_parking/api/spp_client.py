from typing import Dict, Any
from dataclasses import dataclass
from odoo import models
from odoo.exceptions import UserError
from .spp_connection import SPPConnection


@dataclass
class SPPClient(SPPConnection):
    spp_config: models

    def __post_init__(self):
        self.conn = SPPConnection(self.spp_config)

    def get_token(self, payload: Dict[str, Any]):
        func_name = 'GetToken'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def get_token_long_term(self, payload: Dict[str, Any]):
        func_name = 'GetTokenLongTerm'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def sync_provinces(self):
        func_name = 'SyncProvinces'
        result = self.conn.execute_restful(func_name, 'GET')
        return self._validate_result(func_name, result)

    def sync_districts(self):
        func_name = 'SyncDistricts'
        result = self.conn.execute_restful(func_name, 'GET')
        return self._validate_result(func_name, result)

    def sync_wards(self):
        func_name = 'SyncWards'
        result = self.conn.execute_restful(func_name, 'GET')
        return self._validate_result(func_name, result)

    @staticmethod
    def _validate_result(func_name: str, result):
        if result.get('status') != 200:
            raise UserError(f'Request API {func_name} error. {result.get("status")} - {result.get("message")}')
        return result.get('data', False)