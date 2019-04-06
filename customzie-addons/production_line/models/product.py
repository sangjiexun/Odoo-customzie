# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    marker_name = fields.Many2one(
        "marker.info", string="Marker Name")
    marker_product_no = fields.Char('Marker Product')
    product_no = fields.Char('Product No', readonly=True, index=True, copy=False, default='New')

    @api.model
    def create(self, vals):
        if vals.get('product_no', 'New') == 'New':
            vals['product_no'] = self.env['ir.sequence'].next_by_code('product.product')
        return super().create(vals)




