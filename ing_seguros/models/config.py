# -*- encoding: utf-8 -*-

from odoo import models, fields


class Config(models.Model):
    _name           = 'ing.seguros.config'

    name            = fields.Char('Correo receptor')