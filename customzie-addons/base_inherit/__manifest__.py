# -*- coding: utf-8 -*-

{
    'name': "Base Inherit",
    'description': "Base inherit",
    'author': "youshinan",
    'version': '12.0.1.0',
    'category': '',
    # any module necessary for this one to work correctly
    'depends': ['base', 'base', 'base', 'base'],
    'application': False,
    'data': [
        'security/base_groups.xml',
        'views/res_users_views.xml',
        'views/res_bank_views.xml',
        'views/res_company_views.xml',
        'views/management_menu.xml',
    ],
}
