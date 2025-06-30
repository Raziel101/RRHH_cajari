# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class nota_correccion_wizard(models.TransientModel):
    _name = 'nota.correccion.adelantos.wizard'

    # Atributos
    correccion          = fields.Text(string="Comentario de Correccion")

    # Relaciones
    ing_solicitud_id    = fields.Many2one('ing.rrhh.solicitudes.solicitud', readonly=True, string="Solicitud")

    # Funciones
    def crear_nota_correccion(self):
        list = []

        list.append((0, 0, {'model': 'ing.rrhh.solicitudes.solicitud',
                            'subject': 'Public Discussion',
                            'author_id': self.env.user.partner_id.id,
                            'message_type': 'comment',
                            'body': self.correccion,
                            'res_id': self.ing_solicitud_id.id,
                            }))

        self.ing_solicitud_id.sudo().write({'message_ids': list,
                                           'revisar':True,
                                           'state':'revisar'})