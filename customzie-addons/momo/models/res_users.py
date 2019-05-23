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
    def call_print_wizard(self):
        print("user print barcode.")
        res_id = self.env['momo.barcode.print.wizard'].create({'start_row': "1", 'start_column': "1"}).id
        view_id = self.env['ir.ui.view'].search([('name', '=', 'User Barcode Print Wizard')]).id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Barcode Print Wizard',
            'src_model': 'base.res.users',
            'res_model': 'momo.barcode.print.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': res_id,
            'view_id': view_id,
            'target': 'new',
            'context': {'user_active_ids': self._context.get('active_ids')}
        }

    @api.multi
    def count_and_create_barcode_pdf(self, user_active_ids, start_row=1, start_column=1):
        init_count = (start_row - 1) * 5 + (start_column - 1)
        sum_count = init_count + len(user_active_ids)
        page_count = (sum_count - 1) // 65 + 1

        pdf_name = "barcode_print_" + dt.now().strftime('%Y_%m_%d_%H_%M_%S') + ".pdf"

        c = canvas.Canvas(pdf_name, pagesize=A4)

        for x in range(page_count):

            if x == 0:
                self.print_barcode(c, user_active_ids[0:(65 - init_count)], start_row, start_column)
            # last page
            elif x == page_count - 1:
                self.print_barcode(c,
                                   user_active_ids[(65 - init_count) + 65 * (x - 1):(sum_count - init_count)])
            # other pages
            else:
                self.print_barcode(c,
                                   user_active_ids[(65 - init_count) + 65 * (x - 1):(65 - init_count) + 65])

        c.save()
        return pdf_name

    @api.multi
    def print_barcode(self, c, user_active_ids, start_row=1, start_column=1):

        xmargin = 3.5 * mm
        ymargin = 10.92 * mm
        swidth = 40.6 * mm
        sheight = 21.2 * mm
        i = (start_row - 1) * 5 + (start_column - 1)

        for user_active_id in user_active_ids:
            line = self.env['res.users'].search([('id', '=', user_active_id)])

            x = xmargin + swidth * (i % 5)
            y = ymargin + sheight * (12 - (i // 5))

            self.draw_label(c, x, y, line.user_barcode)
            i += 1

        c.showPage()

    @staticmethod
    def draw_label(c, x, y, data):
        c.setLineWidth(0.5)
        c.rect(x, y, 40.6 * mm, 21.2 * mm, stroke=0, fill=0)
        c.setFont("Courier-Bold", 8)
        c.drawString(x + 8.6 * mm, y + 13.4 * mm, data)
        barcode = code128.Code128(data, barWidth=0.26 * mm, barHeight=8.0 * mm, checksum=False)
        barcode.drawOn(c, x - 3.3 * mm, y + 3.4 * mm)
