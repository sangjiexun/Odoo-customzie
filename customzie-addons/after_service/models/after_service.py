# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import Warning


class AfterService(models.Model):

    _name = 'after.service'
    _description = 'After Service'
    _order = 'id'

    name = fields.Char('After Service', required=True, index=True)
    # Sale
    production_line_id = fields.Many2one('production.line', string='Production Reference', ondelete='cascade', index=True, copy=False, readonly=True)
    sale_order_id = fields.Many2one('purchase.order.line', related='production_line_id.sale_order_id', store=True, string='Sale Order', readonly=True)
    sale_partner_id = fields.Many2one('res.partner', related='production_line_id.sale_partner_id', store=True, string='Customer', readonly=True)
    # sale_move_ids = fields.Many2one('stock.move', related='sale_order_line_id', store=True, string='Sale_Move', readonly=True)
    sale_product_id = fields.Many2one(related='production_line_id.sale_product_id', store=True, string='Order Product', readonly=True)
    sale_product_no = fields.Many2one('product.product', related='sale_product_id', store=True, string='Sale Product No', readonly=True)
    treatment_type_ids = fields.Many2many('treatment.book', 'treatment_book_rel', string='Treatment Type')
    treatment_remark = fields.Text('Treatment Remark')

class TreatmentBook(models.Model):

    _name = 'treatment.book'
    _description = 'Treatment Book'
    _order = 'id'

    name = fields.Char('Treatment Book', required=True, index=True)
    after_service_id = fields.Many2one('after.service', string='After Service Reference', required=True, ondelete='cascade', index=True, copy=False, readonly=True)
    treatment_type = fields.Char('Treatment Type', size=5, index=True)
    treatment_book = fields.Text('Treatment Book')

