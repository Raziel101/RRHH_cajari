# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
from datetime import date
from odoo.exceptions import Warning
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class plantilla_iasper(models.Model):
    _name = 'ing.seguros.planilla.iasper'
    _inherit = 'ing.seguros.planilla.art'
    _description = 'Denuncia de Accidente'

    # Datos del siniestro
    poliza_numero = fields.Char(string="Póliza N°", default="80357/12",required=True)
    siniestro_numero = fields.Char(string="Siniestro N°",required=True)
    querrellante_nombre = fields.Char(string="Querrellante Nombre")
    telefono_querrellante = fields.Char(string="Teléfono Denunciante")
    lugar_fecha = fields.Text(string="Lugar y Fecha")
    nota = fields.Text(string="Nota",default="Este formulario debe remitirse junto con el INFORME MÉDICO, inmediatamente de producido el siniestro.")

    # Datos del denunciante
    calle = fields.Char(string="Calle")
    numero = fields.Char(string="N°")
    localidad = fields.Char(string="Localidad")
    dpto = fields.Char(string="Dpto")
    email_querrellante = fields.Char(string="E-mail Querrellante")

    # Datos del asegurado
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True, domain='[("tipo_contrato_id","in",["Locación de Servicios","locacion de servicios"])]')
    #asegurado_nombre = fields.Char(string="Apellido y Nombre del Asegurado")
    asegurado_dni = fields.Char(string="DNI del Asegurado")
    asegurado_email = fields.Char(string="E-mail Asegurado")
    asegurado_calle = fields.Char(string="Calle Asegurado")
    asegurado_provincia = fields.Char(string="Provincia")
    asegurado_cp = fields.Char(string="C.P")
    asegurado_edad = fields.Integer('Edad', compute='_compute_asegurado_edad', store=False, required=True)
    asegurado_localidad = fields.Char(string="Localidad")
    asegurado_numero = fields.Char(string="N°")
    asegurado_piso = fields.Char(string="Piso")
    asegurado_dpto = fields.Char(string="Dpto")
    tarea_efectuada = fields.Char(string="Tarea que efectúa")

    # Datos del Beneficiario
    beneficiario_nombre = fields.Char(string="Apellido y Nombre del Beneficiario")
    cuenta_obra_social = fields.Boolean(string="¿Cuenta con Obra Social?")
    especificar_obra_social = fields.Char(string="Especificar")

    # Circunstancias del accidente
    dia = fields.Integer(string="Día")
    mes = fields.Integer(string="Mes")
    anio = fields.Integer(string="Año")
    hora = fields.Char(string="Hora")
    lugar_accidente = fields.Text(string="Lugar donde ocurrió")
    circunstancias = fields.Text(string="Circunstancias en que se produjo (explicar detalladamente)")
    actividad_accidentado = fields.Text(string="Actividad que efectuaba el accidentado en aquel momento")
    parte_cuerpo_lesionado = fields.Char(string="Parte del cuerpo lesionado")
    tipo_lesion = fields.Char(string="Tipo de lesión")
    medico_primera_atencion = fields.Char(string="Nombre del médico o establecimiento transitorio que prestó primeros auxilios")

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

    #Estado
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('save', 'Guardado'),
        ('done', 'Finalizado')
    ], string="Estado", default='draft')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """ Autocompletar los datos del asegurado al seleccionar un empleado """
        if self.employee_id:
            #self.asegurado_nombre = self.employee_id.name  # Nombre completo (Apellido, Nombre)
            self.asegurado_dni = self.employee_id.identification_id  # DNI
            self.asegurado_email = self.employee_id.work_email  # Email
            self.asegurado_calle = self.employee_id.domic_real #self.employee_id.address_home_id.street if self.employee_id.address_home_id else ''  # Calle
            self.asegurado_provincia = self.employee_id.address_home_id.state_id.name if self.employee_id.address_home_id and self.employee_id.address_home_id.state_id else ''  # Provincia
            self.asegurado_cp = self.employee_id.address_home_id.zip if self.employee_id.address_home_id else ''  # Código Postal
            self.asegurado_localidad = self.employee_id.address_home_id.city if self.employee_id.address_home_id else ''  # Localidad
            self.asegurado_numero = self.employee_id.address_home_id.street_number if hasattr(
                self.employee_id.address_home_id, 'street_number') else ''  # Número de calle
            self.asegurado_piso = self.employee_id.address_home_id.floor if hasattr(self.employee_id.address_home_id,
                                                                                    'floor') else ''  # Piso
            self.asegurado_dpto = self.employee_id.address_home_id.apartment if hasattr(
                self.employee_id.address_home_id, 'apartment') else ''  # Departamento
            self.tarea_efectuada = self.employee_id.job_title  # Tarea que efectúa

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
        """ Genera la URL para la impresión del reporte en formato HTML """
        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": f"/report/html/ing_seguros.planilla_iasper_template/{self.id}?context=%7B%22lang%22%3A%22es_ES%22%2C%22tz%22%3A%22America%2FBuenos_Aires%22%2C%22uid%22%3A274%2C%22allowed_company_ids%22%3A%5B1%5D%7D",
        }


    def name_get(self):
        return [(record.id, str(record.employee_id.name) + '-' + str(record.date_accident)) for record in self]



