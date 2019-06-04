# -*- coding: utf-8 -*-
from odoo import http

# class Nashi(http.Controller):
#     @http.route('/nashi/nashi/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/nashi/nashi/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('nashi.listing', {
#             'root': '/nashi/nashi',
#             'objects': http.request.env['nashi.nashi'].search([]),
#         })

#     @http.route('/nashi/nashi/objects/<model("nashi.nashi"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('nashi.object', {
#             'object': obj
#         })