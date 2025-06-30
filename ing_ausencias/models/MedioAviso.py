# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class MedioAviso(models.Model):
    _name = 'ing.ausencias.medio.aviso'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _description = "MedioAviso"
    
    #Sql Constraint
    _sql_constraints = [
        ("medio_aviso_unique_name",
         "UNIQUE(name)",
         "El medio ingresado ya existe."),
    ]

    # Atributos
    name                    = fields.Char(string=u"Medio", required=True, tracking=True)

    # Relaciones
    ing_ausencias_ids       = fields.One2many('ing.ausencias.ausencias', 'ing_medio_aviso_id', string='Ausencias')