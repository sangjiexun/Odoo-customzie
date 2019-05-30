# -*- coding: utf-8 -*-
from odoo import http,_
from odoo.http import request

class Momo(http.Controller):

    @http.route('/web/momo/reports/<string:pdf_name>', auth='user')
    def get_pdf_file(self, pdf_name, **kwargs):
        pdf_path = "/opt/pdf/"
        pdf_file = pdf_path + pdf_name
        pdf = open(pdf_file,'rb')
        pdfhttpheaders = [
            ('Content-Type','application/pdf'),
        ]
        return request.make_response(pdf,headers=pdfhttpheaders)
