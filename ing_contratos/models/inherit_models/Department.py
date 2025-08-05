# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re
import logging

_logger = logging.getLogger(__name__)

class Department(models.Model):
    _inherit = ['hr.department']

    # Relaciones
    secretaria_ids  = fields.Many2many('ing.contratos.secretaria', relation='secretaria_departamento_rel',
                                      column1='departamento_id',
                                      column2='secretaria_id', string="Secretaria", tracking=True)