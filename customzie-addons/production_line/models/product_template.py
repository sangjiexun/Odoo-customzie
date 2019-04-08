# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    marker_name = fields.Many2one(
        "marker.info", string="Marker Name")
    marker_product_no = fields.Char('Marker Product')
    product_no = fields.Char('Product No', required=True, index=True, copy=False, default='New')
    ceo_price = fields.Float(
        'Ceo Cost', company_dependent=True,
        groups="base_inherit.group_ceo",)

    @api.model
    def create(self, vals):
        if vals.get('product_no', 'New') == 'New':
            vals['product_no'] = self.env['ir.sequence'].next_by_code('product.template')
        return super().create(vals)






