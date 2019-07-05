# -*- coding: utf-8 -*-
from odoo import http 
class ProductProduction(http.Controller):
    @http.route('/product/production', auth='user')
    def list(self, **kwargs):
        pp = http.request.env['product.production']
        pps = pp.search([])
        return http.request.render('product_production_app.product_production_list_template', {'pps': pps})
