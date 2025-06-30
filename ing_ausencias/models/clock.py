# -*- coding: utf-8 -*-
from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)

class Clock(models.Model):
    _name       = 'ing.clock'

    name        = fields.Char('Nombre')