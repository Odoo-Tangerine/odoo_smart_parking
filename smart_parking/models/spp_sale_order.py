from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    duration = fields.Integer(string='Duration')
    slot = fields.Integer(string='Slot')
