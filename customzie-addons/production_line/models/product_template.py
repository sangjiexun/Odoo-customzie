# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_no = fields.Char('Product No',
                             default=lambda self: self.env['ir.sequence'].next_by_code('product.template')
                             , required=True, readonly=True, help="Product No")


