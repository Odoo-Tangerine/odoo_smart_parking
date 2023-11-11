from odoo import fields, models


class SppRegisteredService(models.Model):
    _name = 'spp.registered.vehicle'
    _description = 'Registered Vehicle'
    _rec_name = 'license_plate'
    _inherit = ['mail.thread']

    product_id = fields.Many2one('product.template', required=True, string='Product')
    product_duration = fields.Integer(related='product_id.duration', string='Duration')
    product_slot = fields.Integer(related='product_id.slot', string='Slot')
    invoice_id = fields.Many2one('account.move', required=True, string='Invoice')
    user_id = fields.Many2one('res.users', string='User', required=True)
    license_plate = fields.Char(string='License plate', required=True)
    expire_date = fields.Datetime(string='Expire Date')
    state = fields.Selection([
        ('waiting_for_payment', 'Waiting for Payment'),
        ('expired', 'Expired'),
        ('inuse', 'In Use'),
        ('almost_expired', 'Almost Expired')
    ], default='waiting_for_payment', tracking=True)
    active = fields.Boolean(default=True)
    is_in_parking_lot = fields.Boolean(default=False, string='In parking lot', tracking=True)

