# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import Warning


class ProductionLine(models.Model):

    _name = 'production.line'
    _description = 'Production Line'
    _order = 'id'

    barcode = fields.Char('Barcode', compute='_compute_barcode')
    serial_no = fields.Char('Serial No', compute='_compute_serial', readonly=True)
    purchase_order_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line', index=True)
    sale_order_line_id = fields.Many2one('sale.order.line', 'Sale Order Line', index=True, required=True)
    product_id = fields.Many2one('purchase.order.line', related='purchase.order.line.id.product_id', string='Product')
    product_no = fields.Many2one('purchase.order.line', related='purchase.order.line.id.product_no', string='Product No')








    name = fields.Char('Name')
    purchase_order_line  = fields.Char('Purchase Order Name',readonly=True)
    repair_order_name  = fields.Char('Repair Order Name',readonly=True) 
    sale_order_name  = fields.Char('Sale Order Name',readonly=True) 
    stock_status  = fields.Integer('Stock Status') #0：入荷 1：在庫 2：出庫 3：出荷 4：廃棄
    stock_status_child  = fields.Integer('Stock Status Child') #返品､製造､梱包､清掃､修理
    product_status  = fields.Selection([
        ('0', '正常'),
        ('1', '瑕疵品(可用)'),
        ('2', '瑕疵品(作废)'),
        ('3', '瑕疵品(その他)'),
    ], default='0', string='Product Status')
    remark  = fields.Text('Remark') #備考 メモ


    @api.one
    def _compute_barcode(self):
        self.barcode = self.product_no + self.serial_no

    @api.one
    def _compute_serial(self):
        self.serial_no = "0000001"
