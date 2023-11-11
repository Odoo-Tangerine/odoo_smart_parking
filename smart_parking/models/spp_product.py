from odoo import models, fields


class SppProduct(models.Model):
    _inherit = 'product.template'

    duration = fields.Integer(default=1, string='Duration')
    slot = fields.Integer(default=1, string='Slot')
