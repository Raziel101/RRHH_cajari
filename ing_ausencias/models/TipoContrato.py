# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class TipoContrato(models.Model):
    _name = 'ing.ausencias.tipo.contrato'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _rec_name = 'detalle'
    _description = "TipoContrato"
    
    #Sql Constraint
    _sql_constraints = [
        ("tipo_contrato_unique_name",
         "UNIQUE(name)",
         "El tipo de contrato ingresado ya existe."),
    ]

    # Atributos
    name                    = fields.Char(string=u"Tipo de contrato", required=True, tracking=True)
    # el campo detalle se lo agrego para detallar bien el tipo del nombre de contrato
    # ya que en el name tuve q agregar el nombre del campo select, por elemplo, planta permanente: panta_permanente
    detalle                 = fields.Char(string=u"Detalle", tracking=True)
    texto_contrato          = fields.Html(string=u"Texto del Contrato")