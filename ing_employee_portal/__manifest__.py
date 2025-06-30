# -*- coding: utf-8 -*-
{
    'name': "Employee Portal Custom ",

    'summary': """ """,

    'description': """
        
    """,

    'author': "Ingenio Solutions",
    'website': "https://ingeniosolutions.com.ar",
    'category': 'Uncategorized',
    'version': '14.0.1',

    'depends': ['base', 'portal', "ing_seguros", "ing_rrhh_solicitudes", "ing_licencias", "ing_contratos",
                "ing_ausencias", 'web'],
    'data': [
        'data/data_initial.xml',

        'views/login.xml',
        'views/layout_portal.xml',
        'views/ing_procedure_view.xml',
        'views/hr_employee_view.xml',
        'views/ing_licencias_tipo.xml',
        'views/form_general_views.xml',
        'views/ing_solicitud_view.xml',

        'assets.xml',

        'security/ir.model.access.csv',
        'security/security.xml',

        'templates/personal_data.xml',
        'templates/holidays.xml',
        'templates/advances.xml',
        'templates/subsidies.xml',
        'templates/licenses.xml',
        'templates/hours.xml',
        'templates/scales.xml',
        'templates/guides.xml',

        'menus.xml',
    ],
}
