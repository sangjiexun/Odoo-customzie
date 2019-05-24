# -*- coding: utf-8 -*-
from odoo import http,_
from odoo.http import request

class Momo(http.Controller):

    @http.route('/momo/reports/<string:pdf_name>', auth='public')
    def get_pdf_file(self, pdf_name):
        pdf_path = "/home/developer/odoo-dev/odoo/customzie-addons/momo/reports/"
        pdf_file = pdf_path + pdf_name
        pdf = open(pdf_file,'rb')
        pdfhttpheaders = [
            ('Content-Type','application/pdf'),
        ]
        return request.make_response(pdf,headers=pdfhttpheaders)
