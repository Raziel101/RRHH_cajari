# -*- coding: utf-8 -*-
{
    'name': "Administración de Licencias ",

    'summary': """
        Administración de Licencias""",

    'description': """
        Administración de Licencias
    """,

    'author': "Ingenio Solutions",
    'website': "http://www.ingeniosolutions.com.ar",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', "hr", "mail", "ing_ausencias", "ing_rrhh_solicitudes"],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Initial data
        'data/initial_data.xml',
        'data/cron.xml',

        # Menu
        'menu_view.xml',

        # Views
        'views/ing_form_general_view.xml',
        'views/ing_hours_sev_view.xml',
        'views/ing_base_form_view.xml',
        'views/ing_tipo_licencia_view.xml',
        'views/ing_dia_periodo_view.xml',
        'views/ing_alta_baja_licencia_view.xml',
        'views/inherit_view/hr_employee_views.xml',
        'views/ImportVacaciones/ing_import_vacaciones_view.xml',

        # WIZARD
        'wizard/attachment_wizard.xml',
        'wizard/nota_correccion_wizard.xml',

        # REPORTS
        'reports/reports.xml',
        'reports/licencia_report.xml',

    ],
}
