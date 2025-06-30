# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from odoo.exceptions import Warning
_logger = logging.getLogger(__name__)

_READONLYSTATES= {'cancelada':[('readonly',True)]}
class Ausencias(models.Model):
    _name = 'ing.ausencias.ausencias'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _description = "Ausencias"

    # Atributos
    name                    = fields.Char(string=u"Motivo descripción", required=True, tracking=True, states=_READONLYSTATES)
    aviso                   = fields.Boolean(string="¿Aviso?", tracking=True)
    sin_descuento           = fields.Boolean(string="Sin descuento", default=False, states=_READONLYSTATES)
    revisar                 = fields.Boolean(string="Revisar", default=False,states=_READONLYSTATES )
    fecha_inicio            = fields.Date(string='Fecha de ausencia', index=True, required=True, default=fields.Date.context_today, states=_READONLYSTATES)
    state                   = fields.Selection([('borrador','Borrador'),
                                                ('confirmada','Confirmada'),
                                                ('revisar', 'Por revisar'),
                                                ('cancelada','Cancelada')],
                                               default='borrador', string="Estado", states=_READONLYSTATES, tracking=True)
    tipo_contrato           = fields.Selection([('planta_permanente', 'Planta Permanente'),
                                                ('planta_temporaria', 'Planta Temporaria'),
                                                ('contratado', 'Contratado')],
                                               string="Tipo contrato_",
                                               states=_READONLYSTATES)
    relate_tipo_contrato    = fields.Char(related="tipo_contrato_id.name", readonly=True)

    def _get_domain_t_contract(self):
        names = ['planta_permanente', 'planta_temporaria', 'locacion', 'contrato_facturacion']
        if self.env.user.has_group('ing_ausencias.group_ing_rrhh_ausencias_admin_rrhh'):
            names.append('voluntariado')
        return [('name', 'in', names)]

    # Relaciones
    tipo_contrato_id        = fields.Many2one('ing.ausencias.tipo.contrato', string='Tipo de Contrato', required=True,
                                              states=_READONLYSTATES,
                                              domain=lambda self: self._get_domain_t_contract())
    employee_id             = fields.Many2one('hr.employee', string='Empleado', required=True, states=_READONLYSTATES)
    ing_medio_aviso_id      = fields.Many2one('ing.ausencias.medio.aviso', string='Medio de Aviso', required=True, states=_READONLYSTATES)
    motivo_ausencia_id      = fields.Many2one('ing.motivo.ausencia',string="Tipo ausencia", states=_READONLYSTATES)
    area_id                 = fields.Many2one('hr.department',string="Departamento",required=True,states=_READONLYSTATES)
    attach_ids              = fields.Many2many('ir.attachment', string='Adjuntos', domain="[('res_id','=',id)]")
    
    # Funciones
    @api.onchange('employee_id')
    def set_area(self):
        if not self.area_id:
            if self.employee_id and self.employee_id.department_id:
                self.area_id = self.employee_id.department_id.id

            elif self.env.user.areasgob_ids.ids:
                self.area_id = self.env.user.areasgob_ids[0].id

    def view_history_attach(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('ing_ausencias.view_attach_min').id,
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
            'context': {'create': 0, 'edit': 0}
        }

    def a_revisar(self):
        self.write({'revisar':True, 'state':'revisar'})

    def confirmar(self):
        self.write({'state': 'confirmada','revisar':False})

    def cancelar(self):
        self.write({'state': 'cancelada'})

    def volver_borrador(self):
        self.write({'state': 'borrador'})

    def write(self, vals):
        if not self.env.user.has_group('ing_ausencias.group_ing_rrhh_ausencias_admin_rrhh'):
            vals['revisar'] = True
            vals['state'] = 'revisar'
        return super(Ausencias, self).write(vals)

    def get_ausencias_employee(self, employee_id):
        return self.search([('employee_id','=', employee_id)])

    def call_wizard_attach(self):
        """
        :return: Llama al wizard attach, usado para adjuntar imagenes
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ausencias.attachment.wizard',
            'target': 'new',
            'context': {'default_ing_ausencia_id': self.id},
        }

    def call_wizard_correccion(self):
        """
        :return: Llama al wizard nota de correccion
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ausencias.nota.correccion.wizard',
            'target': 'new',
            'context': {'default_ing_ausencia_id': self.id},
        }

class MotivoAusencias(models.Model):
    _name = 'ing.motivo.ausencia'

    name = fields.Char(string="Motivo")