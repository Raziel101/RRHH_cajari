# -*- coding: utf-8 -*-
from odoo import http
import logging
import base64
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.portal.controllers.portal import pager as portal_pager
_log = logging.getLogger(__name__)

_limit = 25

class ProxyController(http.Controller):
    @http.route('/my/personal-data', type='http', auth="user", website=True)
    def personal_data(self):
        return http.request.redirect('/my/account')

    @http.route(['/my/holidays', '/my/holidays/page/<int:page>', '/my/holiday/<int:_id>'], type='http', auth="user",
                website=True)
    def holidays(self, _id=False, page=1):
        pager = portal_pager(
            url="/my/holidays",
            total=self._get_holidays(http.request.env.user.get_employee().id),
            page=page,
            step=_limit
        )
        ctx = {
            'session_info': http.request.env['ir.http'].session_info(),
            'employee': http.request.env.user.get_employee(),
            'page_name': 'my_holidays',
            'pager': pager,
        }
        if _id:
            ctx['holiday'] = http.request.env['ing.ausencias.ausencias'].sudo().browse(_id)
        else:
            ctx['holidays'] = http.request.env['ing.ausencias.ausencias'].sudo().search([
                ('employee_id', '=', http.request.env.user.get_employee().id)
            ], offset=pager['offset'], limit=_limit)
        return http.request.render(f'ing_employee_portal.{"holiday" if _id else "holidays"}', ctx)

    @http.route(['/my/advances', '/my/advances/page/<int:page>', '/my/advance/<int:_id>'], type='http', auth="user",
                website=True)
    def advances(self, _id=False, page=1):
        pager = portal_pager(
            url="/my/advances",
            total=self._get_advances(http.request.env.user.get_employee().id),
            page=page,
            step=_limit
        )
        ctx = {
            'session_info': http.request.env['ir.http'].session_info(),
            'employee': http.request.env.user.get_employee(),
            'page_name': 'my_advances',
            'pager': pager,
        }
        if _id:
            ctx['advance'] = http.request.env['ing.rrhh.solicitudes.solicitud'].sudo().browse(_id)
        else:
            ctx['advances'] = http.request.env['ing.rrhh.solicitudes.solicitud'].sudo().search([
                ('employee_id', '=', http.request.env.user.get_employee().id)
            ], offset=pager['offset'], limit=_limit)
        return http.request.render(f'ing_employee_portal.{"advance" if _id else "advances"}', ctx)

    @http.route(['/my/advance/new', '/my/advance/create'], type='http', auth="public", website=True,
                methods=['GET', 'POST'], csrf=False)
    def advance_new(self, **kw):
        _session = http.request.env['ir.http'].session_info()
        def get_last_day_skilled(_today, _day: int):
            _today = datetime(_today.year, _today.month, _day)
            _w_day = _today.weekday()
            while _w_day >= 5:
                _w_day -= 1
                _day -= 1
            return _day

        if kw:
            amount_max = http.request.env['ir.config_parameter'].sudo().get_param('amount_max_advances')
            _amount = kw.get('amount')
            _today = datetime.today()
            last_day_skilled = get_last_day_skilled(_today, 20) - 1
            ctx_render = {'session_info': _session, 'a_href': '/my/advance/new', 'a_name': 'Volver'}

            if float(_amount) > float(amount_max):
                ctx_render.update({'message': f'El monto maximo es de {http.request.env.company.currency_id.symbol}{amount_max}'})
                return http.request.render("ing_employee_portal.error_template", ctx_render)
            elif _today.hour >= 10 if _today.day == last_day_skilled else _today.day > last_day_skilled:
                ctx_render.update({'message': f'Solo se pueden solicitar adelantos hasta el dia {last_day_skilled} a las 10:00 hs.'})
                return http.request.render("ing_employee_portal.error_template", ctx_render)

            advance_id = http.request.env['ing.rrhh.solicitudes.solicitud'].sudo().create({
                'employee_id': int(kw.get('employee_id')),
                'monto': _amount,
                'fecha_emision': date(year=_today.year, month=_today.month, day=20),
                'state': 'create_portal',
            })
            return http.request.redirect(f'/my/advance/{advance_id.id}')
        else:
            return http.request.render("ing_employee_portal.advance_new", {
                'session_info': _session,
            })

    @http.route(['/my/subsidies', '/my/subsidies/page/<int:page>', '/my/subsidy/<int:_id>'], type='http', auth="user",
                website=True)
    def subsidies(self, _id=False, page=1):
        pager = portal_pager(
            url="/my/subsidies",
            total=self._get_subsidies(http.request.env.user.get_employee().id),
            page=page,
            step=_limit
        )
        ctx = {
            'session_info': http.request.env['ir.http'].session_info(),
            'employee': http.request.env.user.get_employee(),
            'page_name': 'my_subsidies',
            'pager': pager,
        }
        if _id:
            ctx['subsidy'] = http.request.env['ing.rrhh.solicitudes.subsidy'].sudo().browse(_id)
        else:
            ctx['subsidies'] = http.request.env['ing.rrhh.solicitudes.subsidy'].sudo().search([
                ('employee_id', '=', http.request.env.user.get_employee().id)
            ], offset=pager['offset'], limit=_limit)
        return http.request.render(f'ing_employee_portal.{"subsidy" if _id else "subsidies"}', ctx)

    @http.route(['/my/licenses', '/my/licenses/page/<int:page>', '/my/license/<int:_id>'], type='http', auth="user",
                website=True)
    def licenses(self, _id=False, page=1):
        pager = portal_pager(
            url="/my/licenses",
            total=self._get_licenses(http.request.env.user.get_employee().id),
            page=page,
            step=_limit
        )
        ctx = {
            'session_info': http.request.env['ir.http'].session_info(),
            'employee': http.request.env.user.get_employee(),
            'page_name': 'my_licenses',
            'pager': pager,
        }
        if _id:
            ctx['license'] = http.request.env['ing.licencias.general'].sudo().browse(_id)
        else:
            ctx['licenses'] = http.request.env['ing.licencias.general'].sudo().search([
                ('base_form_id.employee_id', '=', http.request.env.user.get_employee().id),
                ('tipo_lic_id', '!=', http.request.env.ref('ing_licencias.lic_hs_sev_franco').id)
            ], offset=pager['offset'], limit=_limit)
        return http.request.render(f'ing_employee_portal.{"license" if _id else "licenses"}', ctx)

    @http.route(['/my/license/new', '/my/license/create'], type='http', auth="public", website=True,
                methods=['GET', 'POST'], csrf=False)
    def license_new(self, **kw):
        _session = http.request.env['ir.http'].session_info()
        base_form = http.request.env['ing.licencias.base'].sudo()
        _lic_general = http.request.env['ing.licencias.general'].sudo()
        if kw:
            ctx_render = {'session_info': _session, 'a_href': '/my/license/new', 'a_name': 'Volver'}
            base_form_id = base_form.search([('employee_id', '=', int(kw.get('employee_id')))], limit=1)
            if not base_form_id:
                ctx_render.update({'message': 'Usted no puede solicitar Licencias.'})
                return http.request.render("ing_employee_portal.error_template", ctx_render)
            _emp_id = base_form_id.employee_id
            _vals = {
                'base_form_id': base_form_id.id,
                'state': 'create_portal',
                'ing_medio_aviso_id': http.request.env.ref('ing_employee_portal.medio_aviso_default').id,
                'departament_id': _emp_id.department_id.id,
                'tipo_lic_id': http.request.env['ing.licencias.tipo'].sudo().search([('name', '=', kw.get("type_lic"))], limit=1).id,
            }

            if kw.get('type_lic') == 'nac_hijo':
                _date_init = datetime.strptime(kw.get('date_init'), '%Y-%m-%d')
                _date_nac = datetime.strptime(kw.get('date_nac'), '%Y-%m-%d')
                date_limit = _date_nac + relativedelta(days=15)
                if _emp_id.gender != 'male' or _date_init > date_limit:
                    ctx_render.update({
                        'message': '''  Este tipo de licencia es solo para agentes varones y la fecha de inicio no 
                                        puede ser luego de los 15 dias de la fecha de nacimiento.'''
                    })
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                else:
                    _attach_id = self._create_attach(kw.get('attach'))
                    _vals.update({'fecha_inicio': _date_init.date(), 'attach_ids': [(4, _attach_id.id)]})
            elif kw.get('type_lic') == 'lic_evento_deportivo_nrentado':
                _date_event = datetime.strptime(kw.get('date_event'), '%Y-%m-%d')
                if date.today() > (_date_event - relativedelta(days=7)).date():
                    ctx_render.update({'message': 'Este tipo de licencia debe ser cargada 7 dias antes del evento.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                else:
                    _attach_id = self._create_attach(kw.get('attach'))
                    _vals.update({'attach_ids': [(4, _attach_id.id)]})
            elif kw.get('type_lic') == 'lic_matrimonio':
                if date.today() > datetime.strptime(kw.get('date_marriage'), '%Y-%m-%d').date():
                    ctx_render.update({'message': 'Este tipo de licencia debe ser cargada antes de la fecha de matrimonio.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
            elif kw.get('type_lic') == 'lic_razon_salud':
                _attach_id = self._create_attach(kw.get('attach'))
                _vals.update({'attach_ids': [(4, _attach_id.id)]})
            elif kw.get('type_lic') == 'lic_fallecimiento_fam':
                if date.today() < datetime.strptime(kw.get('date_death'), '%Y-%m-%d').date():
                    ctx_render.update({'message': 'La fecha de Fallecimiento no puede ser posterior al dia de hoy.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                _attach_id = self._create_attach(kw.get('attach'))
                _vals.update({'fecha_inicio': kw.get('date_death'), 'attach_ids': [(4, _attach_id.id)]})
            elif kw.get('type_lic') in ['lic_examen', 'lic_razones_gremiales', 'lic_enf_acc_familiar_acargo', 'lic_capacitacion']:
                _attach_id = self._create_attach(kw.get('attach'))
                _vals.update({'fecha_inicio': kw.get('date_init'), 'attach_ids': [(4, _attach_id.id)]})
            elif kw.get('type_lic') == 'lic_matrimonio_dehijos':
                _vals.update({'fecha_inicio': kw.get('date_init')})
            elif kw.get('type_lic') == 'lic_adopcion':
                if int(kw.get('age')) > 2:
                    ctx_render.update({'message': 'La edad del menor no puede ser mayor a 2 años.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                _attach_id = self._create_attach(kw.get('attach'))
                _vals.update({'fecha_inicio': kw.get('date_resolution'), 'attach_ids': [(4, _attach_id.id)]})
            elif kw.get('type_lic') == 'lic_maternidad':
                _date_init = datetime.strptime(kw.get('date_init'), '%Y-%m-%d').date()
                _date_birth = datetime.strptime(kw.get('date_birth'), '%Y-%m-%d').date()
                if date.today() > _date_init:
                    ctx_render.update({'message': 'La fecha de inicio debe ser posterior al dia de hoy.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                if (_date_birth - _date_init).days < 20:
                    ctx_render.update({'message': 'La fecha de inicio debe ser 20 días antes de la fecha probable de parto.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                _attach_id = self._create_attach(kw.get('attach'))
                _vals.update({'fecha_inicio': kw.get('date_init'), 'attach_ids': [(4, _attach_id.id)]})
            elif kw.get('type_lic') == 'lic_uso_particular':
                _date_request = datetime.strptime(kw.get('date_init'), '%Y-%m-%d')
                lics = _lic_general.search([('base_form_id', '=', base_form_id.id),
                                            ('state', '!=', 'cancelada'),
                                            ('fecha_inicio', '>=', datetime.strptime(f'{_date_request.year}-01-01', '%Y-%m-%d').date()),
                                            ('fecha_inicio', '<=', datetime.strptime(f'{_date_request.year}-12-31', '%Y-%m-%d').date()),
                                            ('tipo_lic_id', '=', http.request.env.ref('ing_licencias.lic_uso_particular').id)])
                if date.today() > _date_request.date():
                    ctx_render.update({'message': 'Este tipo de licencia no puede ser cargada con fecha de inicio anterior a hoy.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                elif len(lics) >= 5:
                    ctx_render.update({'message': 'Este tipo de licencia se puede solicitar solo 5 veces en el año.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                elif lics.filtered(lambda x: x.fecha_inicio.month == _date_request.month):
                    ctx_render.update({'message': 'Este tipo de licencia se puede solicitar solo 1 vez en el mes.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                else:
                    _vals.update({'fecha_inicio': _date_request.date()})
            elif kw.get('type_lic') == 'lic_vacaciones':
                _date_init = datetime.strptime(kw.get('date_init'), '%Y-%m-%d')
                _days_requested = kw.get('days_requested') or 0
                _days_available = _lic_general.get_sum_days_available(_emp_id.id)
                if date.today() > (_date_init - relativedelta(days=7)).date():
                    ctx_render.update({'message': 'Este tipo de licencia debe ser cargada 7 dias antes de la fecha de inicio.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                elif _days_requested == 0:
                    ctx_render.update({'message': 'No tiene dias disponibles para solicitar.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                elif float(_days_requested) > float(_days_available):
                    ctx_render.update({'message': f'Tiene disponibles {_days_available} dias para solicitar.'})
                    return http.request.render("ing_employee_portal.error_template", ctx_render)
                period = http.request.env['ing.licencias.periodo'].sudo()
                day_period = http.request.env['ing.licencias.dia.periodo'].sudo()
                _period = period.search([('name', '=', str(date.today().year))])
                _day_period = [day_period.create(_v) for _v in self._get_day_period(_emp_id.id)]
                _vals.update({'dia_periodo_lic_ids': [(4, _d_p.id) for _d_p in _day_period],
                              'dias_solicitados': int(_days_requested),
                              'fecha_inicio': kw.get('date_init')})

            license_id = _lic_general.create(_vals)
            _lic_general.create_message_new_rec_from_portal(license_id)
            return http.request.redirect(f'/my/license/{license_id.id}')
        else:
            return http.request.render("ing_employee_portal.license_new", {
                'session_info': _session,
                'days_available': _lic_general.get_sum_days_available(http.request.env.user.get_employee().id),
                'list_type_lic': [{'name': rec.name, 'det': rec.detalle} for rec in http.request.env['ing.licencias.tipo'].sudo().search([('view_in_portal', '=', True)])],
            })

    @http.route(['/my/hours', '/my/hours/page/<int:page>', '/my/hour/<int:_id>'], type='http', auth="user",
                website=True)
    def hours(self, _id=False, page=1):
        emp = http.request.env.user.get_employee()
        pager = portal_pager(
            url="/my/hours",
            total=self._get_hours(emp.id),
            page=page,
            step=_limit
        )
        ctx = {
            'session_info': http.request.env['ir.http'].session_info(),
            'employee': emp,
            'page_name': 'my_hours',
            'pager': pager,
            'available_hours':  emp.check_availability_hours_sev(emp.id),
        }
        if _id:
            ctx['hour'] = http.request.env['ing.licencias.general'].sudo().browse(_id)
        else:
            ctx['hours'] = http.request.env['ing.licencias.general'].sudo().search([
                ('base_form_id.employee_id', '=', emp.id),
                ('tipo_lic_id', '=', http.request.env.ref('ing_licencias.lic_hs_sev_franco').id)
            ], offset=pager['offset'], limit=_limit)
        return http.request.render(f'ing_employee_portal.{"hour" if _id else "hours"}', ctx)

    @http.route(['/my/scales', '/my/scales/page/<int:page>', '/my/scale/<int:_id>'], type='http', auth="user",
                website=True)
    def scales(self, _id=False, page=1):
        pager = portal_pager(
            url="/my/scales",
            total=self._get_scales(),
            page=page,
            step=_limit
        )
        ctx = {
            'session_info': http.request.env['ir.http'].session_info(),
            'employee': http.request.env.user.get_employee(),
            'page_name': 'my_scales',
            'pager': pager,
        }
        if _id:
            ctx['scale'] = http.request.env['ing.procedure'].sudo().browse(_id)
        else:
            ctx['scales'] = http.request.env['ing.procedure'].sudo().search([
                ('area_id', '=', http.request.env.ref('ing_employee_portal.area_wages').id)
            ], offset=pager['offset'], limit=_limit)
        return http.request.render(f'ing_employee_portal.{"scale" if _id else "scales"}', ctx)

    @http.route(['/my/guides', '/my/guides/page/<int:page>', '/my/guide/<int:_id>'], type='http', auth="user",
                website=True)
    def guides(self, _id=False, page=1):
        pager = portal_pager(
            url="/my/guides",
            total=self._get_guides(),
            page=page,
            step=_limit
        )
        ctx = {
            'session_info': http.request.env['ir.http'].session_info(),
            'employee': http.request.env.user.get_employee(),
            'page_name': 'my_guides',
            'pager': pager,
        }
        if _id:
            ctx['guide'] = http.request.env['ing.procedure'].sudo().browse(_id)
        else:
            ctx['guides'] = http.request.env['ing.procedure'].sudo().search([
                ('area_id', '=', http.request.env.ref('ing_employee_portal.area_staff').id)
            ], offset=pager['offset'], limit=_limit)
        return http.request.render(f'ing_employee_portal.{"guide" if _id else "guides"}', ctx)

    def _get_holidays(self, employee_id):
        return http.request.env['ing.ausencias.ausencias'].sudo().search_count([
                ('employee_id', '=', employee_id)
            ])
    def _get_advances(self, employee_id):
        return http.request.env['ing.rrhh.solicitudes.solicitud'].sudo().search_count([
                ('employee_id', '=', employee_id)
            ])
    def _get_subsidies(self, employee_id):
        return http.request.env['ing.rrhh.solicitudes.subsidy'].sudo().search_count([
                ('employee_id', '=', employee_id)
            ])
    def _get_licenses(self, employee_id):
        return http.request.env['ing.licencias.general'].sudo().search_count([
                ('base_form_id.employee_id', '=', employee_id),
                ('tipo_lic_id', '!=', http.request.env.ref('ing_licencias.lic_hs_sev_franco').id)
            ])
    def _get_hours(self, employee_id):
        return http.request.env['ing.licencias.general'].sudo().search_count([
                ('base_form_id.employee_id', '=', employee_id),
                ('tipo_lic_id', '=', http.request.env.ref('ing_licencias.lic_hs_sev_franco').id)
            ])
    def _get_guides(self):
        return http.request.env['ing.procedure'].sudo().search_count([
                ('area_id', '=', http.request.env.ref('ing_employee_portal.area_staff').id)
            ])
    def _get_scales(self):
        return http.request.env['ing.procedure'].sudo().search_count([
                ('area_id', '=', http.request.env.ref('ing_employee_portal.area_wages').id)
            ])
    def _prepare_portal_layout_values(self):
        sales_user = False
        employee = http.request.env.user.get_employee()
        if not employee:
            return http.request.render("ing_employee_portal.error_template", {
                'session_info': http.request.env['ir.http'].session_info(),
                'message': 'No se encontro empleado.',
            })
        elif employee.user_id and not employee.user_id._is_public():
            sales_user = employee.user_id

        return {
            'sales_user': sales_user,
            'page_name': 'home',
            'holidays_count': self._get_holidays(employee.id),
            'advances_count': self._get_advances(employee.id),
            'subsidies_count': self._get_subsidies(employee.id),
            'licenses_count': self._get_licenses(employee.id),
            'hours_count': self._get_hours(employee.id),
            'guides_count': self._get_guides(),
            'scales_count': self._get_scales(),
        }

    def _create_attach(self, file):
        return http.request.env['ir.attachment'].sudo().create({
            'name': file.filename,
            'store_fname': file.filename,
            'datas': base64.b64encode(file.read()),
            'mimetype': file.mimetype,
            'res_model': 'ing.licencias.general',
            'type': 'binary',
        })

    def _get_day_period(self, emp_id):
        list_periodo = []
        env_vacaciones = http.request.env['ing.alta.baja.licencia'].sudo()
        get_search = env_vacaciones.search_read([('employee_id', '=', emp_id)],
                                                ['periodo', 'dias'], order='periodo asc')
        # Genera la lista de periodos
        [list_periodo.append(x.get('periodo')) for x in get_search if x.get('periodo') not in list_periodo]
        dic_suma = []
        env_periodo = http.request.env['ing.licencias.periodo'].sudo()
        for l in list_periodo:
            periodo = env_periodo.search([('name', '=', l)])
            search_vac = env_vacaciones.search(
                [('employee_id', '=', emp_id), ('periodo', '=', l)])

            dias_disponibles = sum(map(lambda d: d.dias, search_vac))

            if dias_disponibles > 0:
                if not periodo:
                    p_riodo = env_periodo.create({'name': l})
                    dic_suma.append({'periodo_lic_id': p_riodo.id, 'dias': dias_disponibles})
                else:
                    dic_suma.append({'periodo_lic_id': periodo.id, 'dias': dias_disponibles})
        return dic_suma

    MANDATORY_BILLING_FIELDS = []
    OPTIONAL_BILLING_FIELDS = ["domic_real", "domic_legal", "work_email", "work_phone"]

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        employee = http.request.env.user.get_employee()
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and http.request.httprequest.method == 'POST':
            values.update(post)
            values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
            values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
            employee.sudo().write(values)
            if redirect:
                return http.request.redirect(redirect)
            return http.request.redirect('/my/home')

        values.update({
            'employee': employee,
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = http.request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        emp = http.request.env.user.get_employee()
        con_ids = [http.request.env.ref('ing_ausencias.planta_temporaria').id,
                   http.request.env.ref('ing_ausencias.planta_permanente').id]
        if not emp:
            return http.request.redirect('/web/login')
        elif emp.tipo_contrato_id.id not in con_ids:
            return http.request.render("ing_employee_portal.error_template", {
                'session_info': http.request.env['ir.http'].session_info(),
                'message': 'Solo se permite el acceso a empleados de Planta.',
            })
        return http.request.render("portal.portal_my_home", values)

