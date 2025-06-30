# -*- encoding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class Attachment_wizard(models.TransientModel):
    _name = 'attachment.wizard'

    # Relaciones
    ing_contrato_id     = fields.Many2one('ing.contratos.contratos', string="Contrato", readonly=True)
    attachment_ids      = fields.Many2many('ir.attachment', 'wizard_attachment_rel',
                                           'wizard_id', 'attachment_id', 'Attachments')
    # Funciones
    def attach_file(self):
        self.ing_contrato_id.sudo().write({'attach_ids': [(4, attach.id, ) for attach in self.attachment_ids],})
