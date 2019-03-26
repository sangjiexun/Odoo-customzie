# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import Warning


class ProductionLine(models.Model):

    _name = 'production.line'
    _description = 'Production Line'
    _order = 'id'

    name = fields.Char('Production Line', required=True, index=True)
    barcode = fields.Char('Barcode')
    serial_no = fields.Char('Serial No')

    # Purchase
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line', string='Purchase Reference',
        required=True, ondelete='cascade', copy=False, readonly=True)
    purchase_order_id = fields.Many2one(
        string='Purchase Order',
        readonly=True, related='purchase_order_line_id.order_id')
    purchase_partner_id = fields.Many2one(
        'res.partner',  string='Supplier',
        readonly=True, related='purchase_order_line_id.partner_id')
    # Sale
    sale_order_line_id = fields.Many2one(
        'sale.order.line', string='Sale Reference', readonly=True)
    sale_order_id = fields.Many2one(
        string='Sale Order',
        readonly=True, related='sale_order_line_id.order_id')
    sale_partner_id = fields.Many2one(
        'res.partner', string='Customer',
        readonly=True, related='sale_order_line_id.order_partner_id')

    product_id = fields.Many2one(
        'product.product', string='Product',
        readonly=True, related='purchase_order_line_id.product_id', store=True)
    product_no = fields.Many2one(
        string='Product No',
        readonly=True, related='purchase_order_line_id.product_id', store=True)

    stock_picking__id = fields.Many2one(
        'stock.picking', string='Stock Picking',
        readonly=True, store=True)

    is_clean = fields.Boolean(default=False, readonly=True)
    is_defect = fields.Boolean(default=False, readonly=True)
    defect_remark = fields.Text('Defect Remark')

    # after service
    #after_service_id = fields.Many2one(
    #    'after.service', string='After Service',
    #    ondelete='cascade', index=True, copy=False, readonly=True)
    # treatment_type_id = fields.Many2one('treatment.book', related='after_service_id', store=True, string='Treatment Id', readonly=True)

    @api.depends('product_no', 'serial_no')
    def _compute_barcode(self):
        for line in self:
            line.barcode = line.product_no + line.serial_no

    @api.depends('product_no')
    def _compute_serial(self):
        for line in self:
            line.serial_no = "0000001"


class ProductionLineHistory(models.Model):

    _name = 'production.history'
    _description = 'Production history'
    _order = 'id'

    name = fields.Char('Production History', required=True, index=True)
    production_line = fields.Many2one('production.line', string='Production', required=True, ondelete='cascade', index=True)
    action_status = fields.Selection([
        ('new', 'New'),
        ('clean', 'Clean'),
        ('manufacturing', 'Manufacturing'),
        ('repair', 'Repair'),
        ('scrap', 'Scrap'),
        ], string='Action Status', compute='_set_action', store=True, readonly=True)

    def _set_action(self):
        for line in self:
            line.action_status = 'new'


