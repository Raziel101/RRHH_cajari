# -*- coding: utf-8 -*-
from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    department_id = fields.Many2one(string='Departamento', tracking=True)
    job_title = fields.Char(string='Título del trabajo', tracking=True)

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
