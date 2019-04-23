# -*- coding: utf-8 -*-
import webbrowser
from datetime import datetime as dt
from odoo import api, fields, models
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128


class BarcodePrintWizard(models.TransientModel):
    _name = "momo.barcode.print.wizard"

    start_row = fields.Integer('Print Start Row', default=1)
    start_column = fields.Integer('Print Start Column', default=1)

    @api.multi
    def print_barcode1(self):
        product_line_active_ids = self._context.get('product_line_active_ids')
        self.env['momo.product.line'].count_and_create_barcode_pdf(product_line_active_ids, self.start_row,
                                                                   self.start_column)


class ProductLineCreator(models.Model):
    _name = 'momo.product.line.creator'
    _description = 'Product Line Creator'
    _order = 'id desc'

    creator_detail_ids = fields.One2many('momo.product.line.creator.detail',
                                         'product_line_creator_id',
                                         'Product Line Creator Detail', copy=True)
    is_created = fields.Boolean('Is Created', default=False)
    remark = fields.Char('Remark')
    init_location_id = fields.Many2one('stock.location', 'Init Location',
                                       domain="[('active','=',True),('usage','=','internal')]")
    init_location = fields.Char(related='init_location_id.name')

    @api.multi
    def _create_product_line(self):
        for creator in self:
            if not creator.is_created:
                for line in creator.creator_detail_ids:
                    for i in range(int(line.need_qty)):
                        res = {
                            'product_id': line.product_id.id,
                            'remark': self.remark,
                            'init_location': self.init_location,
                        }
                        self.env['momo.product.line'].create(res)
                    creator.update({'is_created': True})
        return True


class ProductLineCreatorDetail(models.Model):
    _name = 'momo.product.line.creator.detail'
    _description = 'Product Line Creator Detail'
    _order = 'id'

    product_line_creator_id = fields.Many2one('momo.product.line.creator', 'Product Line Creator', index=True,
                                              required=True)
    product_id = fields.Many2one('product.product', 'Product', index=True, required=True)
    need_qty = fields.Float('Need Quantity', default=0.0, required=True)


