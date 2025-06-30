from odoo import models, fields

class Ausencias(models.Model):
    _inherit = 'ing.ausencias.ausencias'

    tipo_contrato_id = fields.Many2one(related='employee_id.tipo_contrato_id', store=True, required=False)
    area_id = fields.Many2one(related='employee_id.department_id', store=True, required=False)

    def check_departments(self):
        for rec in self:
            rec.write({'area_id': rec.employee_id.department_id.id})
