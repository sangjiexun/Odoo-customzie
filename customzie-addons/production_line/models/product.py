# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_no = fields.Char('Product No', compute='_compute_product_no', store=True)

    @api.multi
    def _compute_product_no(self):
        for line in self:
            line.product_no = "123456"

