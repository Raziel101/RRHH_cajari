# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re
import logging

_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = ['hr.employee']

    _sql_constraints = [
        ('identification_uniq', 'UNIQUE (identification_id)', 'Ya existe un empleado con este dni.')
    ]

    # Atributos
    domic_real          = fields.Char(string=u"Domicilio Real", required=True, tracking=True)
    domic_legal         = fields.Char(string=u"Domicilio Legal", required=True, tracking=True)
    cuit                = fields.Char(string=u"Cuit", required=True, tracking=True)
    telefono            = fields.Char(string=u"Telefono", required=True, tracking=True)
    clock_one           = fields.Many2one('ing.clock', string='Reloj N°1', tracking=True)
    clock_two           = fields.Many2one('ing.clock', string='Reloj N°2', tracking=True)
    clock_three         = fields.Many2one('ing.clock', string='Reloj N°3', tracking=True)

    # Relaciones
    attach_ids          = fields.Many2many('ir.attachment', string='Adjuntos', domain="[('res_id','=',id)]")
    ing_ausencias_ids   = fields.One2many('ing.ausencias.ausencias', 'employee_id', string='Ausencias')

    # Funciones
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('identification_id', operator, name)]
        return self._search(domain + args, limit= limit, access_rights_uid=name_get_uid)

    def get_ausencias(self):
        ausencias = self.env['ing.ausencias.ausencias'].get_ausencias_employee(self.id)
        tree_view = self.env.ref('ing_ausencias.view_ausencia_tree')
        form_view = self.env.ref('ing_ausencias.view_ausencia_form')
        return {
            'name': 'Ausencias',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'ing.ausencias.ausencias',
            'domain': [('id', 'in', ausencias.ids)],
            'views': [

                (tree_view.id, 'tree'),
                (form_view.id, 'form'),
            ],
            'type': 'ir.actions.act_window',
        }

    def name_get(self):
        res = []
        for record in self:
            name = str(record.name) + '-' + str(record.identification_id)
            res.append((record.id, name))
        return res

    def print_credential(self):
        return {
            'name': 'Seleccione los campos deseados',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ing.credential.custom.wz',
            'views': [(self.env.ref('ing_ausencias.ing_credential_custom_wz_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
            }
        }