# -*- coding: utf-8 -*-
from odoo import api, fields, models


class FormGeneral(models.Model):
    _inherit = 'ing.licencias.general'

    state = fields.Selection(selection_add=[('create_portal', 'Por Autorizar')])
    view_alert_create_portal = fields.Boolean()
    view_request_admin = fields.Boolean(compute='compute_view_request_admin',
        help='Si es True el boton Autorizar solo sera visible para explicitamente administradores de solicitudes y admin de sistema')

    @api.onchange('base_form_id')
    def onchange_empleado(self):
        if self.base_form_id:
            lic_ids = self.env['ing.licencias.general'].search([('base_form_id', '=', self.base_form_id.id),
                                                                ('state', '=', 'create_portal')])
            self.view_alert_create_portal = bool(lic_ids)
        return super().onchange_empleado()

    def compute_view_request_admin(self):
        for rec in self:
            res = self.env.user.has_group('ing_licencias.group_ing_rrhh_licencias_admin') or \
                  self.env.user.has_group('ing_licencias.group_ing_rrhh_licencias_encargado') and \
                  not self.env.user.has_group('ing_licencias.group_ing_rrhh_licencias_admin_rrhh')
            rec.view_request_admin = res

    def action_to_draft(self):
        for rec in self:
            rec.sudo().write({'state': 'borrador'})

    def get_sum_days_available(self, employee_id: int):
        env_vacaciones = self.env['ing.alta.baja.licencia']
        get_search = env_vacaciones.search_read([('employee_id', '=', employee_id)],
                                                ['periodo', 'dias'], order='periodo asc')
        list_periodo = []
        dic_suma = 0
        # Genera la lista de periodos
        [list_periodo.append(x.get('periodo')) for x in get_search if x.get('periodo') not in list_periodo]

        for l in list_periodo:
            search_vac = env_vacaciones.search(
                [('employee_id', '=', employee_id), ('periodo', '=', l)])
            dias_disponibles = sum(map(lambda d: d.dias, search_vac))
            if dias_disponibles > 0:
                dic_suma += dias_disponibles
        return dic_suma


    def get_template_licencia_franquicia(self):
        res = super().get_template_licencia_franquicia()
        res['domain'].append(('state', 'not in', ['create_portal']))
        return res

    def get_template_hs_sev(self):
        res = super().get_template_hs_sev()
        res['domain'].append(('state', 'not in', ['create_portal']))
        return res

    def create_message_new_rec_from_portal(self, lic):
        mail = self.env['mail.mail'].sudo()
        dep = lic.base_form_id.employee_id.department_id
        users = self.env['res.users'].sudo().search([('areasgob_ids', 'in', dep.id)])
        for u in users.filtered(lambda x: x.is_manager_alone_area()):
            mail.create({
                'subject': u'Solicitud de Aprobación',
                'body_html': f'''Se solicita la aprobación de una {lic.tipo_lic_id.detalle} para <strong> 
                                {lic.base_form_id.employee_id.name}. </strong>''',
                'email_to': u.email,
                'email_from': 'rrhh@chajari.gob.ar',
                'message_type': 'email',
                'reply_to': '',
            }).send()
