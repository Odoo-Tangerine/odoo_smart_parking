from odoo import models, fields


class SppVehicleIOHistory(models.Model):
    _name = 'spp.vehicle.io.history'
    _description = 'Spp Vehicle IO History'

    user_id = fields.Many2one('res.users', string='User', required=True, readonly=True)
    license_plate = fields.Char(string='License Plate', required=True, readonly=True)
    io_type = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')
    ], string='IO Type', required=True, readonly=True)
    io_datetime = fields.Datetime(string='IO Datetime', default=fields.Datetime.now, readonly=True)
    driver = fields.Char(string='Driver', readonly=True)
    # device_id = fields.Many2one('spp.device', string='Device', readonly=True)


