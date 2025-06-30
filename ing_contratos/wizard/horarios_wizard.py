# -*- encoding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class horarios_wizard(models.TransientModel):
    _name = 'horarios.contratos.wizard'

    # Atributos
    hora_inicio         = fields.Float('Hora Inicio', required=True)
    hora_fin            = fields.Float('Hora Fin', required=True)
    lunes               = fields.Boolean(string='Lunes', default=True)
    martes              = fields.Boolean(string='Martes', default=True)
    miercoles           = fields.Boolean(string='Miercoles', default=True)
    jueves              = fields.Boolean(string='Jueves', default=True)
    viernes             = fields.Boolean(string='Viernes', default=True)
    sabado              = fields.Boolean(string='Sabado', default=True)
    domingo             = fields.Boolean(string='Domingo', default=True)

    # Relaciones
    ing_contrato_id     = fields.Many2one('ing.contratos.contratos', readonly=True, string="Contrato")

    # Funciones
    def check_dias(self):
        list=[]
        if self.lunes:
            list.append("lunes")
        if self.martes:
            list.append("martes")
        if self.miercoles:
            list.append("miercoles")
        if self.jueves:
            list.append("jueves")
        if self.viernes:
            list.append("viernes")
        if self.sabado:
            list.append("sabado")
        if self.domingo:
            list.append("domingo")
        return list

    def generar_horarios(self):
        env_contrato    = self.env['ing.contratos.contratos']
        contrato        = env_contrato.search([('id', '=', self.ing_contrato_id.id)],)
        ch_dia          = self.check_dias()
        for dias in ch_dia:
            self.env['ing.contratos.hora'].create({'ing_contrato_id': contrato.id,
                                                   'name': dias,
                                                   'hora_inicio': self.hora_inicio,
                                                   'hora_fin': self.hora_fin,
                                                   })