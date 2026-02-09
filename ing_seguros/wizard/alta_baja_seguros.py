# -*- encoding: utf-8 -*-
from odoo import models, fields, api
import logging
from io import BytesIO
import base64
import xlwt  # 📌 Compatible con Odoo 14
from datetime import datetime

_logger = logging.getLogger(__name__)

class AltaBajaWz(models.TransientModel):
    _name = 'ing.alta.baja.seguros.wz'

    employee_ids = fields.Many2many('hr.employee', string='Empleados', required=True,
                                    domain='[("tipo_contrato_id","in",["Locación de Servicios","Contrato de Voluntariado"])]')

    def alta_seguros(self):
        """ Genera y envía el Excel para Altas """
        return self._generate_xls_and_send_email('Altas', 'GA')

    def baja_seguros(self):
        """ Genera y envía el Excel para Bajas """
        return self._generate_xls_and_send_email('Bajas', 'GB')

    def _generate_xls_and_send_email(self, tipo, type_secure):
        """ Genera el archivo Excel y lo envía por email """

        wbook = xlwt.Workbook()
        wsheet = wbook.add_sheet(tipo)

        # 🔹 Estilo de los títulos: fondo blanco y letras negras
        bold_style = xlwt.easyxf(
            'font: bold on, color black;'
            'pattern: pattern solid, fore_colour white;'
            'borders: left thin, right thin, top thin, bottom thin;'
            'align: vertical center, horizontal center;'
        )

        employees = self.employee_ids
        wsheet.write_merge(1, 1, 0, 3, f'{tipo} - Seguros', bold_style)

        # 🔹 Cargar las columnas (DNI, Nombre, Apellido, Fecha de Nacimiento)
        columnas = ['DNI', 'Nombre', 'Apellido', 'Fecha de Nac.']
        for i, val in enumerate(columnas):
            wsheet.write(3, i, val, bold_style)

        # 🔹 Cargar las filas con datos de los empleados
        for i, e in enumerate(employees):
            apellido, nombre = (e.name.split(",", 1) + [""])[:2] if "," in e.name else (e.name, "")
            apellido, nombre = apellido.strip(), nombre.strip()

            # Escribir los valores en el Excel
            wsheet.write(i + 4, 0, e.identification_id or "")  # DNI
            wsheet.write(i + 4, 1, nombre)  # Nombre
            wsheet.write(i + 4, 2, apellido)  # Apellido
            wsheet.write(i + 4, 3, e.birthday.strftime("%d/%m/%Y") if e.birthday else "")  # Fecha de Nacimiento

            wsheet.row(i + 4).height_mismatch = True
            wsheet.row(i + 4).height = 350

        # 🔹 Ajuste de tamaños de columna
        wsheet.col(0).width = 5000  # DNI
        wsheet.col(1).width = 8000  # Nombre
        wsheet.col(2).width = 8000  # Apellido
        wsheet.col(3).width = 5000  # Fecha de Nacimiento

        # 🔹 Guardar el archivo Excel en memoria
        fp = BytesIO()
        wbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()

        _name = f"Seguro_{tipo}_{datetime.now().strftime('%d-%m-%Y')}.xls"
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

        # 🔹 Obtener los destinatarios del email
        emails_to = self.env['ing.seguros.config'].search([]).mapped('name')

        if not emails_to:
            _logger.warning("No se encontraron emails para enviar la solicitud de seguros.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'No hay emails configurados para enviar la solicitud.',
                    'sticky': True,
                }
            }

        # 🔹 Enviar el email con el adjunto
        mail_values = {
            'subject': f'Solicitud de {tipo} de seguros - Póliza 84352/12',
            'body_html': f'''<h3>Buenos días:</h3>
            Por medio del presente, adjunto la planilla del personal contratado para la solicitud de {tipo} de seguro.<br>
            <br>
            Atentamente,<br>
            Dirección del Personal.<br>
            {self.env.user.name}''',
            'email_from': 'rrhh@chajari.gob.ar',
            'email_to': ','.join(emails_to),
            'attachment_ids': [(6, 0, [attach_id.id])],  # Adjuntar el archivo Excel
        }
        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()

        # 🔹 Notificación en Odoo al completar el envío
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Correo Enviado',
                'message': f'El correo con el adjunto {tipo} se ha enviado correctamente.',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }
