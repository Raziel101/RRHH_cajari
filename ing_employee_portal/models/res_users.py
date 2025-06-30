# -*- coding: utf-8 -*-
from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    def get_employee(self):
        return self.employee_ids[0] if self.employee_ids else False

    def is_manager_alone_area(self):
        return self.has_group('ing_licencias.group_ing_rrhh_licencias_encargado') and \
                  not self.has_group('ing_licencias.group_ing_rrhh_licencias_admin_rrhh') and \
                  not self.has_group('ing_licencias.group_ing_rrhh_licencias_admin')
