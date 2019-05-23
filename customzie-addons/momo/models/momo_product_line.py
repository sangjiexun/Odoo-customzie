# -*- coding: utf-8 -*-
from datetime import datetime as dt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BarcodePrintWizard(models.TransientModel):
    _name = "momo.barcode.print.wizard"
    _description = 'barcode.print.wizard'

    start_row = fields.Selection([
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'),
        (9, '9'), (10, '10'), (11, '11'), (12, '12'), (13, '13'),], string='Print Start Row', default='1')

    start_column = fields.Selection([
        (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'),], string='Print Start Column', default='1')

    @api.multi
    def print_product_barcode(self):
        product_line_active_ids = self._context.get('product_line_active_ids')
        pdf_name = self.env['momo.product.line'].count_and_create_barcode_pdf(product_line_active_ids, self.start_row,
                                                                              self.start_column)
        return {
            'type': 'ir.actions.act_url',
            'url': '/momo/momo/hello/%s' % pdf_name,
            'target': 'new',  # open in a new tab
        }

    @api.multi
    def print_user_barcode(self):
        user_active_ids = self._context.get('user_active_ids')
        pdf_name = self.env['res.users'].count_and_create_barcode_pdf(user_active_ids, self.start_row,
                                                                      self.start_column)
        return {
            'type': 'ir.actions.act_url',
            'url': '/momo/momo/hello/%s' % pdf_name,
            'target': 'new',  # open in a new tab
        }


class ProductLineGroup(models.Model):
    _name = "momo.product.line.group"
    _description = 'momo.product.line.group'

    group_id = fields.Many2one('procurement.group', 'Procurement Group')
    product_line_link_ids = fields.One2many('momo.product.line.link', 'product_line_group_id', 'Product Line Link',
                                            copy=True)


class ProductLineLink(models.Model):
    _name = "momo.product.line.link"
    _description = 'momo.product.line.link'

    product_line_group_id = fields.Many2one('momo.product.line.group', 'Product Line Group', index=True, required=True)
    product_line_id = fields.Many2one('momo.product.line', 'Product Line', index=True, required=True)

    barcode = fields.Char('Barcode')

    @api.onchange('barcode')
    def onchange_barcode(self):
        for line in self:
            res = self.env['momo.product.line'].search([('barcode', '=', line.barcode)])
            line.product_line_id = res.id


class ProductLineCreator(models.Model):
    _name = 'momo.product.line.creator'
    _description = 'Product Line Creator'
    _order = 'id desc'

    name = fields.Char('Name', readonly=True, index=True, copy=False, default='New')
    creator_detail_ids = fields.One2many('momo.product.line.creator.detail',
                                         'product_line_creator_id',
                                         'Product Line Creator Detail', copy=True)
    is_created = fields.Boolean('Is Created', default=False)
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    purchase_order_name = fields.Char('Purchase Order Name', related='purchase_id.name', store=True)
    create_type = fields.Char('Create Type', default='manu')
    init_location_id = fields.Many2one('stock.location', 'Init Location',
                                       domain="[('active','=',True),('usage','=','internal')]")
    init_location = fields.Char(related='init_location_id.name')
    group_id = fields.Char('Group Id')

    @api.multi
    def _create_product_line(self):
        for creator in self:
            if not creator.is_created:
                product_line_group_id = self.env['momo.product.line.group'].create({'group_id': self.group_id}).id
                if self.group_id:
                    self.env['procurement.group'].search([('id', '=', self.group_id)]).update(
                        {'product_line_group_id': product_line_group_id})
                for line in creator.creator_detail_ids:
                    for i in range(int(line.need_qty)):
                        res = {
                            'product_id': line.product_id.id,
                            'purchase_id': creator.purchase_id.id,
                            'init_location': creator.init_location,
                            'need_clean': line.need_clean,

                            'maker_name': line.product_id.product_tmpl_id.maker_name.name,
                            'maker_product_no': line.product_id.product_tmpl_id.maker_product_no,
                            'product_no': line.product_id.product_tmpl_id.product_no,
                            'ceo_price': line.product_id.product_tmpl_id.ceo_price,
                            'spec_cpu': line.product_id.product_tmpl_id.spec_cpu,
                            'spec_memory': line.product_id.product_tmpl_id.spec_memory,
                            'spec_hard_disc': line.product_id.product_tmpl_id.spec_hard_disc,
                            'spec_driver': line.product_id.product_tmpl_id.spec_driver,

                        }
                        product_line = self.env['momo.product.line'].create(res)
                        self.env['momo.product.line.link'].create(
                            {'product_line_group_id': product_line_group_id, 'product_line_id': product_line.id,
                             'barcode': product_line.barcode})
                    creator.update({'is_created': True})
        return True

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('momo.product.line.creator') or '/'
        return super(ProductLineCreator, self).create(vals)


class ProductLineCreatorDetail(models.Model):
    _name = 'momo.product.line.creator.detail'
    _description = 'Product Line Creator Detail'
    _order = 'id'

    product_line_creator_id = fields.Many2one('momo.product.line.creator', 'Product Line Creator', index=True,
                                              required=True)
    product_id = fields.Many2one('product.product', 'Product', index=True, required=True)
    need_qty = fields.Float('Need Quantity', default=0.0, required=True)
    need_clean = fields.Boolean('Need Clean', default=True)


class ProductLine(models.Model):
    _name = 'momo.product.line'
    _description = 'Product Line'
    _order = 'id'

    product_id = fields.Many2one('product.product', 'Product', index=True, required=True)
    product_no = fields.Char(related='product_id.product_no')
    product_name = fields.Char(related='product_id.product_tmpl_id.name')
    serial_no = fields.Char(string='Serial No')
    barcode = fields.Char('Barcode', compute='_compute_barcode', store=True, readonly=False)
    printed = fields.Boolean('Is Printed', default=False)
    init_location = fields.Char('Init Location', required=True)
    stock_picking_ids = fields.One2many('momo.product.line.picking', 'product_line_id', 'Stock Picking',
                                        copy=True)

    current_location = fields.Char('Current Location', compute='_compute_current_location', store=True, translate=True)

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    purchase_order_name = fields.Char(related='purchase_id.name', store=True)
    purchase_date = fields.Date('Purchase Date', related='purchase_id.date_approve', store=True)

    supplier_id = fields.Many2one('res.partner', 'Supplier Id', related='purchase_id.partner_id', store=True)
    supplier_name = fields.Char('Supplier Name', related='purchase_id.partner_id.name', store=True)

    sale_order_id = fields.Many2one('sale.order', 'Sale Order Id', compute='_compute_sale_info', store=True)
    sale_order_name = fields.Char('Sale Order Name', compute='_compute_sale_info', store=True)

    customer_id = fields.Many2one('res.partner', 'Customer Id', compute='_compute_sale_info', store=True)
    customer_name = fields.Char('Customer Name', compute='_compute_sale_info', store=True)
    delivery_date = fields.Datetime('Delivery Date', compute='_compute_sale_info', store=True)
    is_defective = fields.Boolean('Is Defective Product Line', default=False)
    defective_detail = fields.Text('Defective Detail')

    product_line_group_id = fields.Many2one('momo.product.line.group', 'Product Line Group')

    # Hierarchy fields
    parent_id = fields.Many2one(
        'momo.product.line',
        'Parent Production',
        ondelete='set null')

    # Optional but good to have:
    child_ids = fields.One2many(
        'momo.product.line',
        'parent_id',
        'Bom Production')

    product_rank = fields.Selection([
        ('N', 'n rank'),
        ('NS', 'ns rank'),
        ('S', 's rank'),
        ('SA', 'sa rank'),
        ('A', 'a rank'),
        ('AB', 'ab rank'),
        ('B', 'b rank'),
        ('C', 'c rank'),
        ('D', 'd rank'),
    ], string='Ranking',  translate=True, default='N')

    rack_prefix = fields.Selection([
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'),
    ], string='Rack Prefix', default='')

    rack_suffix = fields.Selection([
        ('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'd'), ('e', 'e'), ('f', 'f'),
        ('g', 'g'), ('h', 'h'), ('i', 'i'), ('j', 'j'), ('k', 'k'), ('l', 'l'), ('m', 'm'),
        ('n', 'n'), ('o', 'o'), ('p', 'p'), ('q', 'q'), ('r', 'r'), ('s', 's'), ('t', 't'),
        ('u', 'u'), ('v', 'v'), ('w', 'w'), ('x', 'x'), ('y', 'y'), ('z', 'z'),
    ], string='Rack Suffix', default='a')

    rack_no = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], string='Rack No', default='1')

    need_clean = fields.Boolean('Need Clean', default=True)
    is_cleaned = fields.Boolean('Is Cleaned', default=False)
    clean_location = fields.Char('Clean Location')

    restock = fields.Boolean('Restock', default=False)

    remark = fields.Char('Remark')

    maker_name = fields.Char('Maker Name')
    maker_product_no = fields.Char('Maker Product')
    product_no = fields.Char('Product No', readonly=True, index=True, copy=False, default='New')
    ceo_price = fields.Float('Ceo Cost', company_dependent=True, groups="base_inherit.group_ceo",)
    spec_cpu = fields.Char('Spec Cpu')
    spec_memory = fields.Char('Spec Memory')
    spec_hard_disc = fields.Char('Spec HardDisk')
    spec_driver = fields.Char('Spec Driver')

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
        newest_product_line_picking = self.env['momo.product.line.picking'].search([('product_line_id', '=', self.id)], order="id desc", limit=1)
        company_user = self.env.user.company_id
        warehouse=self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if newest_product_line_picking:
            if self.restock:
                newest_stock_picking = self.env['stock.picking'].browse(warehouse.lot_stock_id.id)
            else:
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

    @api.onchange('barcode')
    def onchange_barcode(self):
        for line in self:
            res = self.env['momo.product.line'].search([('barcode', '=', line.barcode)])
            line.product_id = res.product_id

    @api.multi
    def call_print_wizard(self):
        res_id = self.env['momo.barcode.print.wizard'].create({'start_row': "1", 'start_column': "1"}).id
        view_id = self.env['ir.ui.view'].search([('name', '=', 'Product Barcode Print Wizard')]).id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Barcode Print Wizard',
            'src_model': 'momo.product.line',
            'res_model': 'momo.barcode.print.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': res_id,
            'view_id': view_id,
            'target': 'new',
            'context': {'product_line_active_ids': self._context.get('active_ids')}
        }



    @api.one
    def pick2stock(self):
        self.write({'restock': True})
#        self._compute_current_location()

    @api.one
    def ProductLink(self):
        for line in self:
            line.write({'parent_id': line.child_ids})

    @api.multi
    def count_and_create_barcode_pdf(self, product_line_active_ids, start_row=1, start_column=1):
        init_count = (start_row - 1) * 5 + (start_column - 1)
        sum_count = init_count + len(product_line_active_ids)
        page_count = (sum_count - 1) // 65 + 1

        pdf_name = "/opt/barcode_print_" + dt.now().strftime('%Y_%m_%d_%H_%M_%S') + ".pdf"

        c = canvas.Canvas(pdf_name, pagesize=A4)

        for x in range(page_count):

            if x == 0:
                self.print_barcode(c, product_line_active_ids[0:(65 - init_count)], start_row, start_column)
            # last page
            elif x == page_count - 1:
                self.print_barcode(c,
                                   product_line_active_ids[(65 - init_count) + 65 * (x - 1):(sum_count - init_count)])
            # other pages
            else:
                self.print_barcode(c,
                                   product_line_active_ids[(65 - init_count) + 65 * (x - 1):(65 - init_count) + 65])

        c.save()
        return pdf_name

    @api.multi
    def print_barcode(self, c, product_line_active_ids, start_row=1, start_column=1):

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

        c.showPage()

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
    barcode = fields.Char('Barcode')
    name = fields.Char(related='stock_picking_id.name')
    sale_id = fields.Integer('Sale Id', related='stock_picking_id.sale_id.id')
    picking_type_id = fields.Integer('Picking Type Id', related='stock_picking_id.picking_type_id.id')
    picking_type_id_name = fields.Char('Picking Type Name', related='stock_picking_id.picking_type_id.name', store=True,
                                       translate=True)
    sale_order_name = fields.Char('Sale Order Name', related='stock_picking_id.sale_id.name')
    customer_name = fields.Char('Customer Name', related='stock_picking_id.sale_id.partner_id.name')
    is_defective = fields.Boolean(related='product_line_id.is_defective')
    state = fields.Char(string='State')

    @api.onchange('barcode')
    def onchange_barcode(self):
        for line in self:
            res = self.env['momo.product.line'].search([('barcode', '=', line.barcode)])
            line.product_line_id = res.id

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            res = self.env['momo.product.line'].search([('barcode', '=', line.barcode)])
            res.write({'restock': False})
        return lines


class ProductCleanHistory(models.Model):
    _name = 'momo.product.clean.history'
    _description = 'Product Clean History'

    product_clean_id = fields.Many2one('momo.product.clean', 'Product Clean', index=True, required=True)
    product_line_id = fields.Many2one('momo.product.line', 'Product Line', index=True, required=True)
    barcode = fields.Char('Barcode')
    location = fields.Char('Location')
    product_name = fields.Char('Product Name')


class ProductClean(models.Model):
    _name = 'momo.product.clean'
    _description = 'Product Clean'
    _order = 'id'

    scan = fields.Char(string="Scan", store=False)

    clean_history_ids = fields.One2many("momo.product.clean.history", "product_line_id", copy=True)

    def _get_clean_history_ids(self):
        self.clean_history_ids = self.env['momo.product.clean.history'].search(
            [('product_clean_id', '=', self._origin.id)],
            order="create_date desc")

    @api.onchange('scan')
    def _onchange_scan(self):
        scan_code = self.scan
        print("product clean id:", self._origin.id)
        self.scan = False
        if scan_code:
            product_line = self.env['momo.product.line'].search([('barcode', '=', scan_code)], limit=1)
            if not product_line:
                raise ValidationError(_('not found this product!'))
            else:
                if not product_line.need_clean:
                    raise ValidationError(_('this product do not need to clean!'))
                else:
                    product_clean_history = self.env['momo.product.clean.history'].search(
                        ['&', ('barcode', '=', scan_code), ('product_clean_id', '=', self._origin.id)], limit=1)
                    if product_clean_history:
                        raise ValidationError(_('this product has already been cleaned!'))
                    else:
                        self.env['momo.product.clean.history'].create(
                            {"product_line_id": product_line.id, "location": product_line.current_location,
                             "barcode": scan_code, "product_name": product_line.product_name,
                             "product_clean_id": self._origin.id})
                        product_line.write({'is_cleaned': True})
                        lines = []

                        self._get_clean_history_ids()

                        for rec in self.clean_history_ids:
                            line_item = {
                                'barcode': rec.barcode,
                                'product_name': rec.product_name,
                            }
                            lines += [line_item]

                        self.update({'clean_history_ids': lines})
