{
    'name': "Product Production Manager",
    'description': "Manage Product Production",

    'author': "YUAN CHUANG",
    # cate 後の設定との関係??
    #'category': 'Uncategorized',
    'version': '12.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'application': True,
    'license': 'LGPL-3',
    'data': [
        'security/product_production_security.xml',
        'security/ir.model.access.csv',
        'views/product_production_input_individual_view.xml',
        'views/product_production_input_batch_view.xml',
        "views/product_production_clean_view.xml",
        'views/product_production_menu.xml',
        'views/product_production_view.xml',
        'views/product_production_list_template.xml',
    ],
    'demo': [ 
        #'data/res.partner.csv', 
       # 'data/product.production.csv',
    ],
}
