# -*- coding: utf-8 -*-
from odoo import fields, models

class IngProcedure(models.Model):
    _name = 'ing.procedure'
    _order = 'sequence'

    sequence = fields.Integer('Secuencia', default=10)
    name = fields.Char('Titulo')
    description = fields.Html('Descripción')
    attach_ids = fields.Many2many('ir.attachment', string='Adjuntos')
    area_id = fields.Many2one('ing.area')


class IngArea(models.Model):
    _name = 'ing.area'

    name = fields.Char('Nombre')
