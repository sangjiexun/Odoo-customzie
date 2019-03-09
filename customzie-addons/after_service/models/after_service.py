# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import Warning


class AfterService(models.Model):
    _name = 'after.service'
    _description = 'After Service'
    _order = 'id'

    name = fields.Char('After Service', required=True, index=True)
    # Sale
    # production_line_id = fields.Many2one('production.line', string='Production Reference', ondelete='cascade', index=True, copy=False, readonly=True)
    order_id = fields.Char('Sale Order', index=True, readony=True)
    # sale_partner_id = fields.Many2one('res.partner', related='production_line_id.sale_partner_id', store=True, string='Customer', readonly=True)
    # sale_move_ids = fields.Many2one('stock.move', related='sale_order_line_id', store=True, string='Sale_Move', readonly=True)
    barcode = fields.Char('Barcode', index=True, readony=True)
    # sale_product_id = fields.Many2one(related='production_line_id.sale_product_id', store=True, string='Order Product', readonly=True)
    # sale_product_no = fields.Many2one('product.product', related='sale_product_id', store=True, string='Sale Product No', readonly=True)
    treatment_book_id = fields.Many2one(
        "treatment.book", string="Treatment Type", required=True)
    treatment_remark = fields.Text(string='Treatment Remark')


class TreatmentBook(models.Model):
    _name = 'treatment.book'
    _description = 'Treatment Book'
    _order = 'id'

    name = fields.Char('Treatment', required=True, index=True)
    treatment_book = fields.Text(string='Treatment Book')

