# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re
import logging

_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = ['ir.attachment']

    # Relaciones
    wizard_ids  = fields.Many2many('attachment.wizard', 'wizard_attachment_rel',
                                   'attachment_id', 'wizard_id', 'Wizard')