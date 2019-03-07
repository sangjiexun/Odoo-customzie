{
    'name': "Production Line",
    'description': "Production Line",

    'author': "YUAN CHUANG",
    #'category': 'Uncategorized',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'application': True,
    'license': 'LGPL-3',
    'data': [
        'views/production_line_view.xml',
        'views/production_line_menu.xml',
        'security/production_line_security.xml',
        'security/ir.model.access.csv',
    ],
}
