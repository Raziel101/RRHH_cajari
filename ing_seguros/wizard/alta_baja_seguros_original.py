# -*- encoding: utf-8 -*-

from odoo import models, fields, api
import logging
from io import BytesIO
import base64
from odoo.tools.misc import xlwt
import xlrd
from datetime import datetime
_logger = logging.getLogger(__name__)


class AltaBajaWz(models.TransientModel):
    _name = 'ing.alta.baja.seguros.wz'

    employee_ids = fields.Many2many('hr.employee', string='Empleados', required=True,
                                    domain='[("tipo_contrato_id","in",["Locación de Servicios","Contrato de Voluntariado"])]')

    def alta_seguros(self):
        self._get_xls_seguro('Altas', 'GA')

    def baja_seguros(self):
        self._get_xls_seguro('Bajas', 'GB')

    def _get_xls_seguro(self, tipo, type_secure):
        wbook = xlwt.Workbook()
        wsheet = wbook.add_sheet(tipo)

        bold_style = xlwt.easyxf(
            'font: bold on;'
            'pattern: pattern solid;'
            'borders: left thick, right thick, top thick, bottom thick;'
            'align: vertical center, horizontal center;'
        )

        employees = self.employee_ids
        wsheet.write_merge(1, 1, 0, 3, f'{tipo} - Seguros', bold_style)

        # CARGO LAS COLUMNAS (DNI, Nombre, Apellido, Fecha de Nacimiento)
        columnas = ['DNI', 'Nombre', 'Apellido', 'Fecha de Nac.']
        for i, val in enumerate(columnas):
            wsheet.write(3, i, val, bold_style)

        # CARGO LAS FILAS
        for i, e in enumerate(employees):
            # Separar apellido y nombre (asumiendo que `e.name` tiene "Apellido, Nombre")
            apellido = ""
            nombre = ""

            if "," in e.name:
                apellido, nombre = e.name.split(",", 1)
                apellido = apellido.strip()
                nombre = nombre.strip()
            else:
                # Si no tiene coma, asumimos que solo hay un valor (puede ser nombre o apellido)
                apellido = e.name.strip()

            # Escribir en el Excel
            wsheet.write(i + 4, 0, e.identification_id)  # DNI
            wsheet.write(i + 4, 1, nombre)  # Nombre
            wsheet.write(i + 4, 2, apellido)  # Apellido
            wsheet.write(i + 4, 3, e.birthday.strftime("%d/%m/%Y"))  # Fecha de Nacimiento

            wsheet.row(i + 4).height_mismatch = True
            wsheet.row(i + 4).height = 350

        # AJUSTE DE ANCHOS DE COLUMNA
        wsheet.col(0).width = 5000  # DNI
        wsheet.col(1).width = 8000  # Nombre
        wsheet.col(2).width = 8000  # Apellido
        wsheet.col(3).width = 5000  # Fecha de Nacimiento

        # AJUSTE DE ALTURAS
        wsheet.row(3).height_mismatch = True
        wsheet.row(3).height = 450
        wsheet.row(1).height_mismatch = True
        wsheet.row(1).height = 450

        """bold_style = xlwt.easyxf('font: bold on;' 'pattern: pattern solid, fore_colour light_orange;'
                                 'borders: left thick, right thick, top thick, bottom thick;'
                                 'align: vertical center, horizontal center;')

        employees = self.employee_ids
        wsheet.write_merge(1, 1, 1, 3, f'{tipo} - Seguros', bold_style)

        # CARGO LAS COLUMNAS
        columnas = ['Apellido y Nombre', 'Fecha de Nac.', 'DNI']
        for i, val in enumerate(columnas):
            wsheet.write(3, 1 + i, val, bold_style)

        # CARGO LA FILAS
        for i, e in enumerate(employees):
            for l, dat in enumerate(e):
                wsheet.write(i + 4, l + 1, dat.name)
                wsheet.write(i + 4, l + 2, dat.birthday.strftime("%d/%m/%Y"))
                wsheet.write(i + 4, l + 3, dat.identification_id)
                wsheet.row(i + 4).height_mismatch = True
                wsheet.row(i + 4).height = 350

        wsheet.col(1).width = 10000
        wsheet.col(2).width = 5000
        wsheet.row(3).height_mismatch = True
        wsheet.row(3).height = 450
        wsheet.row(1).height_mismatch = True
        wsheet.row(1).height = 450"""

        fp = BytesIO()
        wbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        _name = f"Seguro {tipo} {datetime.now().strftime('%d-%m-%Y')}.xls"
        attach_id = self.env['ir.attachment'].create({
            'name': _name,
            'store_fname': _name,
            'datas': base64.b64encode(data),
            'mimetype': "application/vnd.ms-excel",
            'res_model': 'ing.alta.baja.seguros.wz',
            'res_id': self.id,
        })

        for e in employees:
            e.secure = type_secure

        emails_to = self.env['ing.seguros.config'].search([])

        self.env['mail.mail'].sudo().create({
            'subject': f'Solicitud de {tipo} de seguros Póliza 80357/12',
            'body_html': f'''<h3>Buenos días:</h3>
            Buenos días:
                        Por medio del presente, adjunto planilla con el listado del personal contratado con el fin de solicitar la {tipo} de seguro. 
                        Sin otro particular, y quedando a vuestra entera disposición me despido muy atentamente.<br><br>
                        Dirección del Personal.<br>
                        {self.env.user.name}''',
            'email_from': 'rrhh@chajari.gob.ar',
            'email_to': ','.join([e.name for e in emails_to]),
            'reply_to': '',
            'attachment_ids': [attach_id.id],
        }).send()

        # return {
        #         "name": "Descargar excel seguros",
        #         "type": "ir.actions.act_url",
        #         "url": f"/web/content/{attach_id.id}?download=true",
        #         "target": "new",
        #     }
