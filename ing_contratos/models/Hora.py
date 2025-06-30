# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Hora(models.Model):
    _name = 'ing.contratos.hora'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _description = "Hora"

    # Atributos
    name                = fields.Selection([('lunes','Lunes'),
                                            ('martes','Martes'),
                                            ('miercoles','Miercoles'),
                                            ('jueves','Jueves'),
                                            ('viernes','Viernes'),
                                            ('sabado','Sabado'),
                                            ('domingo','Domingo'),
                                            ], string="Dia", required=True)
    hora_inicio         = fields.Float(string="Hora de Inicio", required=True)
    hora_fin            = fields.Float(string="Hora de Fin", required=True)

    # Relaciones
    ing_contrato_id     = fields.Many2one('ing.contratos.contratos', string="Contrato")