# -*- coding: utf-8 -*-

{
    'name': "Base Inherit",
    'description': "Base inherit",
    'author': "youshinan",
    'version': '12.0.1.0',
    'category': '',
    # any module necessary for this one to work correctly
    'depends': ['base'],
    'application': False,
    'data': [
        'views/res_users_views.xml',
        'views/res_bank_views.xml',
        'views/res_company_views.xml',
        #'views/res_partner_views.xml',
        'security/base_groups.xml',
    ],
}
