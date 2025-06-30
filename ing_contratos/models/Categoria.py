# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Categoria(models.Model):
    _name = 'ing.contratos.categoria'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _description = "Categoria"

    # Atributos
    name            = fields.Char(string=u"Categoria", required=True, tracking=True)

    # SQL Constraints
    _sql_constraints = [
        ('categoria_name_uniq', 'unique(name)', 'La Categoria ingresada ya existe!'),
    ]