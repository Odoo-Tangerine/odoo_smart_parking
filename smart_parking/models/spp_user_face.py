from odoo import fields, models


class SppUserFace(models.Model):
    _name = 'spp.user.face'
    _description = 'Spp User Face'

    user_id = fields.Many2one('res.users', string='User', required=True)
    face_binary = fields.Binary(required=True, string='Face Binary', attachment=False)
    face_encoding = fields.Binary(required=True, string='Face Encoding', attachment=False)
    face_name = fields.Char(required=True, string='Face Name')
