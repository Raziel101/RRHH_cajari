# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from datetime import date
from odoo.exceptions import Warning, UserError

_logger = logging.getLogger(__name__)

_READONLYSTATES = {'cancelada': [('readonly', True)]}


class Solicitud(models.Model):
    _name = 'ing.rrhh.solicitudes.solicitud'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'
    _order = "create_date desc"
    _description = "Solicitud"

    # Atributos
    monto = fields.Monetary(string='Monto', required=True, tracking=True, states=_READONLYSTATES)
    revisar = fields.Boolean(string="Revisar", default=False, states=_READONLYSTATES)
    fecha_emision = fields.Date(string='Fecha de Emision', required=True, tracking=True, states=_READONLYSTATES)
    state = fields.Selection([('borrador', 'Borrador'),
                              ('confirmada', 'Confirmada'),
                              ('revisar', 'Por revisar'),
                              ('cancelada', 'Cancelada')], tracking=True,
                             default='borrador', string="Estado", states=_READONLYSTATES)
    descripcion = fields.Text(string='Descripcion')
    total_month_advances = fields.Monetary(string='Total de adelantos del mes', compute='_compute_total_month_advances')
    view_total_month_advances = fields.Boolean(compute='_compute_view_total_month_advances')

    # Relaciones
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True, states=_READONLYSTATES)
    departament_id = fields.Many2one('hr.department', string="Departamento", readonly=True, compute='get_departament', store=True)
    tipo_contrato_id = fields.Many2one('ing.ausencias.tipo.contrato', string='Tipo de Contrato', compute='get_tipo_contrato',store=True,
                                       readonly=True, domain=[
            ('name', 'in', ['planta_permanente', 'planta_temporaria', 'contratado', 'contrato_facturacion'])])

    # Related
    dni = fields.Char(related="employee_id.identification_id", readonly=True)

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('ing_rrhh_solicitudes.group_ing_rrhh_solicitud_admin_rrhh'):
            t_c_id = self.env['hr.employee'].browse(vals.get('employee_id')).tipo_contrato_id.id
            if t_c_id in [self.env.ref('ing_ausencias.planta_permanente').id, self.env.ref('ing_ausencias.planta_temporaria').id]:
                if date.today().month in [6, 12]:
                    raise UserError(u'No puede crear Adelantos en los meses de Junio o Diciembre.')
        return super().create(vals)

    # Funciones
    @api.depends('employee_id', 'monto')
    def _compute_total_month_advances(self):
        day_current = date.today().day
        config_param = self.env['ir.config_parameter']
        day_init = int(config_param.sudo().get_param('day_init'))
        day_end = int(config_param.sudo().get_param('day_end'))
        if day_current < day_init and date.today().month == 1:
            date_init = date(date.today().year-1, 12, day_init)
            date_end = date(date.today().year, 1, day_end)
        elif day_current > day_end and date.today().month == 1:
            date_init = date(date.today().year, 1, day_init)
            date_end = date(date.today().year, 2, day_end)
        elif day_current > day_end and date.today().month == 12:
            date_init = date(date.today().year, 12, day_init)
            date_end = date(date.today().year+1, 1, day_end)
        elif day_current < day_init and date.today().month == 12:
            date_init = date(date.today().year, 11, day_init)
            date_end = date(date.today().year, 12, day_end)
        else:
            if day_current < day_init:
                month_i = date.today().month - 1
                month_e = date.today().month
            elif day_current > day_end:
                month_i = date.today().month
                month_e = date.today().month + 1
            date_init = date(date.today().year, month_i, day_init)
            date_end = date(date.today().year, month_e, day_end)

        for rec in self:
            advances = self.search_read([('employee_id', '=', rec.employee_id.id),
                                        ('fecha_emision', '>=', date_init),
                                        ('fecha_emision', '<=', date_end)], ['monto'])
            rec.sudo().write({'total_month_advances': sum([mon['monto'] for mon in advances])})

    @api.depends('tipo_contrato_id', 'total_month_advances')
    def _compute_view_total_month_advances(self):
        self._compute_total_month_advances()
        config_param = self.env['ir.config_parameter']
        for rec in self:
            if rec.tipo_contrato_id.name in ['planta_permanente', 'planta_temporaria']:
                total_max = config_param.sudo().get_param('amount_planta')
            else:
                total_max = config_param.sudo().get_param('amount_contratados')
            rec.sudo().write({'view_total_month_advances': rec.total_month_advances > float(total_max)})

    @api.onchange('monto')
    def _onchange_monto(self):
        self._compute_view_total_month_advances()

    def a_revisar(self):
        self.write({'revisar': True, 'state': 'revisar'})

    def confirmar(self):
        self.write({'state': 'confirmada', 'revisar': False})

    def cancelar(self):
        self.write({'state': 'cancelada'})

    def volver_borrador(self):
        self.write({'state': 'borrador'})

    def call_wizard_correccion(self):
        """
        :return: Llama al wizard nota de correccion
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'nota.correccion.adelantos.wizard',
            'target': 'new',
            'context': {'default_ing_solicitud_id': self.id},
        }

    @api.depends('employee_id')
    def get_departament(self):
        for rec in self:
            rec.sudo().write({'departament_id': rec.employee_id.department_id.id})

    @api.depends('employee_id')
    def get_tipo_contrato(self):
        for rec in self:
            rec.sudo().write({'tipo_contrato_id': rec.employee_id.tipo_contrato_id.id})