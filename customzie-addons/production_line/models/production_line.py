# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import Warning


class ProductionLine(models.Model):

    _name = 'production.line'
    _description = 'Production Line'
    _order = 'id'

    name = fields.Char('Production Line')
    barcode = fields.Char('Barcode', compute='_compute_barcode', store=True)
    serial_no = fields.Char('Serial No', compute='_get_next_user_barcode', store=True)

    # Purchase
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line', string='Purchase Reference', ondelete='set null')
    purchase_order_id = fields.Many2one(string='Purchase Order', related="purchase_order_line_id.order_id", store=True)
    purchase_partner_id = fields.Many2one(string='Supplier', related="purchase_order_line_id.partner_id", store=True)

    inventory_name = fields.Char()

    # Sale
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Reference')
    sale_order_id = fields.Integer(string='Sale Order')
    sale_partner_id = fields.Integer(string='Customer')

    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_no = fields.Char(string='Product No', related="product_id.product_no", store=True)

#    stock_picking__id = fields.Many2one(
#        'stock.picking', string='Stock Picking',
#        readonly=True, store=True)

    is_clean = fields.Boolean(default=False, readonly=True)
    is_defect = fields.Boolean(default=False, readonly=True)
    defect_remark = fields.Text('Defect Remark')


    # after service
    after_service_id = fields.Many2one(
        'after.service', string='After Service',
        ondelete='set null')

    state = fields.Selection([
        ('draft', 'New'),
        ('inventory', 'Inventory'),
        ('cleaned', 'Cleaned'),
        ('picked', 'Picked'),
        ('done', 'Sold'),
        ('return', 'Return'),
        ('defect', 'Defect'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    @api.depends('product_no')
    @api.model
    def _get_next_user_barcode(self):
        for line in self:
            line.serial_no = self.search([('product_no', '=', line.product_no)], limit=1).serial_no
            if line.serial_no:
                line.serial_no
            else:
                line.serial_no = '0000001'

    @api.depends('product_no', 'serial_no')
    def _compute_barcode(self):
        for line in self:
            line.barcode = str(line.product_no) + str(line.serial_no)


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


