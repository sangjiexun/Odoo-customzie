# -*- coding: utf-8 -*-
{
    'name': "after_service",
    'description': "After service",
    'version': '12.0.1.0',
    'category': '',
    'depends': ['base', 'sale', 'stock', 'production_line'],
    'application': True,
    'license': 'LGPL-3',
    'data': [
        'views/after_service_views.xml',
        'views/after_service_templates.xml',
        'data/treatment_data.xml',
        'security/after_service_security.xml',
        'security/ir.model.access.csv',

    ],
}