# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from datetime import date
from odoo.exceptions import Warning
from dateutil.relativedelta import relativedelta
import logging
import base64
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class plantilla_iasper(models.Model):
    _name = 'ing.seguros.planilla.iasper'
    _description = 'Denuncia de Accidente'
    _order = 'fecha_creacion desc'

    # Datos del siniestro
    poliza_numero = fields.Char(string="Póliza N°", default="80357/12",required=True)
    siniestro_numero = fields.Char(string="Siniestro N°")
    nota = fields.Text(string="Nota",default="Este formulario debe remitirse junto con el INFORME MÉDICO, inmediatamente de producido el siniestro.")


    # Datos del denunciante
    tomador_nombre = fields.Char(string="Denunciante Nombre", default=lambda self: self._get_company_value('name'))
    tomador_telefono = fields.Char(string="Teléfono Denunciante", default=lambda self: self._get_company_value('phone'))
    tomador_domicilio = fields.Text(string="Domicilio Denunciante", default=lambda self: self._get_company_address())
    tomador_calle = fields.Char(string="Calle", default=lambda self: self._get_company_value('street'))
    tomador_numero = fields.Char(string="N°", default=lambda self: self._get_company_value('street2'))
    tomador_localidad = fields.Char(string="Localidad Denunciante", default=lambda self: self._get_company_value('city'))
    tomador_dpto = fields.Char(string="Dpto", default="Federación")
    tomador_email = fields.Char(string="E-mail Denunciante", default=lambda self: self._get_company_value('email'))


    # Datos del asegurado
    employee_id = fields.Many2one('hr.employee', string='Nombre Asegurado', required=True, domain='[("tipo_contrato_id","in",["Locación de Servicios","locacion de servicios"])]')
    asegurado_dni = fields.Char(string="DNI del Asegurado")
    asegurado_email = fields.Char(string="E-mail Asegurado")
    asegurado_calle = fields.Char(string="Calle Asegurado")
    asegurado_provincia = fields.Char(string="Provincia")
    asegurado_cp = fields.Char(string="C.P", required=True)
    asegurado_edad = fields.Integer('Edad', compute='_compute_asegurado_edad', store=False, required=True)
    asegurado_localidad = fields.Char(string="Localidad Asegurado", required=True)
    asegurado_numero = fields.Char(string="N°")
    asegurado_piso = fields.Char(string="Piso")
    asegurado_dpto = fields.Char(string="Dpto")
    tarea_efectuada = fields.Char(string="Tarea que efectúa")

    # Datos del Beneficiario
    beneficiario_nombre = fields.Char(string="Apellido y Nombre del Beneficiario")
    cuenta_obra_social = fields.Boolean(string="¿Cuenta con Obra Social?")
    especificar_obra_social = fields.Char(string="Especificar")

    # Circunstancias del accidente
    dia = fields.Integer(string="Día", required=True)
    mes = fields.Integer(string="Mes", required=True)
    anio = fields.Integer(string="Año", required=True)
    hora = fields.Char(string="Hora", required=True)
    lugar_accidente = fields.Char(string="Lugar donde ocurrió", required=True, size=40)
    circunstancias = fields.Text(string="Circunstancias en que se produjo (explicar detalladamente)", required=True )
    actividad_accidentado = fields.Char(string="Actividad que efectuaba el accidentado en aquel momento", required=True, size=40)
    tipo_lesion = fields.Selection([('escoriaciones','Escoriaciones'),
                                    ('heridas punzantes','Heridas punzantes'),
                                    ('heridas cortantes','Heridas cortantes'),
                                    ('heridas de bala','Heridas de bala'),
                                    ('contusiones','Contusiones'),
                                    ('torceduras','Torceduras'),
                                    ('luxaciones','Luxaciones'),
                                    ('fracturas cerradas','Fracturas cerradas'),
                                    ('amputaciones','Amputaciones'),
                                    ('quemaduras','Quemaduras'),
                                    ('cuerpo extraño en ojos','Cuerpo extraño en ojos'),
                                    ('esguinces','Esguinces'),
                                    ('fracturas expuestas','Fracturas expuestas'),
                                    ('perdida auditiva','Perdida auditiva'),
                                    ('efectos de cuerpo extraño en oído','Efectos de cuerpo extraño en oído'),
                                    ('efectos de cuerpo extraño en nariz','Efectos de cuerpo extraño en nariz'),
                                    ('efectos por picaduras','Efectos por picaduras'),
                                    ('desgarro','Desgarro')], required=True, string="Tipo de Lesión")
    tipo_lesion2 = fields.Selection([('escoriaciones','Escoriaciones'),
                                    ('heridas punzantes','Heridas punzantes'),
                                    ('heridas cortantes','Heridas cortantes'),
                                    ('heridas de bala','Heridas de bala'),
                                    ('contusiones','Contusiones'),
                                    ('torceduras','Torceduras'),
                                    ('luxaciones','Luxaciones'),
                                    ('fracturas cerradas','Fracturas cerradas'),
                                    ('amputaciones','Amputaciones'),
                                    ('quemaduras','Quemaduras'),
                                    ('cuerpo extraño en ojos','Cuerpo extraño en ojos'),
                                    ('esguinces','Esguinces'),
                                    ('fracturas expuestas','Fracturas expuestas'),
                                    ('perdida auditiva','Perdida auditiva'),
                                    ('efectos de cuerpo extraño en oído','Efectos de cuerpo extraño en oído'),
                                    ('efectos de cuerpo extraño en nariz','Efectos de cuerpo extraño en nariz'),
                                    ('efectos por picaduras','Efectos por picaduras'),
                                    ('desgarro','Desgarro')], string="Tipo de Lesión")
    parte_cuerpo_lesionado = fields.Selection([('Región craneana', 'Región craneana'),
                                    ('Ojos', 'Ojos'),
                                    ('Oído', 'Oído'),
                                    ('Boca', 'Boca'),
                                    ('Nariz', 'Nariz'),
                                    ('Cara', 'Cara'),
                                    ('Cabeza, ubicaciones múltiples', 'Cabeza, ubicaciones múltiples'),
                                    ('Región cervical', 'Región cervical'),
                                    ('Tórax', 'Tórax'),
                                    ('Pelvis', 'Pelvis'),
                                    ('Hombro', 'Hombro'),
                                    ('Brazo', 'Brazo'),
                                    ('Codo', 'Codo'),
                                    ('Antebrazo', 'Antebrazo'),
                                    ('Muñeca', 'Muñeca'),
                                    ('Mano', 'Mano'),
                                    ('Dedos de la mano', 'Dedos de la mano'),
                                    ('Cadera', 'Cadera'),
                                    ('Muslo', 'Muslo'),
                                    ('Rodilla', 'Rodilla'),
                                    ('Pierna', 'Pierna'),
                                    ('Tobillo', 'Tobillo'),
                                    ('Pie', 'Pie'),
                                    ('Dedos de los pies', 'Dedos de los pies'),
                                    ('Testículos', 'Testículos'),
                                    ('Tronco, ubicaciones múltiples', 'Tronco, ubicaciones múltiples'),
                                    ('Ubicaciones múltiples', 'Ubicaciones múltiples'),
                                    ('Cabeza y Cuello', 'Cabeza y Cuello'),
                                    ('Miembros superiores', 'Miembros superiores'),
                                    ('Miembros inferiores', 'Miembros inferiores')], required=True, string="Parte del cuerpo lesionado")
    parte_cuerpo_lesionado2 = fields.Selection([('Región craneana', 'Región craneana'),
                                    ('Ojos', 'Ojos'),
                                    ('Oído', 'Oído'),
                                    ('Boca', 'Boca'),
                                    ('Nariz', 'Nariz'),
                                    ('Cara', 'Cara'),
                                    ('Cabeza, ubicaciones múltiples', 'Cabeza, ubicaciones múltiples'),
                                    ('Región cervical', 'Región cervical'),
                                    ('Tórax', 'Tórax'),
                                    ('Pelvis', 'Pelvis'),
                                    ('Hombro', 'Hombro'),
                                    ('Brazo', 'Brazo'),
                                    ('Codo', 'Codo'),
                                    ('Antebrazo', 'Antebrazo'),
                                    ('Muñeca', 'Muñeca'),
                                    ('Mano', 'Mano'),
                                    ('Dedos de la mano', 'Dedos de la mano'),
                                    ('Cadera', 'Cadera'),
                                    ('Muslo', 'Muslo'),
                                    ('Rodilla', 'Rodilla'),
                                    ('Pierna', 'Pierna'),
                                    ('Tobillo', 'Tobillo'),
                                    ('Pie', 'Pie'),
                                    ('Dedos de los pies', 'Dedos de los pies'),
                                    ('Testículos', 'Testículos'),
                                    ('Tronco, ubicaciones múltiples', 'Tronco, ubicaciones múltiples'),
                                    ('Ubicaciones múltiples', 'Ubicaciones múltiples'),
                                    ('Cabeza y Cuello', 'Cabeza y Cuello'),
                                    ('Miembros superiores', 'Miembros superiores'),
                                    ('Miembros inferiores', 'Miembros inferiores')], string="Parte del cuerpo lesionado")
    medico_primera_atencion = fields.Char(string="Nombe del médico o establecimiento transitorio que prestó primeros auxilios")

    # Testigos y denuncia
    hubo_testigos = fields.Boolean(string="¿Hubo testigos del accidente?")
    nombres_testigos = fields.Text(string="Nombres y Apellidos testigos")
    domicilios_testigos = fields.Text(string="Domicilios testigo")
    sumario_policial = fields.Boolean(string="¿Se instruyó sumario policial?")
    autoridad = fields.Char(string="¿A qué autoridad fue elevado? (si es juez indíquese también Secretaría)")

    # Datos del denunciante
    tipo_denunciante = fields.Selection([
        ('empleador', 'Empleador'),
        ('representante', 'Representantes Legales'),
        ('beneficiario', 'Beneficiarios'),
        ('otro', 'Otro')
    ], string="¿Quién es el denunciante?")

    denunciante_nombre = fields.Char(string="Apellido y Nombre denunciante")
    denunciante_domicilio = fields.Char(string="Domicilio del Denunciante")

    denunciante_telefono_fondo = fields.Char(String="Telefono del Denunciante", required=True)

    #Estado
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('save', 'Guardado'),
        ('done', 'Finalizado')
    ], string="Estado", default='draft')

    # Fecha de creación automática
    fecha_creacion = fields.Datetime(
        string="Fecha de creación",
        default=fields.Datetime.now,
        readonly=True
    )

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """ Autocompletar los datos del asegurado al seleccionar un empleado """
        if self.employee_id:
            #self.asegurado_nombre = self.employee_id.name  # Nombre completo (Apellido, Nombre)
            self.asegurado_dni = self.employee_id.identification_id  # DNI
            self.asegurado_email = self.employee_id.work_email  # Email
            self.asegurado_calle = self.employee_id.domic_real #self.employee_id.address_home_id.street if self.employee_id.address_home_id else ''  # Calle
            self.asegurado_provincia = self.employee_id.address_home_id.state_id.name if self.employee_id.address_home_id and self.employee_id.address_home_id.state_id else 'Entre Ríos (AR)'  # Provincia
            self.asegurado_cp = self.employee_id.address_home_id.zip if self.employee_id.address_home_id else ''  # Código Postal
            self.asegurado_localidad = self.employee_id.address_home_id.city if self.employee_id.address_home_id else ''  # Localidad
            self.asegurado_numero = self.employee_id.address_home_id.street_number if hasattr(
                self.employee_id.address_home_id, 'street_number') else ''  # Número de calle
            self.asegurado_piso = self.employee_id.address_home_id.floor if hasattr(self.employee_id.address_home_id,
                                                                                    'floor') else ''  # Piso
            self.asegurado_dpto = self.employee_id.address_home_id.apartment if hasattr(
                self.employee_id.address_home_id, 'apartment') else 'Federación'  # Departamento
            self.tarea_efectuada = self.employee_id.job_title_for  # Tarea que efectúa

    @api.depends('employee_id', 'employee_id.birthday')
    def _compute_asegurado_edad(self):
        """ Calcular la edad basada en la fecha de nacimiento del empleado """
        today = date.today()
        for record in self:
            if record.employee_id and record.employee_id.birthday:
                birth_date = record.employee_id.birthday
                record.asegurado_edad = today.year - birth_date.year - (
                        (today.month, today.day) < (birth_date.month, birth_date.day)
                )
            else:
                record.asegurado_edad = 0

    @api.model
    def create(self, vals):
        """ Establece el estado en 'save' al crear un registro """
        vals['state'] = 'save'
        return super(plantilla_iasper, self).create(vals)


    def print_planilla(self):
        return self.env.ref('ing_seguros.inf_planilla_iasper_report').report_action(self, config=False)

    def _set_paper_format(self):
        """ Forzar el formato de papel a A4 sin márgenes para evitar desalineación en PDF """
        report_sudo = self.env['ir.actions.report'].sudo().search([
            ('report_name', '=', 'ing_seguros.planilla_iasper_template')
        ], limit=1)
        if report_sudo:
            report_sudo.write({'paperformat_id': self.env.ref('base.paperformat_euro').id})

    def _get_report_base_filename(self):
        return "Informe_Planilla_IASPER"


    def name_get(self):
        return [(record.id, str(record.employee_id.name)) for record in self]

    @api.model
    def _get_company_value(self, field_name):
        """ Obtener valores de la compañía actual """
        company = self.env.company
        return getattr(company, field_name, '') if company else ''

    @api.model
    def _get_company_address(self):
        """ Construir dirección completa de la compañía """
        company = self.env.company
        address_parts = filter(None, [company.street, company.street2])
        return " ".join(address_parts) if company else ''

    @api.onchange('company_id')
    def _onchange_company_id(self):
        """ Si cambia la compañía, actualizar los datos del denunciante """
        for record in self:
            record.tomador_nombre = self._get_company_value('name')
            record.tomador_telefono = self._get_company_value('phone')
            record.tomador_domicilio = self._get_company_address()
            record.tomador_calle = self._get_company_value('street')
            record.tomador_numero = self._get_company_value('street2')
            record.tomador_localidad = self._get_company_value('city')
            record.tomador_dpto = self._get_company_value('company_registry')#state_id.name
            record.tomador_email = self._get_company_value('email')

    imagen_fondo = fields.Binary(compute="_get_imagen_fondo", store=False)

    def _get_imagen_fondo(self):
        for record in self:
            ruta = get_module_resource('ing_seguros', 'static/src/pdf', 'Formulario-de-Denuncia.png')
            try:
                with open(ruta, 'rb') as f:
                    record.imagen_fondo = base64.b64encode(f.read())
            except FileNotFoundError:
                record.imagen_fondo = False

    """def _get_imagen_fondo(self):
        for record in self:
            with open('/server/odoo/addons/ing_seguros/static/src/pdf/Formulario-de-Denuncia.png', 'rb') as f:
                record.imagen_fondo = base64.b64encode(f.read())"""