class ProductLine(models.Model):
    _name = 'momo.product.line'
    _description = 'Product Line'
    _order = 'id'

    product_id = fields.Many2one('product.product', 'Product', index=True, required=True)
    product_no = fields.Char(related='product_id.product_no')
    product_name = fields.Char(related='product_id.product_tmpl_id.name')
    serial_no = fields.Char(string='Serial No')
    barcode = fields.Char('Barcode', compute='_compute_barcode', store=True)
    printed = fields.Boolean('Is Printed', default=False)
    init_location = fields.Char('Init Location', required=True)
    stock_picking_ids = fields.One2many('momo.product.line.picking', 'product_line_id', 'Stock Picking',
                                        copy=True)

    current_location = fields.Char('Current Location', compute='_compute_current_location', store=True)
    sale_order_id = fields.Char('Sale Order Id', compute='_compute_sale_info', store=True)
    sale_order_name = fields.Char('Sale Order Name', compute='_compute_sale_info', store=True)
    customer_id = fields.Char('Customer Id', compute='_compute_sale_info', store=True)
    customer_name = fields.Char('Customer Name', compute='_compute_sale_info', store=True)
    delivery_date = fields.Datetime('Delivery Date', compute='_compute_sale_info', store=True)
    is_defective = fields.Boolean('Is Defective Product Line', default=False)
    defective_detail = fields.Text('Defective Detail')

    remark = fields.Char('Remark')

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(ProductLine, self).create(vals_list)
        for line in lines:
            line.update({'serial_no': self._get_next_serial_no(line.product_no)})
        return lines

    @api.model
    def _get_next_serial_no(self, product_no):
        max_line = self.search([('product_no', '=', product_no), ('serial_no', '!=', '')], order="serial_no desc",
                               limit=1)
        if max_line:
            return str(int(max_line.serial_no) + 1)
        return '1000001'

    @api.depends('product_no', 'serial_no')
    def _compute_barcode(self):
        for line in self:
            line.barcode = str(line.product_no) + str(line.serial_no)

    @api.one
    @api.depends('stock_picking_ids')
    def _compute_current_location(self):
        newest_product_line_picking = self.env['momo.product.line.picking'].search([('product_line_id', '=', self.id)],
                                                                                   order="id desc", limit=1)
        if newest_product_line_picking:
            newest_stock_picking = self.env['stock.picking'].browse(newest_product_line_picking.stock_picking_id.id)
            self.current_location = newest_stock_picking.location_dest_id.name
        else:
            self.current_location = self.init_location

    @api.one
    @api.depends('stock_picking_ids')
    def _compute_sale_info(self):
        newest_product_line_picking = self.env['momo.product.line.picking'].search(
            [('product_line_id', '=', self.id), ('sale_id', '!=', False)],
            order="id desc", limit=1)
        if newest_product_line_picking:
            newest_sale_order = self.env['sale.order'].browse(newest_product_line_picking.sale_id)
            if newest_sale_order:
                self.sale_order_name = newest_sale_order.name
                self.customer_name = newest_sale_order.partner_id.name
                self.sale_order_id = newest_sale_order.id
                self.customer_id = newest_sale_order.partner_id.id
                self.delivery_date = newest_sale_order.create_date


    @api.model
    def search_for_scanner(self, location, barcode):
        line = self.env['momo.product.line'].search(
            [('current_location', '=', location), ('barcode', '=', barcode)])
        if line:
            return line

    @api.multi
    def call_print_wizard(self):
        view_id = self.env['momo.barcode.print.wizard'].create({'start_row': 1, 'start_column': 1}).id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Barcode Print Wizard',
            'src_model': 'momo.product.line',
            'res_model': 'momo.barcode.print.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': view_id,
            'target': 'new',
            'context': {'product_line_active_ids': self._context.get('active_ids')}
        }

    @api.multi
    def count_and_create_barcode_pdf(self, product_line_active_ids, start_row=1, start_column=1):
        init_count = (start_row - 1) * 5 + (start_column - 1)
        sum_count = init_count + len(product_line_active_ids)
        page_count = sum_count // 65 + 1

        pdf_name_first = "barcode_print_" + dt.now().strftime('%Y_%m_%d_%H_%M_%S_')

        for x in range(page_count):
            pdf_name = pdf_name_first + str(x) + ".pdf"
            # first page
            if x == 0:
                self.print_barcode(pdf_name, product_line_active_ids[0:(65 - init_count)], start_row, start_column)
            # last page
            elif x == page_count - 1:
                self.print_barcode(pdf_name,
                                   product_line_active_ids[(65 - init_count) + 65 * (x - 1):(sum_count - init_count)])
            # other pages
            else:
                self.print_barcode(pdf_name,
                                   product_line_active_ids[(65 - init_count) + 65 * (x - 1):(65 - init_count) + 65])

    @api.multi
    def print_barcode(self, pdf_name, product_line_active_ids, start_row=1, start_column=1):

        c = canvas.Canvas(pdf_name, pagesize=A4)
        xmargin = 3.5 * mm
        ymargin = 10.92 * mm
        swidth = 40.6 * mm
        sheight = 21.2 * mm
        i = (start_row - 1) * 5 + (start_column - 1)

        for product_line_active_id in product_line_active_ids:
            line = self.env['momo.product.line'].search([('id', '=', product_line_active_id)])

            x = xmargin + swidth * (i % 5)
            y = ymargin + sheight * (12 - (i // 5))

            self.draw_label(c, x, y, line.barcode)
            line.update({'printed': True})
            i += 1
        c.save()
        webbrowser.open_new(pdf_name)

    @staticmethod
    def draw_label(c, x, y, data):
        c.setLineWidth(0.5)
        c.rect(x, y, 40.6 * mm, 21.2 * mm, stroke=0, fill=0)
        c.setFont("Courier-Bold", 8)
        c.drawString(x + 8.6 * mm, y + 13.4 * mm, data)
        barcode = code128.Code128(data, barWidth=0.26 * mm, barHeight=8.0 * mm, checksum=False)
        barcode.drawOn(c, x - 3.3 * mm, y + 3.4 * mm)


class ProductLinePicking(models.Model):
    _name = 'momo.product.line.picking'
    _description = 'Product Line Picking'
    _order = 'id'

    product_line_id = fields.Many2one('momo.product.line', 'Product Line', index=True, required=True)
    stock_picking_id = fields.Many2one('stock.picking', 'Stock Picking', index=True, required=True)
    barcode = fields.Char(related='product_line_id.barcode')
    name = fields.Char(related='stock_picking_id.name')
    sale_id = fields.Integer('stock.picking', related='stock_picking_id.sale_id.id')
    picking_type_id = fields.Integer('stock.picking', related='stock_picking_id.picking_type_id.id')
    picking_type_id_name = fields.Char('stock.picking', related='stock_picking_id.picking_type_id.name')
    sale_order_name = fields.Char('stock.picking', related='stock_picking_id.sale_id.name')
    customer_name = fields.Char('stock.picking', related='stock_picking_id.sale_id.partner_id.name')
    is_defective = fields.Boolean(related='product_line_id.is_defective')
    state = fields.Char(string='State')