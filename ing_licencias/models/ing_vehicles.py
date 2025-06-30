# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re
from datetime import timedelta
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class IngVehicle(models.Model):
    _name = 'ing.vehicle'

    name = fields.Char('Nombre', required=True)
    patent = fields.Char('Patente', required=True)
    department_id = fields.Many2one(comodel_name='hr.department', string='Departamento')


class IngTypeLic(models.Model):
    _name = 'ing.type.lic'

    name = fields.Char('Clase de Licencia de Conducir', required=True)
    desc = fields.Text('Descripción')