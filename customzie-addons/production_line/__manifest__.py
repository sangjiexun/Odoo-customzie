# -*- coding: utf-8 -*-

{
    'name': "Production Line",
    'description': "Production Line",
    'version': '12.0.1.0',
    'category': '',
    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'sale', 'purchase'],
    'application': True,
    'data': [
        'views/production_line_view.xml',
        'views/production_line_menu.xml',
        'security/production_line_security.xml',
        'security/ir.model.access.csv',
    ],
}
