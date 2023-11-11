from odoo import _
from odoo.exceptions import UserError
from ..api.spp_client import SPPClient


class Func:
    @staticmethod
    def get_api_client_spp(self) -> SPPClient:
        spp_config = self.env.ref('smart_parking.spp_api_config_for_viettelpost')
        if not spp_config:
            raise UserError(_('The spp config does not exist.'))
        client = SPPClient(spp_config)
        return client