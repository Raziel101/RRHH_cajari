# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from odoo.exceptions import Warning
_logger = logging.getLogger(__name__)


class Periodo(models.Model):
    _name = 'ing.licencias.periodo'
    _inherit = 'mail.thread'
    _order = "name asc"
    _description = "Periodo"

    # Sql Constraint
    _sql_constraints = [
        ("periodo_lic_unique_name",
         "UNIQUE(name)",
         "El Periodo ingresado ya existe."),
    ]

    # Atributos
    name            = fields.Char(string=u"Nombre Interno", required=True, size=4, tracking=True)