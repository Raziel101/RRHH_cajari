# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re
import logging

_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = ['hr.employee']

    # Atributos
    funcion = fields.Char(string=u"Funcion", compute='_get_funcion_desempenia', tracking=True)
    date_first_contract = fields.Date(string=u'Fecha de 1er Contrato', tracking=True)
    date_init_plant = fields.Date(string=u'Fecha de inicio de planta', tracking=True)

    def _get_domain_t_contract(self):
        names = ['planta_temporaria','planta_permanente','locacion','contrato_facturacion','pago_unico','funcionarios_publicos']
        if self.env.user.has_group('ing_contratos.group_ing_rrhh_contratos_admin_rrhh'):
            names.append('voluntariado')
        return [('name', 'in', names)]

    # Relaciones
    tipo_contrato_id = fields.Many2one('ing.ausencias.tipo.contrato', string='Tipo de Contrato', required=True,
                                       copy=True, tracking=True, domain=lambda self: self._get_domain_t_contract())

    # Relacion sobreescrita
    category_ids = fields.Many2many(
        'hr.employee.category', 'employee_category_rel',
        'emp_id', 'category_id',
        groups="hr.group_hr_manager,ing_contratos.group_ing_rrhh_contratos_admin_rrhh,ing_contratos.group_ing_rrhh_contratos_encargado,ing_contratos.group_ing_rrhh_contratos_admin",
        string='Tags', tracking=True)

    contrato_ids = fields.One2many('ing.contratos.contratos', 'employee_id', string='Contratos', tracking=True)
    job_title_for = fields.Char('Funcion', compute="_compute_job_title", store=False, readonly=False, tracking=True)

    """ El campo 'view_job_title' lo uso para mostrar el 'job_title' o el 'job_title_for' dependiendo de 'tipo_contrato_id'"""
    view_job_title = fields.Boolean(compute="_compute_view_job_title", store=False, tracking=True)

    @api.depends('contrato_ids.fecha_inicio')
    def _compute_job_title(self):
        """
        Ariel me solicito que en el campo 'job_title_for' muestre la funcion desarrolla cuando el tipo del ultimo
        contrato es 'clausulas de facturacion o locacion, locacion de servicios, contratos temporarios, facturacion',
        en otro caso se introduce a mano el valor. Si el contrato es de 'pago unico' no se debe hacer nada.
        """
        for employee in self.filtered(lambda x: x.tipo_contrato_id):
            if employee.tipo_contrato_id.id != self.env.ref('ing_ausencias.planta_temporaria').id:
                contrato = employee._get_last_contrato_no_pago_unico()
                employee.job_title_for = contrato[0]['funcion_desarrolla'] if contrato else ''

    def _get_last_contrato_no_pago_unico(self):
        return self.env['ing.contratos.contratos'].search_read([('employee_id.id','=',self.id),
                                                                ('tipo_contrato_id.id','!=',self.env.ref('ing_ausencias.contrato_pago_unico').id)],
                                                                ['funcion_desarrolla'],
                                                                order='fecha_inicio desc',limit=1)

    def _compute_view_job_title(self):
        _lista = [self.env.ref('ing_ausencias.contratado_facturacion').id,self.env.ref('ing_ausencias.locacion_servicios').id]
        for e in self:
            e.view_job_title = e.tipo_contrato_id.id not in _lista

    def _get_funcion_desempenia(self):
        env_contratos = self.env['ing.contratos.contratos']
        locacion_servicio = env_contratos.search(
            [('tipo_contrato_id.name', '=', 'locacion'), ('employee_id', '=', self.id)], limit=1)

        if locacion_servicio:
            self.funcion = locacion_servicio.funcion_desarrolla
        else:
            self.funcion = ''

    def get_contrato(self):
        contratos = self.env['ing.contratos.contratos'].get_contratos_employee(self.id)
        tree_view = self.env.ref('ing_contratos.view_contrato_tree')
        form_view = self.env.ref('ing_contratos.view_contrato_form')
        return {
            'name': 'Contratos',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'ing.contratos.contratos',
            'domain': [('id', 'in', contratos.ids)],
            'views': [
                (tree_view.id, 'tree'),
                (form_view.id, 'form'),
            ],
            'type': 'ir.actions.act_window',
        }

    def name_get(self):
        res = []
        for record in self:
            name = str(record.name) + '-' + str(record.identification_id)
            res.append((record.id, name))
        return res
