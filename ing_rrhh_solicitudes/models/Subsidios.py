# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from datetime import date

_logger = logging.getLogger(__name__)

_READONLYSTATES = {'confirmed': [('readonly', True)], 'annulled': [('readonly', True)]}


class Subsidy(models.Model):
    _name = 'ing.rrhh.solicitudes.subsidy'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'
    _order = "create_date desc"
    _description = "Subsidio"

    # Atributos
    amount = fields.Monetary(string='Monto', required=True, tracking=True, states=_READONLYSTATES)
    state = fields.Selection([('draft', 'Borrador'),
                              ('salary_management', 'En Gestion de Sueldos'),
                              ('government_management', 'En Gestion de Gobierno'),
                              ('confirmed', 'Confirmado'),
                              ('annulled', 'Anulado')], tracking=True,
                             default='draft', string="Estado", states=_READONLYSTATES)
    description = fields.Text(string='Observaciones')
    num_quot = fields.Integer(u'N° de Cuotas')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    def _get_domain_employee(self):
        fac = self.env.ref('ing_ausencias.facturacion').id
        c_fac = self.env.ref('ing_ausencias.clausula_contrato').id
        cto_fac = self.env.ref('ing_ausencias.contratado_facturacion').id
        p_u = self.env.ref('ing_ausencias.contrato_pago_unico').id
        return [("tipo_contrato_id", "not in", [fac, c_fac, p_u, cto_fac])]

    employee_id = fields.Many2one('hr.employee', string='Empleado', domain=lambda self: self._get_domain_employee(),
                                  required=True, states=_READONLYSTATES)
    address = fields.Char(related='employee_id.domic_legal')
    phone = fields.Char(related='employee_id.telefono')
    department_id = fields.Many2one(related='employee_id.department_id', string='Departamento')
    tipo_contrato_id = fields.Many2one(related='employee_id.tipo_contrato_id')
    dni = fields.Char(related="employee_id.identification_id", readonly=True)
    attach_ids = fields.Many2many('ir.attachment', string='Adjuntos', domain="[('res_id','=',id)]", copy=True)

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_m_salary(self):
        self.write({'state': 'salary_management'})

    def action_m_government(self):
        self.write({'state': 'government_management'})

    def action_confirmed(self):
        self.write({'state': 'confirmed'})

    def action_annulled(self):
        self.write({'state': 'annulled'})

    def view_history_attach(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('ing_rrhh_solicitudes.view_attach_min').id,
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
            'context': {'create': 0, 'edit': 0}
        }

