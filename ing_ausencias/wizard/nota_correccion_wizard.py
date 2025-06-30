# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class nota_correccion_wizard(models.TransientModel):
    _name = 'ausencias.nota.correccion.wizard'

    # Atributos
    correccion          = fields.Text(string="Comentario de Correccion")

    # Relaciones
    ing_ausencia_id     = fields.Many2one('ing.ausencias.ausencias', string="Ausencia", readonly=True)

    # Funciones
    def crear_nota_correccion(self):
        list = []

        list.append((0, 0, {'model': 'ing.ausencias.ausencias',
                            'subject': 'Public Discussion',
                            'author_id': self.env.user.partner_id.id,
                            'message_type': 'comment',
                            'body': self.correccion,
                            'res_id': self.ing_ausencia_id.id,
                            }))

        self.ing_ausencia_id.sudo().write({'message_ids': list,
                                           'revisar':True,
                                           'state':'revisar'})