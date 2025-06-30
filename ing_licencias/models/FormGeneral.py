# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from calendar import monthrange
from odoo.exceptions import UserError, ValidationError, RedirectWarning
import logging

_logger = logging.getLogger(__name__)

_READONLYSTATES = {'cancelada': [('readonly', True)]}


class FormGeneral(models.Model):
    _name = 'ing.licencias.general'
    _inherit = 'mail.thread'
    _rec_name = 'base_form_id'
    _order = "create_date desc"
    _description = "Licencias y Franquicias"

    state = fields.Selection([('borrador', 'Borrador'),
                              ('confirmada', 'Confirmada'),
                              ('revisar', 'Por revisar'),
                              ('cancelada', 'Cancelada')], tracking=True,
                             default='borrador', string="Estado", states=_READONLYSTATES)
    hs_del_mes = fields.Selection([('enero', 'Enero'),
                                   ('febrero', 'Febrero'),
                                   ('marzo', 'Marzo'),
                                   ('abril', 'Abril'),
                                   ('mayo', 'Mayo'),
                                   ('junio', 'Junio'),
                                   ('julio', 'Julio'),
                                   ('agosto', 'Agosto'),
                                   ('septiembre', 'Septiembre'),
                                   ('octubre', 'Octubre'),
                                   ('noviembre', 'Noviembre'),
                                   ('diciembre', 'Diciembre')],
                                  default='enero', string="Hs. del mes de:", states=_READONLYSTATES)
    revisar = fields.Boolean(string="Revisar", default=False, states=_READONLYSTATES)
    cantidad_hs = fields.Integer(string=u"Cantidad de Hs.", tracking=True, states=_READONLYSTATES)
    dias_solicitados = fields.Integer(string=u"Dias Solicitados", tracking=True, states=_READONLYSTATES)
    fecha_inicio = fields.Date(string='Fecha de inicio', states=_READONLYSTATES)
    aviso = fields.Boolean(string="¿Aviso?", tracking=True)
    confirma = fields.Boolean(string="Confirma", tracking=True)
    descripcion = fields.Text(string='Observaciones')
    fecha_reingreso = fields.Date(string='Fecha de fin Lic.', compute='_compute_fecha_reingreso', store=False)
    tipo_lic_no_remunerada = fields.Selection([('lic_electiva','Lic. por cargos electivos o de representación politica'),
                                               ('lic_particular','Lic. por razones particulares'),
                                               ('lic_enfermedad','Lic. por enfermedad de familiar a cargo'),
                                               ('lic_capacitacion','Lic. por capacitación'),
                                               ('lic_integracion','Lic. por integración del grupo familiar'),
                                               ('lic_evento','Lic. por evento deportivo no rentado')],string='Tipo No Remun.')
    observaciones = fields.Text(string='Observaciones')
    activity_ids = fields.Many2many('mail.activity', string='Actividades')

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id, readonly=True)

    def _get_domain_base_form_id(self):
        if not self.env.user.has_group('base.group_system'):
            return [('departament_id', 'in', self.env.user.areasgob_ids.ids)]
        else:
            return []

    base_form_id = fields.Many2one('ing.licencias.base', string='Datos del Empleado', required=True,
                                   domain=_get_domain_base_form_id)
    ing_medio_aviso_id = fields.Many2one('ing.ausencias.medio.aviso', string='Medio de Aviso', states=_READONLYSTATES)
    tipo_lic_id = fields.Many2one('ing.licencias.tipo', string='Tipo Licencia', required=True)
    dia_periodo_lic_ids = fields.One2many(comodel_name='ing.licencias.dia.periodo', inverse_name='ing_form_general_id',
                                          string='Dias Disponibles')
    attach_ids = fields.Many2many('ir.attachment', string='Adjuntos', domain="[('res_id','=',id)]")

    tipo_lic_name = fields.Char(related="tipo_lic_id.name", store=True, readonly=True)
    departament_id = fields.Many2one(related="base_form_id.employee_id.department_id", string="Departamento",
                                     store=True, readonly=False, required=True)

    def _employee_not_in_planta(self, vals=None):
        _contracts = [self.env.ref('ing_ausencias.planta_temporaria').id, self.env.ref('ing_ausencias.planta_permanente').id]
        if vals:
            employee_id = self.env['ing.licencias.base'].browse(vals.get('base_form_id')).employee_id
            res = employee_id.tipo_contrato_id.id
        else:
            res = self.base_form_id.employee_id.tipo_contrato_id.id

        return res not in _contracts

    def _change_state(self, state):
        if self.tipo_lic_id.id == self._get_lic_horas_sev_id():
            rec = self.env['ing.hours.sev']
            if state == 'confirmada':
                rec.create({
                    'employee_id': self.base_form_id.employee_id.id,
                    'hours': - (self.dias_solicitados * 6),
                    'state': 'confirmed',
                })
            elif state == 'cancelada':
                rec.create({
                    'employee_id': self.base_form_id.employee_id.id,
                    'hours': (self.dias_solicitados * 6),
                    'state': 'confirmed',
                })

    def a_revisar(self):
        self.write({'revisar': True, 'state': 'revisar'})

    def confirmar(self):
        self.write({'state': 'confirmada', 'revisar': False, 'confirma': True})
        self.generar_descuentos_dias(tipo=-1)

    def cancelar(self):
        self.write({'state': 'cancelada'})
        self.generar_descuentos_dias(tipo=1)

    def volver_borrador(self):
        self.write({'state': 'borrador'})

    def get_licencias_employee(self, employee_id):
        return self.search([('base_form_id.employee_id', '=', employee_id),
                            ('tipo_lic_id', '!=', self._get_lic_horas_sev_id())])

    def get_horas_sev_employee(self, employee_id):
        return self.search([('base_form_id.employee_id', '=', employee_id),
                            ('tipo_lic_id', '=', self._get_lic_horas_sev_id ())])

    def _get_lic_horas_sev_id(self):
        return self.env.ref('ing_licencias.lic_hs_sev_franco').id

    @api.onchange('dias_solicitados')
    def get_dias(self):
        if self.tipo_lic_id.id != self._get_lic_horas_sev_id() and \
                self.tipo_lic_id.id != self.env.ref('ing_licencias.lic_no_remunerada').id:
            #  CALCULA LOS DIAS Y PERIODO
            env_dia_periodo = self.env['ing.licencias.dia.periodo']

            dic_suma = self.get_dict_dia_periodo()

            ds_cont = 0
            for ds in dic_suma:
                ds_cont += ds.get('dias')

            if self.dias_solicitados > int(ds_cont):
                return {
                    'warning': {'title': 'Atencion', 'message': 'Esta solicitando mas dias de los que dispone.', },
                }
            else:
                env_dia_periodo.create(dic_suma)

    def get_dict_dia_periodo(self):
        list_periodo = []
        env_vacaciones = self.env['ing.alta.baja.licencia']
        get_search = env_vacaciones.search_read([('employee_id', '=', self.base_form_id.employee_id.id)],
                                                ['periodo', 'dias'], order='periodo asc')
        # limpiar
        self.dia_periodo_lic_ids = [(5,)]

        # Genera la lista de periodos
        [list_periodo.append(x.get('periodo')) for x in get_search if x.get('periodo') not in list_periodo]

        dic_suma = []
        env_periodo = self.env['ing.licencias.periodo']
        for l in list_periodo:
            periodo = env_periodo.search([('name', '=', l)])
            search_vac = env_vacaciones.search(
                [('employee_id', '=', self.base_form_id.employee_id.id), ('periodo', '=', l)])

            dias_disponibles = sum(map(lambda d: d.dias, search_vac))

            if dias_disponibles > 0:
                if not periodo:
                    p_riodo = env_periodo.create({'name': l})
                    dic_suma.append({'ing_form_general_id': self.id,
                                     'periodo_lic_id': p_riodo.id,
                                     'periodo_lic_name': p_riodo.name,
                                     'dias': dias_disponibles, })
                else:
                    dic_suma.append({'ing_form_general_id': self.id,
                                     'periodo_lic_id': periodo.id,
                                     'periodo_lic_name': periodo.name,
                                     'dias': dias_disponibles, })
        return dic_suma

    @api.model
    def create(self, vals):
        rec = super(FormGeneral, self).create(vals)
        env_tipo = self.env['ing.licencias.tipo']
        lic_id = vals.get('tipo_lic_id')
        name_lic = env_tipo.browse(lic_id)

        if name_lic.name == 'lic_vacaciones' and not vals.get('dia_periodo_lic_ids'):
            raise UserError('No posee dias disponibles, descarte para continuar otra operacion')

        self._check_date_for_vacaciones(vals)
        self._check_date_for_horas_sev(vals)
        if self._employee_not_in_planta(vals):
            raise UserError('El empleado debe ser de Planta')

        if not self.check_horas_sev_availability(vals):
            raise UserError('No tiene suficientes horas sev. disponibles.')

        return rec

    def check_horas_sev_availability(self, vals):
        if self.env.context.get('default_tipo_lic_id') == self._get_lic_horas_sev_id():
            emp_id = self.base_form_id.id or vals.get('base_form_id')
            employee_id = self.env['ing.licencias.base'].browse(emp_id).employee_id.id
            hours_sev = self.base_form_id.employee_id.check_availability_hours_sev(employee_id)
            if 6 * (vals.get('dias_solicitados') or self.dias_solicitados) > hours_sev:
                if vals.get('state') not in ['cancelada', 'revisar']:
                    return False
        return True

    def _check_date_for_horas_sev(self, vals):
        if not self.env.user.has_group('ing_licencias.group_ing_rrhh_licencias_admin_rrhh'):
            if self.env.context.get('default_tipo_lic_id') == self._get_lic_horas_sev_id()\
                    or self.tipo_lic_id.id == self._get_lic_horas_sev_id():
                date_time = datetime.strptime(vals['fecha_inicio'], '%Y-%m-%d') if vals.get('fecha_inicio') else datetime(self.fecha_inicio.year, self.fecha_inicio.month,self.fecha_inicio.day)
                if date_time <= datetime.today() and not vals.get('state') == 'revisar':
                    raise UserError('No se pueden crear con fecha de inicio, anterior o igual a la fecha de creación.')

    def write(self, vals):
        self._check_date_for_vacaciones(vals)
        self._check_date_for_horas_sev(vals)
        if not self.check_horas_sev_availability(vals):
            raise UserError('No tiene suficientes horas sev. disponibles.')
        if vals.get('state'):
            self._change_state(vals.get('state'))

        if self._employee_not_in_planta():
            raise UserError('El empleado debe ser de Planta')

        return super(FormGeneral, self).write(vals)

    def _compute_fecha_reingreso(self):
        for rec in self:
            if rec.tipo_lic_id.id == self.env.ref('ing_licencias.lic_no_remunerada').id:
                if rec.fecha_inicio and rec.dias_solicitados:
                    rec.sudo().write({'fecha_reingreso': rec.fecha_inicio + timedelta(days=rec.dias_solicitados)})
            else:
                #le harcodeo una fecha para que no falle el metodo de computar
                rec.sudo().write({'fecha_reingreso': self.fecha_reingreso})

    def _check_date_for_vacaciones(self, vals):
        if not self.env.user.has_group('ing_licencias.group_ing_rrhh_licencias_admin_rrhh'):
            lic_id = self.env.ref('ing_licencias.lic_vacaciones').id
            if vals.get('tipo_lic_id') and vals.get('fecha_inicio'):
                _date_init = vals['fecha_inicio'] if isinstance(vals['fecha_inicio'], date) else datetime.strptime(vals['fecha_inicio'], '%Y-%m-%d').date()
                if _date_init <= date.today() and vals['tipo_lic_id'] == lic_id:
                    raise UserError('No se pueden cargar vacaciones, con fecha de inicio, anterior o igual a la fecha de creación.')


    def generar_descuentos_dias(self, tipo):
        #  CREAR CUENTA CORRIENTE
        env_periodo = self.env['ing.licencias.periodo']
        env_vacaciones = self.env['ing.alta.baja.licencia']
        dias_periodos = self.dia_periodo_lic_ids
        c_corriente = []
        cont_1 = self.dias_solicitados
        ref_vacaciones = self.env.ref('ing_licencias.lic_vacaciones').id
        if self.confirma and self.tipo_lic_id.id == ref_vacaciones:
            for d in dias_periodos:
                periodo = env_periodo.browse(d.periodo_lic_id.id)

                if self.dias_solicitados > 0 and d.dias > 0:
                    anio = periodo.name
                    dias = d.dias

                    if dias >= cont_1:
                        c_corriente.append({'employee_id': self.base_form_id.employee_id.id,
                                            'fecha_inicio': self.fecha_inicio,
                                            'state': 'reservada',
                                            'periodo': anio,
                                            'dias': cont_1 * tipo})
                        cont_1 = 0
                    else:
                        if cont_1 > 0:
                            c_corriente.append({'employee_id': self.base_form_id.employee_id.id,
                                                'fecha_inicio': self.fecha_inicio,
                                                'state': 'reservada',
                                                'periodo': anio,
                                                'dias': dias * tipo})

                            cont_1 -= dias
            if c_corriente:
                env_vacaciones.create(c_corriente)
            else:
                raise UserError("No poseé dias disponibles")

    def get_days_available(self):
        days_solicited = self.dias_solicitados
        list_dict = []
        for x in self.dia_periodo_lic_ids:
            if x.dias > days_solicited:
                list_dict.append({'days': x.dias - days_solicited, 'period': x.periodo_lic_id.name})
                days_solicited = 0
            else:
                days_solicited -= x.dias
        return list_dict

    def get_dias_periodo_usado(self):
        env_periodo = self.env['ing.licencias.periodo']
        dias_periodos = self.dia_periodo_lic_ids
        c_corriente = []
        cont_1 = self.dias_solicitados

        for d in dias_periodos:
            periodo = env_periodo.browse(d.periodo_lic_id.id)

            if self.dias_solicitados > 0 and d.dias > 0:
                anio = periodo.name
                dias = d.dias

                if dias >= cont_1:
                    c_corriente.append({'periodo': anio,
                                        'dias': cont_1})
                    cont_1 = 0
                else:
                    if cont_1 > 0:
                        c_corriente.append({'periodo': anio,
                                            'dias': dias})

                        cont_1 -= dias
        return c_corriente

    def get_dias_vacaciones(self, employe_id):
        env_vacaciones = self.env['ing.alta.baja.licencia']
        env_periodo = self.env['ing.licencias.periodo']

        get_search = env_vacaciones.search_read([('employee_id', '=', employe_id)],
                                                ['periodo', 'dias'], order='periodo asc')
        list_periodo = []
        dic_suma = []
        # Genera la lista de periodos
        [list_periodo.append(x.get('periodo')) for x in get_search if x.get('periodo') not in list_periodo]

        for l in list_periodo:
            periodo = env_periodo.search([('name', '=', l)])
            search_vac = env_vacaciones.search(
                [('employee_id', '=', employe_id), ('periodo', '=', l)])

            dias_disponibles = sum(map(lambda d: d.dias, search_vac))

            if dias_disponibles > 0:
                dic_suma.append({'Periodo': periodo.name,
                                 'Dias': dias_disponibles, })
        return dic_suma

    def view_history_attach(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('ing_licencias.view_attach_min').id,
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
            'context': {'create': 0, 'edit': 0}
        }

    def call_wizard_attach(self):
        """
        :return: Llama al wizard attach, usado para adjuntar imagenes
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'attachment.licencia.wizard',
            'target': 'new',
            'context': {'default_ing_form_general_id': self.id},
        }

    def call_wizard_correccion(self):
        """
        :return: Llama al wizard nota de correccion
        """
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'nota.correccion.licencia.wizard',
            'target': 'new',
            'context': {'default_ing_form_general_id': self.id},
        }

    def _get_datetime_create(self):
        _f_ini = fields.Datetime.from_string(self.create_date)
        for_mat = _f_ini.strftime('%d-%m-%Y')
        return for_mat

    def get_template_hs_sev(self):
        formview_ref = self.env.ref('ing_licencias.view_formgeneral_horas_sev_form').id
        treeview_ref = self.env.ref('ing_licencias.view_formgeneral_tree').id

        return {
            'name': "Horas Sev. - Consumo de HS",
            'view_mode': 'tree,form',
            'view_id': formview_ref,
            'view_type': 'form',
            'res_model': 'ing.licencias.general',
            'type': 'ir.actions.act_window',
            'views': [(treeview_ref, 'tree'), (formview_ref, 'form')],
            'context': {'default_tipo_lic_id': self._get_lic_horas_sev_id(), },
            'domain': [('tipo_lic_id', '=', self._get_lic_horas_sev_id())]}

    def get_template_licencia_franquicia(self):
        formview_ref = self.env.ref('ing_licencias.view_formgeneral_form').id
        treeview_ref = self.env.ref('ing_licencias.view_formgeneral_tree').id

        return {
            'name': "Licencias y Franquicias",
            'view_mode': 'tree,form',
            'view_id': formview_ref,
            'view_type': 'form',
            'res_model': 'ing.licencias.general',
            'type': 'ir.actions.act_window',
            'views': [(treeview_ref, 'tree'), (formview_ref, 'form')],
            'domain': [('tipo_lic_id', '!=', self._get_lic_horas_sev_id())]}

    @api.onchange('base_form_id')
    def onchange_empleado(self):
        if not self.env.context.get('default_tipo_lic_id'):
            operador = '!='
        else:
            operador = '='

        return {'domain': {'tipo_lic_id': [('id', operador,
                                            self._get_lic_horas_sev_id())]
                           }
                }

    def check_solicitud(self, compara):
        today = date.today()
        lic_uso_part = self.env.ref('ing_licencias.lic_uso_particular')
        _domain = [('tipo_lic_id', '=', lic_uso_part.id),
                   ('state', 'in', ['confirmada', 'revisar']),
                   ('base_form_id.employee_id', '=', self.base_form_id.employee_id.id)]

        if compara == 'anio':
            _domain.append(  ('fecha_inicio', '>=', f'{today.year}-01-01'),   )
            _domain.append(  ('fecha_inicio', '<=', f'{today.year}-12-31'),   )
        elif compara == 'mes':
            _mes = self.fecha_inicio.month
            _anio = today.year
            ult_dia_mes = monthrange(_anio, _mes)[1]
            _domain.append(('fecha_inicio', '>=', f'{_anio}-{_mes}-01'), )
            _domain.append(('fecha_inicio', '<=', f'{_anio}-{_mes}-{ult_dia_mes}'), )

        return self.search_count(_domain)

    @api.constrains('base_form_id')
    def _check_solicitud(self):
        if self.tipo_lic_id == self.env.ref('ing_licencias.lic_uso_particular') and self.base_form_id.employee_id and \
                not self.env.user.has_group('ing_licencias.group_ing_rrhh_licencias_admin_rrhh'):
            if self.check_solicitud('mes') >= 1 and self.check_solicitud('anio') >= 5:
                raise UserError(_("Ya solicito los Cinco dias correspondiente a este año."))
            elif self.fecha_inicio and self.check_solicitud('mes') and self.check_solicitud('mes') >= 1:
                raise UserError(_("Ya solicito el dia correspondiente a este mes"))
            elif self.fecha_inicio and self.check_solicitud('anio') >= 5:
                raise UserError(_("Ya solicito los Cinco dias correspondiente a este año."))

    @api.model
    def _generate_activity_by_date_reentry(self):
        today = date.today()
        lics = self.search([('tipo_lic_id','=',self.env.ref('ing_licencias.lic_no_remunerada').id),
                            ('state','=','confirmada')])
        l_aux = []
        for l in lics:
            if today <= l.fecha_reingreso <= today + timedelta(days=7):
                l_aux.append(l)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ref_channel = self.env.ref("ing_licencias.ing_channel_lic_no_remunerada")
        channel = f'''<a href="{base_url}/web#model=mail.channel&amp;id={ref_channel.id}" 
                              class="o_channel_redirect" data-oe-id="{ref_channel.id}" data-oe-model="mail.channel" 
                              target="_blank">#{ref_channel.name}</a>'''
        for lic in l_aux:
            body = f'''{channel} Aviso de Reingreso. Se le comunica que El/La Sr./Sra. <strong>
                       {lic.base_form_id.employee_id.name}</strong> tiene fecha de reingreso para el dia <strong>
                       {lic.fecha_reingreso.strftime("%d/%m/%Y")}</strong> conforme a la Lic. No Remunerada creada el
                       {lic.create_date.strftime("%d/%m/%Y")}'''
            self.env['mail.channel'].browse(ref_channel.id).message_post(attachment_ids=[], body=body, channel_ids=[],
                                                                         message_type='comment', partner_ids=[],
                                                                         subtype_xmlid='mail.mt_comment')
