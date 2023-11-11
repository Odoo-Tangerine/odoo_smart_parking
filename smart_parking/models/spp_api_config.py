import concurrent.futures
from typing import Dict, Any
from odoo import fields, models
from ..common.func import Func


class SPPAPIConfig(models.Model):
    _name = 'spp.api.config'
    _description = 'SPP API Config'

    name = fields.Char(string='Name', required=True)
    username = fields.Char(string='Username', required=True)
    password = fields.Char(string='Password', required=True)
    host = fields.Char(string='Host', required=True)
    token = fields.Char(string='Token', readonly=True)

    def _build_payload_get_token(self) -> Dict[str, Any]:
        payload = {
            'USERNAME': self.username,
            'PASSWORD': self.password
        }
        return payload

    def spp_get_token(self):
        payload = self._build_payload_get_token()
        client = Func.get_api_client_spp(self)
        data = client.get_token(payload)
        self.token = data.get('token')
        data = client.get_token_long_term(payload)
        self.token = data.get('token')
