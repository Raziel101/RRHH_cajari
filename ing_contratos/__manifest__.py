# -*- coding: utf-8 -*-
{
    'name': "Administración de Contratos ",

    'summary': """
        Administración de Personal""",

    'description': """
        Administración de Personal
    """,

    'author': "Ingenio Solutions",
    'website': "http://www.ingeniosolutions.com.ar",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', "mail", "ing_ausencias"],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Initial data
        'data/initial_data.xml',

        # Menu
        'menu_view.xml',

        # SECUENCE
        'sequence/sequence.xml',

        # Views
        'views/ing_contrato_view.xml',
        'views/ing_hora_view.xml',
        'views/ing_secretaria_view.xml',
        'views/ing_categoria_view.xml',
        'views/inherit_view/ing_tipo_contrato_view.xml',
        'views/inherit_view/hr_employee_views.xml',

        # WIZARD
        'wizard/horarios_wizard.xml',
        'wizard/attachment_wizard.xml',
        'wizard/nota_correccion_wizard.xml',

        # REPORTS
        'reports/reports.xml',
        'reports/contrato_locacion_report.xml',

    ],
}
