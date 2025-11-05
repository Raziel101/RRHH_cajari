# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    department_id = fields.Many2one(string='Departamento', tracking=True)
    job_title = fields.Char(string='Título del trabajo', tracking=True)
    license_class = fields.Many2many('ing.type.lic', string='Clases de licencias de conducir', tracking=True,
                                     store=True)
    category_ids = fields.Many2many(
        'hr.employee.category', 'employee_category_rel',
        'emp_id', 'category_id',
        groups="hr.group_hr_manager,ing_contratos.group_ing_rrhh_contratos_admin_rrhh,ing_contratos.group_ing_rrhh_contratos_encargado,ing_contratos.group_ing_rrhh_contratos_admin",
        string='Tags', tracking=True, store=True)

    fecha_examen_li = fields.Date(string='Fecha de Examen', tracking=True)
    fecha_dictamen_li = fields.Date(string='Fecha de Dictamen', tracking=True)
    fecha_vigencia_li = fields.Date(string='Fecha de Vigencia', tracking=True)
    dictamen = fields.Selection([
            ('APTO', 'Apto'),
            ('RETENIDO', 'Retenido'),
        ], string="Dictamen")
    vigencia_alertada = fields.Boolean(string="Alerta enviada", default=False)

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

    @api.model
    def _generate_activity_psychophysical_expiration(self):
        """Aviso diario de psicofísicos que vencen en menos de 30 días."""

        hoy = date.today()
        target_date = hoy + timedelta(days=30)

        # Ejecutar la búsqueda con privilegios elevados
        employees = self.sudo().search([
            ('fecha_vigencia_li', '!=', False),
            ('fecha_vigencia_li', '>=', hoy),
            ('fecha_vigencia_li', '<=', target_date),
        ])

        # Buscar o crear canal con sudo
        channel = self.env['mail.channel'].sudo().search([
            ('name', '=', 'Vencimiento Licencia Psicofisico')
        ], limit=1)

        if not channel:
            channel = self.env['mail.channel'].sudo().create({
                'name': 'Vencimiento Licencia Psicofisico',
                'public': 'public',
                'channel_type': 'channel',
            })
            all_partners = self.env['res.users'].sudo().search([]).mapped('partner_id')
            channel.sudo().write({'channel_partner_ids': [(6, 0, all_partners.ids)]})

        for emp in employees:
            fecha_vig = fields.Date.from_string(emp.fecha_vigencia_li)

            # Verificar actividad existente con sudo
            exist = self.env['mail.activity'].sudo().search([
                ('res_model', '=', 'hr.employee'),
                ('res_id', '=', emp.id),
                ('summary', '=', 'Vencimiento de psicofísico')
            ], limit=1)

            if not exist:
                self.env['mail.activity'].sudo().create({
                    'res_model_id': self.env.ref('hr.model_hr_employee').id,
                    'res_id': emp.id,
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'user_id': emp.user_id.id or self.env.uid,
                    'summary': 'Vencimiento de psicofísico',
                    'note': f'El psicofísico de {emp.name} vence el {fecha_vig.strftime("%d/%m/%Y")}',
                    'date_deadline': fecha_vig,
                })

            # Mensaje diario en canal
            channel.sudo().message_post(
                body=(
                    f"⚠️ <b>Vencimiento próximo de Psicofísico</b><br/>"
                    f"<b>{emp.name}</b> vence el <b>{fecha_vig.strftime('%d/%m/%Y')}</b>"
                ),
                subtype_xmlid="mail.mt_comment"
            )

    """def _cron_alerta_vencimiento(self):
        hoy = date.today()
        empleados = self.search([
            ('fecha_vigencia_li', '!=', False)
        ])

        # Buscar canal, si no existe lo creamos
        canal = self.env['mail.channel'].sudo().search([
            ('name', '=', 'Vencimiento Licencia Psicofisico')
        ], limit=1)

        if not canal:
            canal = self.env['mail.channel'].sudo().create({
                'name': 'Vencimiento Licencia Psicofisico',
                'public': 'public',  # visible para todos
                'channel_type': 'channel',  # sala de conversación
            })

        # Agregar TODOS los usuarios de Odoo al canal (solo una vez)
        all_partners = self.env['res.users'].sudo().search([]).mapped('partner_id')
        canal.write({'channel_partner_ids': [(6, 0, all_partners.ids)]})

        model_id = self.env['ir.model'].sudo().search([('model', '=', 'hr.employee')]).id

        for empleado in empleados:
            fecha_vigencia = fields.Date.from_string(empleado.fecha_vigencia_li)
            alerta_fecha = fecha_vigencia - timedelta(days=30)

            if alerta_fecha == hoy:
                # Verificar si ya existe actividad
                existe = self.env['mail.activity'].search([
                    ('res_model', '=', 'hr.employee'),
                    ('res_id', '=', empleado.id),
                    ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id),
                    ('summary', '=', 'Vencimiento de psicofísico'),
                ], limit=1)

                if not existe:
                    # Crear actividad en la ficha del empleado
                    self.env['mail.activity'].create({
                        'res_model_id': model_id,
                        'res_id': empleado.id,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'user_id': empleado.user_id.id or self.env.uid,
                        'summary': 'Vencimiento de psicofísico',
                        'note': f'El psicofísico de {empleado.name} vence el {fecha_vigencia.strftime("%d/%m/%Y")}',
                        'date_deadline': fecha_vigencia,
                    })

                    # Mensaje en el canal visible y notificado a todos
                    canal.message_post(
                        body=(
                            f"⚠️ <b>Alerta de vencimiento de Licencia Psicofísico</b><br/>"
                            f"Empleado: <b>{empleado.name}</b><br/>"
                            f"Fecha de vencimiento: {fecha_vigencia.strftime('%d/%m/%Y')}"
                        ),
                        subtype_xmlid="mail.mt_comment"
                    )"""




