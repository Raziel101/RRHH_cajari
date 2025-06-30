# -*- coding: utf-8 -*-
{
    'name': "Administración de Solicitudes ",

    'summary': """
        Administración de Solicitudes""",

    'description': """
        Administración de Solicitudes
    """,

    'author': "Ingenio Solutions",
    'website': "http://www.ingeniosolutions.com.ar",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', "mail", "ing_ausencias", "ing_contratos"],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/initial_data.xml',

        # Assets
        'assets.xml',

        # Menu
        'menu_view.xml',

        # Views
        'views/ing_solicitud_view.xml',
        'views/ing_subsidio_view.xml',
        'views/inherit_view/hr_employee_view.xml',

        # WIZARD
        'wizard/nota_correccion_adelantos_wizard.xml',

        # REPORTS
        'reports/subsidy_report.xml',
        'reports/reports.xml',
        'reports/solicitud_report.xml',

    ],
}
