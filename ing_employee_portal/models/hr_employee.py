# -*- coding: utf-8 -*-
from odoo import fields, models,api
from datetime import date, timedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    department_id = fields.Many2one(string='Departamento', tracking=True)
    job_title = fields.Char(string='Título del trabajo', tracking=True)
    license_class = fields.Many2many('ing.type.lic', string='Clases de licencias de conducir', tracking=True, store=True)
    category_ids = fields.Many2many(
        'hr.employee.category', 'employee_category_rel',
        'emp_id', 'category_id',
        groups="hr.group_hr_manager,ing_contratos.group_ing_rrhh_contratos_admin_rrhh,ing_contratos.group_ing_rrhh_contratos_encargado,ing_contratos.group_ing_rrhh_contratos_admin",
        string='Tags', tracking=True, store=True)

    def get_job(self):
        return self.job_title if self.view_job_title else self.job_title_for

    def _sync_user(self, user, employee_has_image=False):
        vals = dict(
            work_email=user.email,
            user_id=user.id,
        )
        if not self.image_1920:
            vals['image_1920'] = user.image_1920
        if user.tz:
            vals['tz'] = user.tz
        return vals

    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        for record in self:
            if 'license_class' in vals:
                new_vals = record.license_class.mapped('name')
                record.message_post(
                    body="Clases de licencia modificadas: %s" % ", ".join(new_vals)
                )
            if 'category_ids' in vals:
                new_vals = record.category_ids.mapped('name')
                record.message_post(
                    body="Categorías modificadas: %s" % ", ".join(new_vals)
                )
        return res

    fecha_examen_li = fields.Date(string='Fecha de Examen', tracking=True)
    fecha_dictamen_li = fields.Date(string='Fecha de Dictamen', tracking=True)
    fecha_vigencia_li = fields.Date(string='Fecha de Vigencia', tracking=True)
    dictamen = fields.Selection(
        [
            ('APTO', 'Apto'),
            ('RETENIDO', 'Retenido'),
        ],
        string="Dictamen",
    )

    vigencia_alertada = fields.Boolean(string="Alerta enviada", default=False)

    @api.model
    def cron_check_vigencia(self):
        """
        Verifica empleados cuya fecha de vigencia esté a 30 días.
        Dispara la alerta solo una vez.
        """
        today = date.today()
        limite = today + timedelta(days=30)

        empleados = self.search([
            ('fecha_vigencia_li', '=', limite),
            ('vigencia_alertada', '=', False)
        ])

        for emp in empleados:
            # Crear una actividad en el chatter
            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get_id('hr.employee'),
                'res_id': emp.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': 'Vigencia próxima a vencer',
                'note': f'La fecha de vigencia del examen médico ({emp.fecha_vigencia_li}) vence en 30 días.',
                'user_id': emp.user_id.id or self.env.user.id,
            })
            # Marcar que ya se alertó → no se vuelve a repetir
            emp.vigencia_alertada = True