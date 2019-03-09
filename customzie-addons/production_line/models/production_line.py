# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import Warning


class ProductionLine(models.Model):

    _name = 'production.line'
    _description = 'Production Line'
    _order = 'id'

    name = fields.Char('Production Line', required=True, index=True)
    barcode = fields.Char('Barcode', compute='_compute_barcode', store = True)
    serial_no = fields.Char('Serial No', compute='_compute_serial', store = True)

    # Purchase
    purchase_order_line_id = fields.Many2one('purchase.order.line', string='Purchase Reference', required=True, ondelete='cascade', index=True, copy=False, readonly=True)
    purchase_order_id = fields.Many2one(related='purchase_order_line_id.order_id', store=True, string='POrder', readonly=True)
    purchase_partner_id = fields.Many2one(related='purchase_order_line_id.partner_id', store=True, string='Supplier', readonly=True)
    purchase_move_ids = fields.Many2one(related='purchase_order_line_id.move_ids', store=True, string='PMove', readonly=True)
    purchase_product_id = fields.Many2one(related='purchase_order_line_id.product_id', store=True, string='Purchase Product', readonly=True)
    Purchase_price_unit = fields.Many2one(related='purchase_order_line_id.price_unit', store=True, string='Purchase Price Unit', readonly=True)
    Purchase_taxes_id = fields.Many2one(related='purchase_order_line_id.taxes_id', store=True, string='Purchase Tax', readonly=True)
    purchase_product_no = fields.Many2one(related='p_product_id.product_no', store=True, string='Purchase Product No', readonly=True)

    # Sale
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Reference', ondelete='cascade', index=True, copy=False, readonly=True)
    sale_order_id = fields.Many2one(related='sale_order_line_id.order_id', store=True, string='SOrder', readonly=True)
    sale_partner_id = fields.Many2one(related='sale_order_line_id.partner_id', store=True, string='Customer', readonly=True)
    sale_move_ids = fields.Many2one(related='sale_order_line_id.move_ids', store=True, string='SMove', readonly=True)
    sale_product_id = fields.Many2one(related='sale_order_line_id.s_product_id', store=True, string='Order Product', readonly=True)
    sale_price_unit = fields.Many2one(related='sale_order_line_id.price_unit', store=True, string='Sale Price Unit', readonly=True)
    sale_taxes_id = fields.Many2one(related='sale_order_line_id.taxes_id', store=True, string='Sale Tax', readonly=True)
    s_product_no = fields.Many2one(related='s_product_id.product_no', store=True, string='Sale Product No', readonly=True)

    # repair
    repair_line_id = fields.Many2one('repair.line', string='Repair Line', ondelete='cascade', index=True, copy=False, readonly=True)
    repair_id = fields.Many2one(related='repair_line_id.repair_id', store=True, string='Repair id', readonly=True)

    @api.depends('product_no', 'serial_no')
    def _compute_barcode(self):
        self.barcode = self.product_no + self.serial_no

    @api.depends('product_no')
    def _compute_serial(self):
        self.serial_no = "0000001"


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
        self.action_status = 'new'


