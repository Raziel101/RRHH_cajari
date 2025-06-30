# -*- coding: utf-8 -*-
from odoo import fields, models, api

class Employee(models.Model):
    _inherit = ['hr.employee']

    secure = fields.Selection([('SI','Seguro en Vigencia'), ('NO','Seguro dado de Baja'), ('GA','En gestion Alta de seguro'),
                               ('GB','En gestion Baja de seguro')], string='Seguro', tracking=True)

    view_secure_field = fields.Boolean(compute="_compute_view_secure_field", store=False)
    required_country_of_birth = fields.Boolean(compute='_required_country_of_birth', store=False)

    @api.depends('tipo_contrato_id')
    def _required_country_of_birth(self):
        p_perm = self.env.ref('ing_ausencias.planta_permanente').id
        p_temp = self.env.ref('ing_ausencias.planta_temporaria').id
        for e in self:
            e.required_country_of_birth = self.tipo_contrato_id.id in [p_perm, p_temp]

    def _compute_view_secure_field(self):
        tipo_contrato = self.env.ref('ing_ausencias.locacion_servicios').id
        for e in self:
            e.view_secure_field = e.tipo_contrato_id.id == tipo_contrato

    def get_historic_art(self):
        planillas = self.env['ing.seguros.planilla.art'].search([('employee_id.id', '=', self.id)])
        tree_view = self.env.ref('ing_seguros.view_ing_secure_tree_planilla_art').id
        form_view = self.env.ref('ing_seguros.view_ing_secure_form_planilla_art').id
        return {
            'name': 'ART',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'ing.seguros.planilla.art',
            'domain': [('id', 'in', planillas.ids), ('employee_id.department_id', 'in', self.env.user.areasgob_ids.ids)],
            'views': [
                (tree_view, 'tree'),
                (form_view, 'form'),
            ],
            'type': 'ir.actions.act_window',
        }