# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class nota_correccion_wizard(models.TransientModel):
    _name = 'nota.correccion.licencia.wizard'

    # Atributos
    correccion = fields.Text(string="Comentario de Correccion")

    # Relaciones
    ing_form_general_id = fields.Many2one('ing.licencias.general', readonly=True, string="Licencias")

    # Funciones
    def crear_nota_correccion(self):
        list = []

        list.append((0, 0, {'model': 'ing.licencias.general',
                            'subject': 'Public Discussion',
                            'author_id': self.env.user.partner_id.id,
                            'message_type': 'comment',
                            'body': self.correccion,
                            'res_id': self.ing_form_general_id.id,
                            }))

        self.ing_form_general_id.sudo().write({'message_ids': list,
                                               'revisar': True,
                                               'state': 'revisar'})



class NotaCorreccionWZHorasSev(models.TransientModel):
    _name = 'nota.correccion.horas.sev.wizard'

    hours_sev_id = fields.Many2one('ing.hours.sev', readonly=True)
    correccion = fields.Text(string="Comentario de Correccion")

    # Funciones
    def crear_nota_correccion(self):
        self.hours_sev_id.sudo().write({
            'state': 'to_review',
            'correction': self.correccion,
        })




class nota_correccion_vac_wizard(models.TransientModel):
    _name = 'nota.correccion.vacaciones.wizard'

    # Atributos
    correccion = fields.Text(string="Comentario de Correccion")

    # Relaciones
    ing_vacaciones_id = fields.Many2one('ing.alta.baja.licencia', readonly=True, string="Vacaciones")

    # Funciones
    def crear_nota_correccion(self):
        list = []

        list.append((0, 0, {'model': 'ing.alta.baja.licencia',
                            'subject': 'Public Discussion',
                            'author_id': self.env.user.partner_id.id,
                            'message_type': 'comment',
                            'body': self.correccion,
                            'res_id': self.ing_vacaciones_id.id,
                            }))

        self.ing_vacaciones_id.sudo().write({'message_ids': list,
                                             'state': 'revisar'})
