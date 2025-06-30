# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re
from datetime import timedelta, date
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = ['hr.employee']

    driver_license_expiration = fields.Date('Fecha de Vencimiento de la licencia de conducir',tracking=True)
    driven_vehicles = fields.Many2many('ing.vehicle', string='Vehiculos que maneja')
    license_class = fields.Many2many('ing.type.lic', string='Clases de licencias de conducir',tracking=True)

    departure_reason = fields.Selection([
        ('fired', 'Despedido'),
        ('resigned', 'Renuncio'),
        ('retired', 'Jubilado'),
        ('death', 'Fallecio')
    ], string="Motivo de Salida", groups="hr.group_hr_user", copy=False, tracking=True)

    # Funciones
    def _generate_activity_driver_license_expiration(self):
        _date = date.today() + timedelta(days=30)
        emps = self.search([('driver_license_expiration', '<=', _date)])

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ref_channel = self.env.ref("ing_licencias.ing_channel_activities_scheduler_action")
        channel = f'''<a href="{base_url}/web#model=mail.channel&amp;id={ref_channel.id}" 
                                     class="o_channel_redirect" data-oe-id="{ref_channel.id}" data-oe-model="mail.channel" 
                                     target="_blank">#{ref_channel.name}</a>'''
        for emp in emps:
            body = f'''{channel} Aviso de Vencimiento de Licencia. Se le comunica que El/La Sr./Sra. <strong>
                              {emp.name}</strong> debera renovar su licencia antes del dia <strong>
                              {emp.driver_license_expiration.strftime("%d/%m/%Y")}</strong>'''
            self.env['mail.channel'].browse(ref_channel.id).message_post(attachment_ids=[], body=body, channel_ids=[],
                                                                         message_type='comment', partner_ids=[],
                                                                         subtype_xmlid='mail.mt_comment')

    def get_licencias(self):
        licencias = self.env['ing.licencias.general'].get_licencias_employee(self.id)
        tree_view = self.env.ref('ing_licencias.view_formgeneral_tree')
        form_view = self.env.ref('ing_licencias.view_formgeneral_form')
        return {
            'name': 'Licencias',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'ing.licencias.general',
            'domain': [('id', 'in', licencias.ids)],
            'views': [
                (tree_view.id, 'tree'),
                (form_view.id, 'form'),
            ],
            'type': 'ir.actions.act_window',
        }

    def get_horas_sev(self):
        horas_sev = self.env['ing.licencias.general'].get_horas_sev_employee(self.id)
        tree_view = self.env.ref('ing_licencias.view_formgeneral_tree')
        form_view = self.env.ref('ing_licencias.view_formgeneral_horas_sev_form')
        return {
            'name': 'Horas Sev.',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'ing.licencias.general',
            'domain': [('id', 'in', horas_sev.ids)],
            'views': [
                (tree_view.id, 'tree'),
                (form_view.id, 'form'),
            ],
            'type': 'ir.actions.act_window',
        }

    def get_vacaciones(self):
        env_general = self.env['ing.licencias.general']
        dic_vac = env_general.get_dias_vacaciones(employe_id=self.id)
        vac = [f'Periodo: {x.get("Periodo")}. Dias: {x.get("Dias")}' for x in dic_vac]
        raise Warning(f'Dias de vacaciones por tomar: \n' + "\n".join(vac))

    def check_availability_hours_sev(self, employee_id):
        hours_sev = self.env['ing.hours.sev'].search([('employee_id', '=', (employee_id or self.id)),
                                                      ('state', '=', 'confirmed')])
        return sum([rec.hours for rec in hours_sev])

    def query_hours_sev(self):
        hours = str(self.check_availability_hours_sev(self.id)).replace('.5', ':30').replace('.0', ':00')
        raise Warning(f'Horas Disponibles: {hours}')


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    departure_reason = fields.Selection([
        ('fired', 'Despedido'),
        ('resigned', 'Renuncio'),
        ('retired', 'Jubilado'),
        ('death', 'Fallecio')
    ], string="Motivo de Salida", default="fired")


class EmployeeWz(models.TransientModel):
    _name = 'hr.employee.wz'

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Empleado')
    date_expired = fields.Date('Fecha de vencimiento de la licencia')
    attach_ids = fields.Many2many('ir.attachment', string='Adjuntos')
    driven_vehicles = fields.Many2many('ing.vehicle', string='Vehiculos que maneja')
    license_class = fields.Many2many('ing.type.lic', string='Clases de licencias de conducir')

    def action_confirm(self):
        self.employee_id.sudo().write({
            'driver_license_expiration': self.date_expired,
            'attach_ids': [(4, a.id) for a in self.attach_ids],
            'driven_vehicles': [(4, a.id) for a in self.driven_vehicles],
            'license_class': [(4, a.id) for a in self.license_class],
        })


