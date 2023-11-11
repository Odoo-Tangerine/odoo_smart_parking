from odoo import models, fields


class SppVehicleIOHistory(models.Model):
    _name = 'spp.vehicle.io.history'
    _description = 'Spp Vehicle IO History'

    vehicle_id = fields.Many2one('spp.registered.vehicle', string='License plate')
    io_type = fields.Selection([
        ('in', 'In'),
        ('out', 'Out')
    ], string='IO Type')

