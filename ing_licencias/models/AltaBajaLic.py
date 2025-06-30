# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

_READONLYSTATES = {'confirmada': [('readonly', True)]}


class AltaBajaLic(models.Model):
    _name = 'ing.alta.baja.licencia'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _rec_name = 'employee_id'
    _description = "AltaBajaLic"

    # Atributos
    state = fields.Selection([('alta', 'Alta'),
                              ('reservada', 'Reservada'),
                              ('confirmada', 'Confirmada'),
                              ('revisar', 'Por revisar'), ],
                             default='alta', string="Estado", states=_READONLYSTATES)
    dias = fields.Integer(string=u"Dias", tracking=True, states=_READONLYSTATES, required=True)
    periodo = fields.Char(string=u"Periodo", tracking=True, size=4, required=True,
                          readonly=False, store=True, states=_READONLYSTATES)
    fecha_inicio = fields.Date(string='Fecha de inicio', tracking=True, states=_READONLYSTATES, required=True)
    descripcion = fields.Text(string='Observaciones')

    # Relaciones
    tipo_lic_id = fields.Many2one('ing.licencias.tipo', string='Tipo Licencia')
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True, states=_READONLYSTATES)
    departament_id = fields.Many2one(related="employee_id.department_id", string="Departamento", readonly=1)
    attach_ids = fields.Many2many('ir.attachment', string='Adjuntos', domain="[('res_id','=',id)]")

    # Funciones
    def alta(self):
        self.write({'state': 'alta'})

    def reservada(self):
        self.write({'state': 'reservada'})

    def confirmada(self):
        self.write({'state': 'confirmada'})

    def revisar(self):
        self.write({'state': 'revisar'})

    def write(self, vals):
        if not self.env.user.has_group('ing_licencias.group_ing_rrhh_licencias_admin_rrhh'):
            vals['state'] = 'reservada'
        self._check_date_for_vacaciones(vals)

        return super(AltaBajaLic, self).write(vals)

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('ing_licencias.group_ing_rrhh_licencias_admin_rrhh'):
            vals['state'] = 'reservada'

        self._check_date_for_vacaciones(vals)

        return super(AltaBajaLic, self).create(vals)

    def _check_date_for_vacaciones(self, vals):
        if not self.env.user.has_group('ing_licencias.group_ing_rrhh_licencias_admin_rrhh'):
            lic_id = self.env.ref('ing_licencias.lic_vacaciones').id
            if vals.get('tipo_lic_id') and vals.get('fecha_inicio'):
                if datetime.strptime(vals['fecha_inicio'], '%Y-%m-%d') < datetime.today() and vals['tipo_lic_id'] == lic_id:
                    raise UserError('No se pueden cargar vacaciones, con fecha de inicio, anterior a la fecha de creación.')


    def call_wizard_attach(self):
        """
        :return: Llama al wizard attach, usado para adjuntar imagenes
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'attachment.vacaciones.wizard',
            'target': 'new',
            'context': {'default_ing_vacaciones_id': self.id},
        }

    def call_wizard_correccion(self):
        """
        :return: Llama al wizard nota de correccion
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'nota.correccion.vacaciones.wizard',
            'target': 'new',
            'context': {'default_ing_vacaciones_id': self.id},
        }