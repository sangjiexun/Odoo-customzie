# -*- coding: utf-8 -*-
{
    'name': "nashi",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ckc",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase', 'sale_stock'],

    # always loaded
    'data': [
        'security/assemble_security.xml',
        'security/ir.model.access.csv',
        'views/nashi_assemble_views.xml',
        'views/stock_picking_views.xml',
        'views/nashi_menu.xml',
        'data/nashi_data.xml',
        'data/ir_sequence_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}