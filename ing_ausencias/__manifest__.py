# -*- coding: utf-8 -*-
{
    'name': "Administración de Ausencias ",

    'summary': """
        Administración de Personal """,

    'description': """
        Administración de Personal 
    """,

    'author': "Ingenio Solutions",
    'website': "http://www.ingeniosolutions.com.ar",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base', "mail", "hr"],
    'data': [
        # ASSETS
        'assets.xml',

        # Initial data
        'data/initial_data.xml',

        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        # Menu
        'menu_view.xml',

        # Views
        'views/ing_ausencia_view.xml',
        'views/ing_medio_aviso_view.xml',
        'views/ing_tipo_contrato_view.xml',
        'views/clock_view.xml',

        # Inherit views
        'views/inherit_view/hr_employee_views.xml',
        'views/inherit_view/res_users_views.xml',

        # WIZARD
        'wizard/attachment_wizard.xml',
        'wizard/nota_correccion_wizard.xml',
        'wizard/print_badge_custom_view.xml',

        # REPORTS
        'reports/reports.xml',
        'reports/ausencias_report.xml',

    ],
}
