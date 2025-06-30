# -*- encoding: utf-8 -*-
from odoo.http import request
from odoo import models, fields, api


class PrintCredentialCustomWZ(models.TransientModel):
    _name = 'ing.credential.custom.wz'

    employee_id = fields.Many2one('hr.employee', readonly=True, string='Empleado')
    dni = fields.Boolean('Dni')
    job = fields.Boolean('Función')
    type_contract = fields.Boolean('Revista o Tipo de Contrato')
    birthdate = fields.Boolean('Fecha de Nacimiento')
    department = fields.Boolean('Departamento')
    address = fields.Boolean('Domicilio')
    phone = fields.Boolean('Telefóno')
    cuit = fields.Boolean('Cuil')

    def print_credential_custom(self):
        datas = {
            'ids': self.employee_id.ids,
            'model': 'hr.employee',
            'dni': self.dni,
            'cuit': self.cuit,
            'address': self.address,
            'phone': self.phone,
            'job': self.job,
            'type_contract': self.type_contract,
            'department': self.department,
            'birthdate': self.birthdate,
        }
        return self.env.ref('hr.hr_employee_print_badge').report_action(self.employee_id, data=datas)
