# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import Warning
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128


class ProductionOperation(models.Model):

    _name = 'production.operation'
    _description = 'Production operation'
    _order = 'sequence, id'

    name = fields.Char('Production Operation', required=True, index=True, translate=True)
    color = fields.Integer('Color')
    sequence = fields.Integer('Sequence', help="Used to order the 'All Operations' kanban view")
    # sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence', required=True)
    active = fields.Boolean('Active', default=True)
    action_name = fields.Char('Action Name')
    production_line = fields.One2many('production.line', 'operation_id', string='Production Lines', copy=True)
    # Statistics for the kanban view
    count_picking_inventory = fields.Integer(compute='_compute_picking_inventory', store=True)
    count_picking_pick = fields.Integer(compute='_compute_picking_pick')
    count_picking_manufacture = fields.Integer(compute='_compute_picking_manufacture')
    count_picking_clean = fields.Integer(compute='_compute_picking_clean')
    count_picking_delivery = fields.Integer(compute='_compute_picking_delivery')

    @api.multi
    def _compute_picking_inventory(self):
        return self.env['production.line'].search_count([('need_inventory', '=', True), ('state', '=', 'draft')])

    def _compute_picking_pick(self):
        return self.env['production.line'].search_count([('need_pick', '=', True), ('state', '=', 'inventory')])

    def _compute_picking_manufacture(self):
        return self.env['production.line'].search_count([('need_manufacture', '=', True), ('state', '=', 'inventory')])

    def _compute_picking_clean(self):
        return self.env['production.line'].search_count([('need_clean', '=', True), ('state', '=', 'inventory' or 'manufactured')])

    def _compute_picking_delivery(self):
        return self.env['production.line'].search_count([('need_delivery', '=', True), ('state', '=', 'inventory' or 'cleaned' or 'inventory')])


class ProductionLine(models.Model):

    _name = 'production.line'
    _description = 'Production Line'
    _order = 'id'

    name = fields.Char('Production Line')
    barcode = fields.Char('Barcode', compute='_compute_barcode', store=True)
    serial_no = fields.Char('Serial No')

    operation_id = fields.Many2one('production.operation', string='Production Oeration', index=True)

    # Purchase
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line', string='Purchase Reference', ondelete='set null')
    purchase_order_id = fields.Many2one(string='Purchase Order', related="purchase_order_line_id.order_id", store=True)
    purchase_partner_id = fields.Many2one(string='Supplier', related="purchase_order_line_id.partner_id", store=True)
    purchase_price_unit = fields.Float(string='Purchase Price', related="purchase_order_line_id.price_unit", store=True)

    # Inventory
    inventory_name = fields.Char('Inventory Name')
    inventory_date = fields.Datetime()
    inventory_uid = fields.Many2one('res.users', string='Inventory Uid')
    need_inventory = fields.Boolean('Need Inventory', default=True)

    # Pick
    pick_name = fields.Char('Pick Name')
    pick_date = fields.Datetime()
    pick_uid = fields.Many2one('res.users', string='Pick Uid')
    need_pick = fields.Boolean('Need Pick', default=False)

    # Manufacture
    manufacture_name = fields.Char('Manufacture Name')
    manufacture_date = fields.Datetime()
    manufacture_uid = fields.Many2one('res.users', string='Manufacture Uid')
    need_manufacture = fields.Boolean('Need Manufacture', default=False)

    # Clean
    clean_name = fields.Char('Clean Name')
    clean_date = fields.Datetime()
    clean_uid = fields.Many2one('res.users', string='Clean Uid')
    need_clean = fields.Boolean('Need Clean', default=False)

    # Delivery
    delivery_name = fields.Char('Delivery Name')
    delivery_date = fields.Datetime()
    delivery_uid = fields.Many2one('res.users', string='Delivery Uid')
    need_delivery = fields.Boolean('Need Delivery', default=False)

    # Sale
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Reference', ondelete='set null')
    sale_order_id = fields.Many2one(string='Sale Order', related="sale_order_line_id.order_id", store=True)
    sale_order_partner_id = fields.Many2one(string='Customer', related="sale_order_line_id.order_partner_id", store=True)
    sale_price_unit = fields.Float(string='Sale Price', related="sale_order_line_id.price_unit", store=True)

    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_no = fields.Char(string='Product No', related="product_id.product_no", store=True)

    is_clean = fields.Boolean(default=False, readonly=True)
    is_defect = fields.Boolean(default=False, readonly=True)
    defect_remark = fields.Text('Defect Remark')

    # Hierarchy fields
    parent_id = fields.Many2one(
        'production.line',
        'Parent Production',
        ondelete='restrict')

    # Optional but good to have:
    child_ids = fields.One2many(
        'production.line',
        'parent_id',
        'Bom Production')

    # after service
    # after_service_id = fields.Many2one('after.service', string='After Service', ondelete='set null')

    state = fields.Selection([
        ('draft', 'New'),
        ('inventory', 'Inventory'),
        ('picked', 'Picked'),
        ('manufactured', 'Manufactured'),
        ('cleaned', 'Cleaned'),
        ('delivery', 'Delivery'),
        ('done', 'Sold'),
        ('returned', 'Returned'),
        ('defect', 'Defect'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(ProductionLine, self).create(vals_list)
        for line in lines:
            line.update({'serial_no': self._get_next_serial_no(line.product_no)})
        return lines

    @api.model
    def _get_next_serial_no(self, product_no):
        max_line = self.search([('product_no', '=', product_no), ('serial_no', '!=', False)], order="serial_no desc", limit=1)
        if max_line:
            return str(int(max_line.serial_no) + 1)
        return '10000001'

    @api.depends('product_no', 'serial_no')
    def _compute_barcode(self):
        for line in self:
            line.barcode = str(line.product_no) + str(line.serial_no)

    @api.onchange('inventory_date', 'pick_date', 'manufacture_date', 'clean_date', 'delivery_date')
    def _compute_picking(self):
        """
        Trigger the recompute of the Picking if the production is changed.
        """
        return self.env['production.operation']._compute_picking_inventory()

    @api.multi
    def print_barcode(self):
        c = canvas.Canvas("production_barcode_print.pdf", pagesize=A4)
        xmargin = 8.4 * mm
        ymargin = 8.8 * mm
        swidth = 48.3 * mm
        sheight = 25.4 * mm
        i = 0

        for line in self:
            x = xmargin + swidth * (i % 4)
            y = ymargin + sheight * (10 - (i // 4))
            self.draw_label(c, x, y, line.barcode)
            i += 1
        c.save()

    @staticmethod
    def draw_label(c, x, y, data):
        c.setLineWidth(0.5)
        c.rect(x, y, 48.3*mm, 25.4*mm, stroke=1, fill=0)
        c.setFont("Courier-Bold", 8)
        c.drawString(x + 14.6*mm, y + 13.4*mm, data)
        barcode = code128.Code128("*"+data+"*", barWidth=0.26*mm, barHeight=8.0*mm, checksum=False)
        barcode.drawOn(c, x, y + 3.4*mm)



class MarkerInfo(models.Model):

    _name = 'marker.info'
    _description = 'Marker Info'
    _order = 'id'

    name = fields.Char('Marker', required=True, index=True)








