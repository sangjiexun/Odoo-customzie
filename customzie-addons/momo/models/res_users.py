# -*- coding: utf-8 -*-
from datetime import datetime as dt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from odoo import api, fields, models, _


class Users(models.Model):
    _inherit = 'res.users'

    @api.multi
    def print_user_barcode(self):
        pdf_name = self.env['res.users'].count_and_create_barcode_pdf(self._context.get('active_ids'))
        return{
            "type": "ir.actions.act_url",
            "url" : "/web/momo/reports/%s" % pdf_name,
            "target": "new",
        }


    @api.multi
    def count_and_create_barcode_pdf(self, user_active_ids):
        page_count = len(user_active_ids)

        pdf_path = "/opt/pdf/"
        pdf_name = "barcode_print_" + dt.now().strftime('%Y_%m_%d_%H_%M_%S') + ".pdf"
        pdf_file = pdf_path + pdf_name

        c = canvas.Canvas(pdf_file)
        c.setPageSize((44 * mm, 24 * mm))
        x = y = 0
        for i in range(page_count):
            line = self.env['res.users'].search([('id', '=', user_active_ids[i])])
            self.draw_label(c, x, y, line.user_barcode)
            c.showPage()
        c.save()
        return pdf_name

    @staticmethod
    def draw_label(c, x, y, data):
        #c.setLineWidth(0.5)
        #c.rect(x + 2 * mm, y + 2 * mm, 40 * mm, 20 * mm, stroke=True, fill=0)
        c.setFont("Courier-Bold", 10)
        c.drawString(x + 6 * mm, y + 6 * mm, data)
        barcode = code128.Code128(data, barWidth=0.25 * mm, barHeight= 9 * mm, checksum=False)
        barcode.drawOn(c, x - 1 * mm, y + 10 * mm)
