# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    maker_name = fields.Many2one(
        "maker.info", string="Maker Name")
    maker_product_no = fields.Char('Maker Product')
    product_no = fields.Char('Product No', required=True, index=True, copy=False, default='New')

    @api.model
    def create(self, vals):
        if vals.get('product_no', 'New') == 'New':
            vals['product_no'] = self.env['ir.sequence'].next_by_code('product.template')
        return super(ProductTemplate, self).create(vals)

class MakerInfo(models.Model):

    _name = 'maker.info'
    _description = 'Maker Info'
    _order = 'id'

    name = fields.Char('Maker', required=True, index=True)
