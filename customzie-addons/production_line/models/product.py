# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_no = fields.Char('Product No', compute='_compute_product_no')

    @api.one
    def _compute_product_no(self):
        self.code = "123456"

