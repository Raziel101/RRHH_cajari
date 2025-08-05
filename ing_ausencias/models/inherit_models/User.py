# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re
import logging

_logger = logging.getLogger(__name__)

class User(models.Model):
    _inherit = ['res.users']

    # Relaciones
    areasgob_ids        = fields.Many2many('hr.department',relation='usuarios_areagob',
                                            column1='user_id',
                                            column2='areagob_id',string=u"Áreas asignadas", tracking=True)