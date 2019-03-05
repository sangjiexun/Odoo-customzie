# -*- coding: utf-8 -*-
from odoo import http 
class ProductProduction(http.Controller):
    #　一覧画面、検索結果
    @http.route('/production/list', auth='public')
    def list(self, **kwargs):
        pp = http.request.env['product.production']
        pps = pp.search([])
        return http.request.render('product_production_app.product_production_list', {'pps': pps})

    @http.route('/product/HelloWorld', auth='public')
    def index(self, **kw):
        return "Hello, world"
    # 個別入庫画面
    @http.route('/production/warehousing', auth='user')
    def warehousing(self, **kwargs):
        pp = http.request.env['product.production']
        pps = pp.search([])
        return http.request.render('product_production_app.product_production_warehousing', {'pps': pps})
