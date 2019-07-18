# -*- coding: utf-8 -*-

{
    'name': "initial",
    'description': "initial",
    'author': "youshinan",
    'version': '12.0.1.0',
    'category': '',
    # any module necessary for this one to work correctly
    'depends': ['hr_holidays', 'sale_management', 'purchase', 'stock_account', 'website', 'contacts', 'momo', 'nashi', 'after_service', 'company_stamp', 'auto_backup'],
    'application': False,
    'data': [
        'data/res_partner_initial.xml',
        'data/res_users_initial.xml',
        'data/hr_initial.xml',
        'data/product_initial.xml',
        'data/stock_data.xml',
    ],
}
