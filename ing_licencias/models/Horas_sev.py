# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime, date
from odoo.exceptions import UserError


class SettlementPeriods(models.Model):
    _name           = 'ing.settlement.periods'

    name            = fields.Char('Nombre', required=True)
    date_init       = fields.Date('Fecha de Inicio', required=True)
    date_end        = fields.Date('Fecha de Fin', required=True)

    def reformat_date(self, date):
        return f'{date[8:]}/{date[5:7]}/{date[:4]}'

    @api.model
    def create(self, vals):
        vals['name'] = vals.get('name') + '(' + self.reformat_date(vals.get('date_init')) + ' - ' + self.reformat_date(vals.get('date_end')) + ')'
        return super().create(vals)

    def get_period_current(self):
        return self.search([('date_init', '<=', date.today()), ('date_end', '>=', date.today())], limit=1)

class HorasSev(models.Model):
    _name   = 'ing.hours.sev'
    _order  = 'create_date desc'
    _inherit = 'mail.thread'

    def _get_domain_employee(self):
        p_perm = self.env.ref('ing_ausencias.planta_permanente').id
        p_temp = self.env.ref('ing_ausencias.planta_temporaria').id
        return [('tipo_contrato_id', 'in', [p_temp, p_perm])]

    employee_id     = fields.Many2one('hr.employee', string='Empleado', required=True, domain=_get_domain_employee,
                                      tracking=True)
    hours           = fields.Float('Horas', digits=(3, 1), required=True, tracking=True)
    department_id   = fields.Many2one('hr.department', related='employee_id.department_id', string='Departamento')
    tipo_contrato_id= fields.Many2one('ing.ausencias.tipo.contrato', related='employee_id.tipo_contrato_id',
                                      string='Tipo de Contrato')
    state           = fields.Selection([('draft', 'Borrador'), ('confirmed', 'Confirmada'), ('to_review', 'A revisar')],
                                       string='Estado', default='draft', tracking=True)
    correction      = fields.Text('Corrección', tracking=True)

    def _default_settlement_period(self):
        rec = self.env['ing.settlement.periods'].get_period_current()
        return rec.id if rec else False

    settlement_period_id = fields.Many2one('ing.settlement.periods', 'Período de liquidación', readonly=True,
                                           default=_default_settlement_period, tracking=True)

    def set_periods(self):
        period = self.env['ing.settlement.periods']
        for rec in self.search([]):
            p = period.search([('date_init', '<=', rec.create_date), ('date_end', '>=', rec.create_date)], limit=1)
            rec.settlement_period_id = p.id

    def check_cant_employee(self, docs):
        list_emp = []
        for rec in docs:
            if rec.employee_id.id not in list_emp:
                list_emp.append(rec.employee_id.id)
        return len(list_emp) > 1

    def correction_wz(self):
        return {
            'name': 'Agregar Corrección',
            'res_model': 'nota.correccion.horas.sev.wizard',
            'target': 'new',
            'context': {
                'default_hours_sev_id': self.id,
            },
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(self.env.ref('ing_licencias.correccion_horas_sev_wizard_form_view').id, 'form')],
            'type': 'ir.actions.act_window',
        }

    def change_confirmed(self):
        self.state = 'confirmed'

    def change_to_review(self):
        self.state = 'to_review'

    def change_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        if (vals.get('hours') % 0.5) != 0.0:
            raise UserError('Solo puede ingresar horas enteras o equivalentes a media hora.')
        hours_sev = self.search([('employee_id', '=', vals.get('employee_id')), ('state', '=', 'confirmed')])
        sum_hours = sum([h.hours for h in hours_sev])
        if sum_hours + vals.get('hours') > 120:
            raise UserError(f'El maximo de horas reservadas es 120, tiene reservadas {sum_hours} y esta intentando guardar {vals.get("hours")} mas.')
        return super().create(vals)
