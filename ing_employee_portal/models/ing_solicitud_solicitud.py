# -*- coding: utf-8 -*-
from odoo import models, fields, api
class Solicitud(models.Model):
    _inherit = 'ing.rrhh.solicitudes.solicitud'

    state = fields.Selection(selection_add=[('create_portal', 'Por Autorizar')])
    view_alert_create_portal = fields.Boolean()
    view_request_admin = fields.Boolean(compute='compute_view_request_admin',
        help='Si es True el boton Autorizar solo sera visible para explicitamente administradores de solicitudes y admin de sistema')

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            adv_ids = self.env['ing.rrhh.solicitudes.solicitud'].search([('employee_id', '=', self.employee_id.id),
                                                                         ('state', '=', 'create_portal')])
            self.view_alert_create_portal = bool(adv_ids)

    def compute_view_request_admin(self):
        for rec in self:
            res = self.env.user.has_group('base.group_system') or \
                  self.env.user.has_group('ing_rrhh_solicitudes.group_ing_rrhh_solicitud_admin') and \
                  not self.env.user.has_group('ing_rrhh_solicitudes.group_ing_rrhh_solicitud_admin_rrhh')
            rec.view_request_admin = res

    def action_to_draft(self):
        for rec in self:
            rec.sudo().write({'state': 'borrador'})
