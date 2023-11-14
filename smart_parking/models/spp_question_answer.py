from odoo import models, fields, api, _


class SppQuestionAndAnswer(models.Model):
    _name = 'spp.question.answer'
    _description = 'Spp Question Answer'
    _rec_name = 'question'

    question = fields.Char(string='Question', required=True)
    answer = fields.Char(string='Answer', required=True)
