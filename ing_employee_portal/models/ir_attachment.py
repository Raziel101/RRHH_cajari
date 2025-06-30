from odoo import models, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def check(self, mode, values=None):
        lic_base = self.env['ing.licencias.base'].sudo()
        _user = self.env.user.get_employee().id if self.env.user.get_employee() else False
        res = bool(lic_base.search([('employee_id', '=', _user)], limit=1))
        return res or super().check(mode, values)

