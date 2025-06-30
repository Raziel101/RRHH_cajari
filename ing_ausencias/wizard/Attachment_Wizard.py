# -*- encoding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Attachment_wizard(models.TransientModel):
    _name = 'ausencias.attachment.wizard'

    # Relaciones
    ing_ausencia_id     = fields.Many2one('ing.ausencias.ausencias', string="Ausencia", readonly=True)
    attachment_ids      = fields.Many2many('ir.attachment', 'ausencia_wizard_attachment_rel',
                                           'wizard_id', 'attachment_id', 'Attachments')
    # Funciones
    def attach_file(self):
        self.ing_ausencia_id.sudo().write({'attach_ids': [(4, attach.id, ) for attach in self.attachment_ids],})
