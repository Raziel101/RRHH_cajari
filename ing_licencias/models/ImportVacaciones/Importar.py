# -*- coding: utf-8 -*-
from odoo import api, fields, models
import xlrd
import base64
import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class Importar(models.Model):
    _name = 'ing.importar.vacaciones'
    _inherit = 'mail.thread'
    _order = "create_date desc"
    _rec_name = 'fecha_importacion'
    _description = "Importar vacaciones"

    # Atributos
    fecha_importacion = fields.Date(string="Fecha", default=fields.Datetime.now, readonly=1)
    periodo = fields.Char(string="Periodo", required=True, size=4)
    txt_error = fields.Text(string="Errores en los siguientes DNI, ")

    # Relaciones
    xls_vacaciones_ids = fields.Many2many(comodel_name='ir.attachment', string=u"Importar")

    # Funciones
    def procesar_excel_vacaciones(self):
        if len(self.xls_vacaciones_ids) > 1:
            # Solo puede haber un archivo a la hora de procesar.
            raise UserError("Solo puede haber un archivo para procesar")
        if len(self.xls_vacaciones_ids) < 1:
            # Solo puede haber un archivo a la hora de procesar.
            raise UserError("Debe seleccionar archivo a procesar")

        data = base64.b64decode(self.xls_vacaciones_ids[0].datas)
        book = xlrd.open_workbook(file_contents=data)
        sheet_g = book.sheet_by_index(0)
        self.process_sheet_multithread(sheet_g)

    def process_sheet_multithread(self, sheet):
        env_vacaciones = self.env['ing.alta.baja.licencia']
        env_employee = self.env['hr.employee']

        error_list = []

        for i in range(0, sheet.nrows):
            row = sheet.row_slice(i)
            dni = row[0].value
            if len(str(int(dni))) > 8:
                error_list.append(dni)

        if error_list:
            self.sudo().write({'txt_error': error_list})

        if not self.txt_error:
            for i in range(0, sheet.nrows):
                row = sheet.row_slice(i)
                dni = row[0].value
                val = int(row[1].value)

                _logger.info('CREAR')
                _logger.info(dni)

                id_employee = env_employee.search([('identification_id', '=', str(int(dni)))], limit=1)

                _logger.info('EMPLOYE')
                _logger.info(id_employee)

                if id_employee:
                    crear = env_vacaciones.sudo().create({'employee_id': id_employee.id,
                                                          'state': 'alta',
                                                          'dias': val,
                                                          'periodo': self.periodo,
                                                          'fecha_inicio': self.fecha_importacion,
                                                          })
                    _logger.info('DENTRO')
                    _logger.info(crear)
