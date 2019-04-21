# -*- coding: utf-8 -*-
from odoo import http


class Momo(http.Controller):

    @http.route('/momo/momo/hello/', auth='public')
    def hello(self, **kw):
        return http.request.render('momo.barcode_scanner', {
        })
