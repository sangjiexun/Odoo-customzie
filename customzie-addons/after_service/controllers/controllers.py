# -*- coding: utf-8 -*-
from odoo import http

# class AfterService(http.Controller):
#     @http.route('/after_service/after_service/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/after_service/after_service/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('after_service.listing', {
#             'root': '/after_service/after_service',
#             'objects': http.request.env['after_service.after_service'].search([]),
#         })

#     @http.route('/after_service/after_service/objects/<model("after_service.after_service"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('after_service.object', {
#             'object': obj
#         })