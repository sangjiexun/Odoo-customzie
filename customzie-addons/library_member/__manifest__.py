# -*- coding: utf-8 -*-

{
    'name': 'Library Members',
    'description': 'Manage people who will be able to borrow books.',
    'author': 'youshinan',
    'depends': ['library_app', 'mail'],
    'application': False,
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/book_view.xml',
        'views/member_view.xml',
        'views/library_menu.xml',
        'views/book_list_template.xml',
    ],
}