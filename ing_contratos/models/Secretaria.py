# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Secretaria(models.Model):
    _name = 'ing.contratos.secretaria'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _description = "Secretaria"

    # Atributos
    name            = fields.Char(string=u"Secretaria", required=True, tracking=True)

    # Relaciones
    departament_ids = fields.Many2many('hr.department',relation='secretaria_departamento_rel',
                                       column1='secretaria_id',
                                       column2='departamento_id',string="Departamentos",tracking=True)
    # SQL Constraints
    _sql_constraints = [
        ('secretaria_name_uniq', 'unique(name)', 'La Secretaria ingresada ya existe!'),
    ]