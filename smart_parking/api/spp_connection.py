import requests
from dataclasses import dataclass
from typing import Dict, Any, NoReturn
from odoo import models, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import ustr

API_ROUTES = {
    'GetToken': '/v2/user/Login',
    'GetTokenLongTerm': '/v2/user/ownerconnect',
    'SyncProvinces': '/v2/categories/listProvinceById?provinceId=-1',
    'SyncDistricts': '/v2/categories/listDistrict?provinceId=-1',
    'SyncWards': '/v2/categories/listWards?districtId=-1'
}


@dataclass
class SPPConnection:
    spp_config: models

    @staticmethod
    def _build_header(func_name: str, token: str) -> Dict[str, Any]:
        header = {'Content-Type': 'application/json'}
        if func_name != 'GetToken':
            header.update({'Token': token})
        return header

    @staticmethod
    def _validate_func_name(func_name: str) -> NoReturn:
        if func_name not in API_ROUTES:
            raise UserError(_(f'The routes {func_name} not found.'))

    def execute_restful(self, func_name, method, *args, **kwargs):
        self._validate_func_name(func_name)
        try:
            header = self._build_header(func_name, self.spp_config.token)
            endpoint = self.spp_config.host + API_ROUTES[func_name].format(*args)
            if method == 'POST':
                response = requests.post(endpoint, json=kwargs, headers=header, timeout=300)
            elif method == 'GET':
                response = requests.get(endpoint, headers=header, timeout=300)
            else:
                raise UserError(_('The method invalid'))
            response.raise_for_status()
            result = response.json()
            if response.status_code != 200:
                raise UserError(_(f'Request Name {func_name} error.'))
            return result
        except Exception as e:
            raise UserError(ustr(e))
