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

    def _cron_alerta_vencimiento(self):
        """Genera una actividad y una alerta en canal 30 días antes de la fecha de vigencia"""
        hoy = date.today()
        empleados = self.search([
            ('fecha_vigencia_li', '!=', False)
        ])

        model_id = self.env['ir.model'].sudo().search([('model', '=', 'hr.employee')]).id
        canal = self.env['mail.channel'].sudo().search([('name', '=', 'Vencimiento Licencia Psicofisico')], limit=1)
        if not canal:
            canal = self.env['mail.channel'].sudo().create({
                'name': 'Vencimiento Licencia Psicofisico',
                'channel_type': 'channel',
                'public': 'public',
            })

        for empleado in empleados:
            alerta_fecha = empleado.fecha_vigencia_li - timedelta(days=30)
            if alerta_fecha == hoy and not empleado.vigencia_alertada:
                # Verificar que no se haya creado ya una actividad para este vencimiento
                existe = self.env['mail.activity'].search([
                    ('res_model', '=', 'hr.employee'),
                    ('res_id', '=', empleado.id),
                    ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id),
                    ('summary', '=', 'Vencimiento de psicofísico'),
                ], limit=1)

                if not existe:
                    self.env['mail.activity'].create({
                        'res_model_id': model_id,
                        'res_id': empleado.id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'user_id': empleado.user_id.id or self.env.uid,
                        'summary': 'Vencimiento de psicofísico',
                        'note': f'El psicofísico de {empleado.name} vence el {empleado.fecha_vigencia_li}',
                        'date_deadline': empleado.fecha_vigencia_li,
                    })

                # 📢 Enviar mensaje al canal de conversación
                canal.message_post(
                    body=(
                        f"⚠️ <b>Vencimiento de Licencia Psicofísico</b><br/>"
                        f"Empleado: <b>{empleado.name}</b><br/>"
                        f"Fecha de vencimiento: {empleado.fecha_vigencia_li.strftime('%d/%m/%Y')}"
                    ),
                    subtype_xmlid="mail.mt_comment"
                )

                # Marcar como alertado para no duplicar
                empleado.vigencia_alertada = True
