# -*- coding: utf-8 -*-
{
    'name': "after_service",
    'description': "After service",
    'version': '12.0.1.0',
    'category': '',
    'author': "youshinan",
    'depends': ['momo','mail'],
    'application': True,
    'license': 'LGPL-3',
    'data': [
        'security/after_service_security.xml',
        'security/ir.model.access.csv',
        'views/after_service_views.xml',
        'report/after_service_report.xml',
        'data/treatment_data.xml',
        'data/ir_sequence_data.xml',

    ],
}
