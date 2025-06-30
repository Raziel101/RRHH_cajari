# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re
import logging

_logger = logging.getLogger(__name__)

class Department(models.Model):
    _inherit = ['hr.department']

    # Relaciones
    usuarios_ids        = fields.Many2many('res.users',relation='usuarios_areagob',
                                            column1='areagob_id',
                                            column2='user_id',string="Usuarios del área")