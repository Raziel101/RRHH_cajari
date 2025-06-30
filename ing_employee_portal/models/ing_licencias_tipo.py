# -*- coding: utf-8 -*-
from odoo import fields, models


class Tipo(models.Model):
    _inherit = 'ing.licencias.tipo'

    view_in_portal = fields.Boolean('¿Visible en el portal?', default=True, help='''Le va permitir al usuario poder 
    gestionar este tipo de licencia desde el portal.''')
