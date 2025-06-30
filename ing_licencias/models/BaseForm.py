# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from odoo.exceptions import Warning
_logger = logging.getLogger(__name__)


class BaseForm(models.Model):
    _name = 'ing.licencias.base'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'
    _order = "create_date desc"
    _description = "BaseForm"

    # Relaciones
    employee_id             = fields.Many2one('hr.employee', string='Empleado', required=True)
    tipo_contrato_id        = fields.Many2one('ing.ausencias.tipo.contrato', string='Tipo de Contrato', required=True, domain=[('name', 'in', ['planta_permanente', 'planta_temporaria'])])
    company_id              = fields.Many2one('res.company',string='Company', required=True, default=lambda self: self.env.user.company_id, readonly=True)

    # Related
    departament_id          = fields.Many2one(related="employee_id.department_id", string="Departamento", store=True, readonly=False, required=True)
    # este campo categoria_ids, lo usaron para cargar categorias, pero me praece q en algun momento se tiene que crear otro,
    categoria_ids           = fields.Many2many(related="employee_id.category_ids", string='Categoria', readonly=False, required=True)
    telefono                = fields.Char(related="employee_id.telefono", store=True, readonly=False, required=True)
    domic_real              = fields.Char(related="employee_id.domic_real", store=True, readonly=False, required=True)
    domic_legal             = fields.Char(related="employee_id.domic_legal", store=True, readonly=False, required=True)
    dni                     = fields.Char(related="employee_id.identification_id", store=True, readonly=False, required=True)
    cuit                    = fields.Char(related="employee_id.cuit", store=True, readonly=False, required=True)
    fecha_nac               = fields.Date(related="employee_id.birthday", store=True, readonly=False, required=True)