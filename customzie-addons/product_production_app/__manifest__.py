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
        'views/product_production_view.xml',
        'views/product_production_menu.xml',
        'views/product_production_management.xml',
        'security/product_production_security.xml',
        'security/ir.model.access.csv',
    ],
   # 'demo': [
        #'data/res.partner.csv', 
       # 'data/product.production.csv',
    #],
}
