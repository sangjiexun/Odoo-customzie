# -*- coding: utf-8 -*-

{
    'name': "Production Line",
    'description': "Production Line",
    'author': "youshinan",
    'version': '12.0.1.0',
    'category': '',
    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'sale', 'purchase'],
    'application': True,
    'data': [
        'views/production_line_view.xml',
        'views/product_template_views.xml',
        'views/product_views.xml',
        # 'views/assets.xml',
        'security/production_line_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/production_operation_data.xml',
        'data/marker_data.xml',
    ],
}
