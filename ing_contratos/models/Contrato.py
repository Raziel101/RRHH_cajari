# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)

_READONLYSTATES = {'cancelada': [('readonly', True)]}


class Contrato(models.Model):
    _name = 'ing.contratos.contratos'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _description = "Contrato"

    # Atributos
    secuencia = fields.Char(string=u"Nº de seguimiento", default=u"NÚMERO", readonly=1)
    funcion_desarrolla = fields.Char(string=u"Funcion", required=True, tracking=True)
    hs_semanales = fields.Char(string=u"Hs. semanales", tracking=True)
    fecha_inicio = fields.Date(string='Inicio Contrato', required=True, tracking=True, states=_READONLYSTATES)
    fecha_fin = fields.Date(string='Fin Contrato', required=True, tracking=True, states=_READONLYSTATES)
    revisar = fields.Boolean(string="Revisar", default=False, states=_READONLYSTATES)
    monto = fields.Monetary(string='Monto', required=True, tracking=True, states=_READONLYSTATES)
    monto_hs_adicionales = fields.Char(string='Monto de Hs. Adicionales', tracking=True, states=_READONLYSTATES)
    state = fields.Selection([('borrador', 'Borrador'),
                              ('confirmada', 'Confirmada'),
                              ('revisar', 'Por revisar'),
                              ('cancelada', 'Cancelada')], tracking=True,
                             default='borrador', string="Estado", states=_READONLYSTATES)
    x_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)
    # Relaciones
    categoria_id = fields.Many2one('ing.contratos.categoria', string='Categoria', states=_READONLYSTATES, copy=True)

    def _get_domain_t_contract(self):
        names = ['clausula', 'facturacion', 'pago_unico', 'temporario', 'locacion', 'clausula_facturacion']
        if self.env.user.has_group('ing_contratos.group_ing_rrhh_contratos_admin_rrhh'):
            names.append('voluntariado')
        return [('name', 'in', names)]

    tipo_contrato_id = fields.Many2one('ing.ausencias.tipo.contrato', string='Relación laboral', required=True,
                                       copy=True, states=_READONLYSTATES,
                                       domain=lambda self: self._get_domain_t_contract())
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True, index=True, states=_READONLYSTATES,
                                  copy=True)
    ing_solicitante_id = fields.Many2one('hr.employee', string='Solicitante', required=True, index=True, readonly=False,
                                         store=True, compute='get_responsable_solicitante', states=_READONLYSTATES,
                                         copy=True)
    departament_id = fields.Many2one('hr.department', string='Departamento', required=True, tracking=True, index=True,
                                     states=_READONLYSTATES, copy=True)
    secretaria_id = fields.Many2one('ing.contratos.secretaria', string='Secretaria', required=True, tracking=True,
                                    compute='get_secretaria', states=_READONLYSTATES, copy=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id, copy=True)
    ing_hora_ids = fields.One2many('ing.contratos.hora', 'ing_contrato_id', string="Horarios", copy=True,
                                   states=_READONLYSTATES)
    attach_ids = fields.Many2many('ir.attachment', string='Adjuntos', domain="[('res_id','=',id)]", copy=True)

    # Related
    tipo_contrato = fields.Char(related="tipo_contrato_id.name", store=True, readonly=True, copy=True)
    telefono = fields.Char(related="employee_id.telefono", store=True, readonly=False, required=True, copy=True)
    domic_real = fields.Char(related="employee_id.domic_real", store=True, readonly=False, required=True, copy=True)
    domic_legal = fields.Char(related="employee_id.domic_legal", store=True, readonly=False, required=True, copy=True)
    dni = fields.Char(related="employee_id.identification_id", store=True, readonly=False, required=True, copy=True)
    cuit = fields.Char(related="employee_id.cuit", store=True, readonly=False, required=True, copy=True)
    fecha_nac = fields.Date(related="employee_id.birthday", store=True, readonly=False, required=True, copy=True)

    # Funciones
    @api.depends('state')
    def _compute_css(self):
        group_encargado = self.user_has_groups('ing_contratos.group_ing_rrhh_contratos_encargado')
        group_rrhh = self.user_has_groups('ing_contratos.group_ing_rrhh_contratos_admin_rrhh')
        group_admin = self.user_has_groups('ing_contratos.group_ing_rrhh_contratos_admin')
        estate = self.state

        def condition():
            if estate:
                if group_encargado and not group_rrhh and not group_admin:
                    return True
            else:
                return False

        for record in self:
            if condition():
                record.x_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.x_css = False

    def name_get(self):
        res = []
        for record in self:
            name = str(record.employee_id.name) + u'--' + str(record.fecha_inicio)
            res.append((record.id, name))
        return res

    def view_history_attach(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('ing_contratos.view_attach_min').id,
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
            'context': {'create': 0, 'edit': 0}
        }

    def call_wizard_horarios(self):
        """
        :return: Llama al wizard horarios, usado para generar los horarios de cursos
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'horarios.contratos.wizard',
            'target': 'new',
            'context': {'default_ing_contrato_id': self.id},
        }

    def call_wizard_attach(self):
        """
        :return: Llama al wizard attach, usado para adjuntar imagenes
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'attachment.wizard',
            'target': 'new',
            'context': {'default_ing_contrato_id': self.id},
        }

    def call_wizard_correccion(self):
        """
        :return: Llama al wizard nota de correccion
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'nota.correccion.wizard',
            'target': 'new',
            'context': {'default_ing_contrato_id': self.id},
        }

    def a_revisar(self):
        self.write({'revisar': True, 'state': 'revisar'})

    def confirmar(self):
        self.write({'state': 'confirmada', 'revisar': False})

    def cancelar(self):
        self.write({'state': 'cancelada'})

    def volver_borrador(self):
        self.write({'revisar': False, 'state': 'borrador'})

    def copy(self, default=None):
        default = dict(default or {})
        default.update({'revisar': False})
        return super(Contrato, self).copy(default=default)

    # def write(self, vals):
    #     if not self.env.user.has_group('ing_contratos.group_ing_rrhh_contratos_admin_rrhh'):
    #         vals['revisar'] = True
    #         vals['state'] = 'revisar'
    #     return super(Contrato, self).write(vals)

    @api.model
    def create(self, vals):
        if 'secuencia' not in vals or vals['secuencia'] == u"NÚMERO":
            aux = self.env['ir.sequence'].next_by_code('ing.sec.contratos.contratos')
            vals['secuencia'] = aux
        return super(Contrato, self).create(vals)

    @api.depends('departament_id')
    def get_secretaria(self):
        for rec in self:
            rec.secretaria_id = rec.departament_id.secretaria_ids.filtered(lambda x: x.id)

    @api.depends('departament_id.manager_id')
    def get_responsable_solicitante(self):
        for rec in self:
            rec.ing_solicitante_id = rec.departament_id.manager_id.id

    def get_contratos_employee(self, employee_id):
        return self.search([('employee_id', '=', employee_id)])

    def print_contrato(self):
        return self.env.ref('ing_contratos.report_ing_listado_contratos').report_action(self)

    def reemplazar_contenido(self, contrato_id):
        reemplazar = contrato_id.tipo_contrato_id.texto_contrato.replace('{NOMBRE}',
                                                                         '<strong style="font-size: 25px;">{0}</strong>'.format(
                                                                             contrato_id.employee_id.name)) \
            .replace('{DNI}',
                     '<strong style="font-size: 25px;">{0}</strong>'.format(contrato_id.employee_id.identification_id)) \
            .replace('{SECRETARIA}', '<strong>{0}</strong>'.format(contrato_id.secretaria_id.name)) \
            .replace('{RESPONSABLE}', '<strong>{0}</strong>'.format(contrato_id.departament_id.manager_id.name)) \
            .replace('{DNI_DE_SEC}',
                     '<strong>{0}</strong>'.format(contrato_id.departament_id.manager_id.identification_id)) \
            .replace('{FECHA_NAC}', '<strong>{0}</strong>'.format(contrato_id.employee_id.birthday)) \
            .replace('{DOM_REAL}', '<strong>{0}</strong>'.format(contrato_id.employee_id.domic_real)) \
            .replace('{DOM_LEGAL}', '<strong>{0}</strong>'.format(contrato_id.employee_id.domic_legal)) \
            .replace('{TEL}', '<strong>{0}</strong>'.format(contrato_id.employee_id.phone)) \
            .replace('{FECHA_CONTRATO}', '<strong>{0}</strong>'.format(contrato_id.fecha_inicio)) \
            .replace('{FECHA_FINCONTRATO}', '<strong>{0}</strong>'.format(contrato_id.fecha_fin)) \
            .replace('{FUNCION}', '<strong>{0}</strong>'.format(contrato_id.funcion_desarrolla)) \
            .replace('{MONTO}', '<strong>{0}</strong>'.format(contrato_id.monto)) \
            .replace('{CUIT}', '<strong>{0}</strong>'.format(contrato_id.employee_id.cuit))
        return reemplazar
