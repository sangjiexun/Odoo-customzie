# -*- coding: utf-8 -*-
{
    'name': "momo",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ckc",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase', 'sale_stock'],

    # always loaded
    'data': [
        'security/product_line_security.xml',
        'security/ir.model.access.csv',
        'views/wizard_product_line.xml',
        'views/momo_product_line_scanner_view.xml',
        'views/momo_product_line_view.xml',
        'views/product_template_views.xml',
        'views/product_views.xml',
        'data/ir_sequence_data.xml',
        'data/marker_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
