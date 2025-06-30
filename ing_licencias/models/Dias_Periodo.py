# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class Dias_Periodo(models.Model):
    _name = 'ing.licencias.dia.periodo'
    _inherit = 'mail.thread'
    _rec_name = 'dias'
    _description = "Dias_Periodo"

    # Atributos
    dias = fields.Integer(string=u"Dias")

    # Relaciones
    ing_form_general_id = fields.Many2one('ing.licencias.general', string='Form General')
    periodo_lic_id = fields.Many2one('ing.licencias.periodo', string='Periodo')
    periodo_lic_name = fields.Char(related='periodo_lic_id.name')