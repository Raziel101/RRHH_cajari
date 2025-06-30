# -*- encoding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Attachment_wizard(models.TransientModel):
    _name = 'attachment.licencia.wizard'

    # Relaciones
    ing_form_general_id     = fields.Many2one('ing.licencias.general', string="Licencias", readonly=True)
    attachment_ids          = fields.Many2many('ir.attachment', 'wizard_attachment_licencias_rel',
                                               'wizard_lic_id', 'attachment_lic_id', 'Attachments')
    # Funciones
    def attach_file(self):
        self.ing_form_general_id.sudo().write({'attach_ids': [(4, attach.id, ) for attach in self.attachment_ids],})

class Att_vacaciones_wizard(models.TransientModel):
    _name = 'attachment.vacaciones.wizard'

    # Relaciones
    ing_vacaciones_id       = fields.Many2one('ing.alta.baja.licencia', string="Vacaciones", readonly=True)
    attachment_ids          = fields.Many2many('ir.attachment', 'attachment_vacaciones_rel',
                                               'wizard_vac_id', 'attachment_vac_id', 'Attachments')
    # Funciones
    def attach_file(self):
        self.ing_vacaciones_id.sudo().write({'attach_ids': [(4, attach.id, ) for attach in self.attachment_ids],})
