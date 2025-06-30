# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from odoo.exceptions import Warning
_logger = logging.getLogger(__name__)


class Tipo(models.Model):
    _name = 'ing.licencias.tipo'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _rec_name = 'detalle'
    _description = "Tipo"

    # Sql Constraint
    _sql_constraints = [
        ("tipo_lic_unique_name",
         "UNIQUE(name)",
         "El tipo ingresado ya existe."),
    ]

    # Atributos
    name                    = fields.Char(string=u"Nombre Interno", required=True, tracking=True)
    detalle                 = fields.Char(string=u"Detalle", required=True, tracking=True)
    dias_permitidos_año     = fields.Integer(string=u"Dias permitidos por año")
    dias_permitidos_mes     = fields.Integer(string=u"Dias permitidos por mes")

    active                  = fields.Boolean(string='Activo', default=True)
